from rag_modules import load_graph, extract_schema_info, generate_sparql, execute_sparql, generate_answer
import sys
import os

def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set.")
        sys.exit(1)

    print("=== Step 2 Verification ===")
    
    # 1. Load Graph
    print("[1] Loading Graph...")
    g = load_graph()
    if len(g) == 0:
        print("Error: Graph empty")
        sys.exit(1)
        
    # 2. Extract Schema
    print("[2] Extracting Schema...")
    schema_info = extract_schema_info(g)
    
    # 3. Define Question
    question = "301동 식당에서 파는 메뉴 이름과 가격을 알려줘."
    print(f"\n[3] Test Question: {question}")
    
    # 4. Generate SPARQL
    print("[4] Generating SPARQL...")
    sparql_query = generate_sparql(question, schema_info)
    print("--- Generated SPARQL ---")
    print(sparql_query)
    print("------------------------")
    
    if not sparql_query:
        print("Error: Failed to generate SPARQL")
        sys.exit(1)
        
    # 5. Execute SPARQL
    print("[5] Executing SPARQL...")
    results = execute_sparql(sparql_query, g)
    print(f"--- Raw Results ({len(results)} items) ---")
    if len(results) > 5:
        print(results[:5], "...")
    else:
        print(results)
    print("-----------------------")
    
    # 6. Generate Answer
    print("[6] Generating Answer...")
    answer = generate_answer(question, results)
    print("--- Final Answer ---")
    print(answer)
    print("--------------------")

if __name__ == "__main__":
    main()
