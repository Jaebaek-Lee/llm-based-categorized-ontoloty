import sys
import os
import rdflib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_modules import load_graph

def debug_breakfast():
    print("Loading Graph...")
    g = load_graph()
    
    # Query 1: Explicit xsd:string
    print("\n--- Test 1: Explicit xsd:string ---")
    query1 = """
    PREFIX : <http://snu.ac.kr/dining/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?venueName WHERE {
      ?service a :MealService ;
               :mealType "breakfast"^^xsd:string ;
               :providedAt ?venue .
      ?venue a :Venue ;
             :name ?venueName .
    }
    """
    results1 = g.query(query1)
    print(f"Results (Typed): {len(results1)}")

    # Query 2: Filter STR
    print("\n--- Test 2: STR() Filter ---")
    query2 = """
    PREFIX : <http://snu.ac.kr/dining/>
    SELECT ?venueName WHERE {
      ?service a :MealService ;
               :mealType ?mt ;
               :providedAt ?venue .
      ?venue a :Venue ;
             :name ?venueName .
      FILTER (STR(?mt) = "breakfast")
    }
    """
    results2 = g.query(query2)
    print(f"Results (STR check): {len(results2)}")

if __name__ == "__main__":
    debug_breakfast()
