# SNU Gwanak Campus Dining Ontology — Question Set (for Vibe Coding)

이 문서는 현재 보유한 데이터(메뉴 JSON + venue 메타데이터)만으로 답할 수 있는 “사람 중심 자연어 질문” 12개와, 각 질문이 기대하는 온톨로지 연결 구조(그래프 패턴)를 정리한 참고자료입니다.

* 목표: “온톨로지가 어떤 질문을 풀어주는가?”를 교육용으로 보여주기
* 원칙: 질문이 데이터의 특정 메뉴명/특정 문자열에 과도하게 종속되지 않도록 구성
* 구현 관점: 일부 질문은 원시 데이터에서 추출/정규화/태깅(derived data)이 필요하지만, 이는 외부 추가 데이터 없이 가능한 범위(룰 기반)로 제한

---

0. 데이터 스코프 & 기본 개념

---

입력 데이터(요약)

* MealService 단위: date, restaurant(venue_id), breakfast/lunch/dinner 각각의 description/items, time
* Venue 메타: venue_id, display_name, place_name, address, lat/lng, phone, building, floor(optional)
* (옵션) campus_center 좌표

추천 온톨로지 코어(최소)

* Venue

  * id, display_name, geo(lat,lng), building, floor, phone
* MealService

  * date, mealType(Breakfast/Lunch/Dinner), timeWindow, crowdWindow(optional), serviceStyle(optional), venue
* MenuItem (선택: 구조화가 필요할 때)

  * name, price, tags(takeout/spicy/noodles/etc), mealService

---

1. 오늘 점심 가능한 식당(또는 매장) 목록 보여줘

---

난이도: 쉬움
의미: 특정 날짜+끼니에 대해 제공되는 meal service 존재 여부로 필터링

Expected graph / pseudo
INPUT: date=today, mealType=Lunch
FIND Venue v
WHERE exists MealService ms:
ms.venue = v
ms.date = date
ms.mealType = mealType
AND (ms.timeWindow != null OR ms.description/items not empty)
RETURN v.display_name, ms.timeWindow

---

2. 지금(현재 시간) 열려있는 곳 어디야?

---

난이도: 쉬움(시간 파싱 필요)
의미: 자연어 “지금” → now ∈ timeWindow

Expected graph / pseudo
INPUT: now, date=today
FIND MealService ms
WHERE ms.date = date
AND ms.timeWindow contains now
RETURN ms.venue, ms.mealType, ms.descriptionSummary

---

3. 아침 먹을 수 있는 곳 중에 가장 저렴한 옵션은 뭐야?

---

난이도: 중간(가격 파싱/정규화)
의미: 메뉴 텍스트에서 price 추출 → 최소값 비교

Expected graph / pseudo
INPUT: date=today, mealType=Breakfast
FIND MenuItem mi
WHERE mi.mealService.date = date
AND mi.mealService.mealType = mealType
AND mi.price exists
ORDER BY mi.price ASC
RETURN top mi, mi.mealService.venue

---

4. 예산 6,000원 이하로 점심 가능한 곳 추천해줘

---

난이도: 중간(가격 파싱)
의미: 사용자 조건(budget)과 메뉴 가격을 연결

Expected graph / pseudo
INPUT: date=today, mealType=Lunch, budget<=6000
FIND (Venue v, MenuItem mi)
WHERE mi.mealService.date = date
AND mi.mealService.mealType = mealType
AND mi.price <= budget
RETURN groupBy v: list(mi)

---

5. 뷔페 있는 식당만 골라줘

---

난이도: 중간(서비스 유형 태깅)
의미: 텍스트(<뷔페>, 세미뷔페 등) → serviceStyle로 승격

Expected graph / pseudo
FIND MealService ms
WHERE ms.serviceStyle IN {Buffet, SemiBuffet}
RETURN ms.venue, ms.date, ms.mealType, ms.priceRange

---

6. 테이크아웃 되는 메뉴가 있는 곳 있어?

---

난이도: 중간(테이크아웃 태깅)
의미: 텍스트(TAKE-OUT 등) → consumptionMode 태깅

Expected graph / pseudo
FIND MenuItem mi
WHERE mi.consumptionMode = Takeout
RETURN mi.mealService.venue, mi.mealService.date, mi.mealService.mealType, mi.name, mi.price

---

7. 혼잡 시간 피해서 갈 수 있는 점심 후보 알려줘

---

난이도: 중간(혼잡시간 파싱)
의미: crowdWindow를 별도 속성으로 분리하고 회피 조건 적용

Expected graph / pseudo
INPUT: desiredArrivalTime t, date=today, mealType=Lunch
FIND MealService ms
WHERE ms.date = date
AND ms.mealType = mealType
AND ms.timeWindow contains t
AND NOT (ms.crowdWindow contains t)
RETURN ms.venue, ms.timeWindow, ms.crowdWindow

---

8. 가장 가까운 식당에서 점심 뭐 먹지?

---

난이도: 중간~상(거리 계산)
의미: venue geo + 기준점(userLocation or campus_center) → nearest 계산

Expected graph / pseudo
INPUT: origin (lat,lng), date=today, mealType=Lunch
FIND Venue v
WHERE exists MealService ms:
ms.venue=v AND ms.date=date AND ms.mealType=mealType
ORDER BY distance(origin, v.geo) ASC
RETURN topK: (v, ms.menuSummary, distance)

---

