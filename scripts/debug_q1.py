import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_modules import load_graph, extract_schema_info, generate_sparql

def debug_q1():
    print("Loading Graph...")
    g = load_graph()
    schema_info = extract_schema_info(g)
    
    question = "지금 아침 식사 되는 식당 어디야?"
    print(f"\nQuestion: {question}")
    
    sparql = generate_sparql(question, schema_info)
    print("\n--- Generated SPARQL ---")
    print(sparql)
    print("------------------------")

if __name__ == "__main__":
    debug_q1()
