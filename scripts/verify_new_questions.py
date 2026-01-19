import sys
import os

# Add parent directory to path to import rag_modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_modules import load_graph, extract_schema_info, generate_sparql, execute_sparql, generate_answer

def run_verification():
    print("Loading Graph...")
    g = load_graph()
    schema_info = extract_schema_info(g)
    print("Graph Loaded.")

    questions = [
        "지금 아침 식사 되는 식당 어디야?",
        "5,000원 이하로 점심 먹을 수 있는 곳 있어?",
        "오늘 면 요리(Noodle) 먹고 싶은데 어디로 가면 돼?",
        "301동(공대) 근처에 일식 파는 식당 찾아줘.",
        "바쁜데 빨리 받아서 갈 수 있는(테이크아웃) 점심 메뉴 추천해줘.",
        "오늘 매콤한 한식 땡기는데, 학생회관 근처에 그런 메뉴 있어?",
        "오늘 고기 없는 식단(채식) 있어?",
        "오늘 저녁 6시 30분 이후에도 밥 먹을 수 있는 곳 있어?",
        "나 매운 거 못 먹는데, 안 매운 걸로 추천해줘.",
        "오늘 나온 메뉴 중에 제일 싼 게 뭐야?"
    ]

    print(f"\nTesting {len(questions)} Competency Questions...\n")

    for i, q in enumerate(questions, 1):
        print(f"=== Q{i}: {q} ===")
        
        # 1. Generate SPARQL
        print("  [1] Generating SPARQL...")
        sparql = generate_sparql(q, schema_info)
        print(f"  -> QUERY: {sparql.replace(chr(10), ' ')[:100]}...") # Print first 100 chars
        
        # 2. Execute
        print("  [2] Executing...")
        results = execute_sparql(sparql, g)
        print(f"  -> FOUND: {len(results)} items")
        
        # 3. Answer
        print("  [3] Answer:")
        if results:
            ans = generate_answer(q, results[:5]) # Limit context to 5 items to save tokens/screen
            print(f"  -> {ans.replace(chr(10), ' ')}")
        else:
            print("  -> No results found (Answer generation skipped)")
        
        print("\n" + "-"*30 + "\n")

if __name__ == "__main__":
    run_verification()