9. 오늘 매운 메뉴 위주로 추천해줘

---

난이도: 쉬움 (LLM 태깅 활용)
의미: `isSpicy` 속성을 통해 확실하게 매운 음식 필터링

Expected graph / pseudo
INPUT: preference=Spicy, date=today, mealType=Lunch
FIND MenuItem mi
WHERE mi.mealService.date=date
AND mi.mealService.mealType=mealType
AND mi.isSpicy = true
RETURN mi.name, mi.price, mi.cuisineType

---

10. 면 요리 위주로 가능한 옵션 모아줘

---

난이도: 쉬움 (LLM 태깅 활용)
의미: `carbType` 속성을 통해 면 요리(Noodle) 정확히 필터링

Expected graph / pseudo
INPUT: carbType=Noodle, date=today, mealType=Lunch
FIND MenuItem mi
WHERE mi.mealService.date=date
AND mi.mealService.mealType=mealType
AND mi.carbType = 'Noodle'
RETURN groupBy mi.mealService.venue

---

11. ‘자하연’ 근처에서 점심 + ‘정문 근처’에서 저녁, 동선 좋게 짜줘

---

난이도: 상(구역/건물 기반 제약 충족)
의미: 장소를 area/building로 묶고, 끼니 간 시간/이동 제약을 만족하는 조합 찾기

Expected graph / pseudo
INPUT:
lunchArea = "자하연", dinnerArea="정문 근처"
date=today
FIND lunchOption (v1, ms1), dinnerOption (v2, ms2)
WHERE ms1.date=date AND ms1.mealType=Lunch AND v1.area=lunchArea
AND ms2.date=date AND ms2.mealType=Dinner AND v2.area=dinnerArea
AND timeFeasible(ms1.timeWindow, ms2.timeWindow)
RETURN bestPairs by (distanceWithinArea, price, crowdAvoidanceOptional)

---

12. 이번 3일 점심을 ‘중복 없이’ 돌려먹고 싶어. 하루 7,000원 이하로 플랜 짜줘

---

난이도: 상(기간 + 제약 + 최적화)
의미: 날짜별 후보 세트 → 중복회피 제약(식당 or 카테고리) → 계획 생성

Expected graph / pseudo
INPUT: dateRange, mealType=Lunch, dailyBudget<=7000, noRepeat={venue OR menuCategory}
FOR each date d in dateRange:
candidateItems[d] = {mi | mi.mealService.date=d AND mi.price<=budget}

SOLVE assignment:
choose one mi per d
subject to:
notRepeated( mi.venue ) OR notRepeated( mi.category )
optimize:
minimize totalCost
maximize varietyScore(categories, cuisines)
minimize crowdPenalty(ms.crowdWindow)

RETURN plan by day: (venue, menuItem, timeWindow, price)

---

13. 채식(고기 없는) 메뉴 있어?

---

난이도: 쉬움 (LLM 태깅 활용)
의미: `containsMeat` 속성이 false인 메뉴 탐색

Expected graph / pseudo
INPUT: date=today
FIND MenuItem mi
WHERE mi.mealService.date=date
AND mi.containsMeat = false
RETURN mi.venue, mi.name, mi.cuisineType

---

14. 오늘 점심으로 일식 먹고 싶어

---

난이도: 쉬움 (LLM 태깅 활용)
의미: `cuisineType` 속성을 활용하여 특정 요리 스타일 필터링

Expected graph / pseudo
INPUT: cuisine='Japanese', date=today, mealType=Lunch
FIND MenuItem mi
WHERE mi.mealService.date=date
AND mi.mealService.mealType=mealType
AND mi.cuisineType = 'Japanese'
RETURN mi.venue, mi.name, mi.price

---

15. 매콤한 한식 추천해줘 (복합 질의)

---

난이도: 쉬움 (LLM 태깅 활용)
의미: `cuisineType`과 `isSpicy` 속성을 결합한 다중 조건 검색

Expected graph / pseudo
INPUT: cuisine='Korean', spicy=true, date=today
FIND MenuItem mi
WHERE mi.mealService.date=date
AND mi.cuisineType = 'Korean'
AND mi.isSpicy = true
RETURN mi.venue, mi.name, mi.price

---

## Derived Data 규칙(외부 데이터 없이 가능한 범위)

A) Price extraction

* 패턴 예: ": 6,000원", "6,500원", "1,000원"
* 결과: MenuItem.price (int)

B) TimeWindow / CrowdWindow parsing

* 패턴 예: "11:00~14:00", "11:30~12:30", "17:00"
* 결과: MealService.timeWindow, MealService.crowdWindow

C) ServiceStyle tagging

* 키워드 예: "<뷔페>", "세미뷔페"
* 결과: MealService.serviceStyle

D) ConsumptionMode tagging

* 키워드 예: "TAKE-OUT", "Take-Out", "포장"
* 결과: MenuItem.consumptionMode = Takeout

E) LLM-based Classification (Gemini 2.0 Flash)

* 입력: 메뉴명 (예: "등심돈까스", "순두부찌개")
* 출력:
    * `cuisineType`: Korean, Western, Chinese, Japanese, Other
    * `containsMeat`: Boolean (육류 주재료 여부)
    * `carbType`: Rice, Noodle, Bread, None
    * `isSpicy`: Boolean (매운맛 여부)
* 장점: 단순 키워드 매칭보다 문맥/상식 기반의 정확한 분류 가능

---
