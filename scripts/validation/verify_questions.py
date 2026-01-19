import os
from rdflib import Graph, Namespace

SNU = Namespace("http://snu.ac.kr/dining/")

def run():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inferred_path = os.path.join(base_dir, 'abox_inferred.ttl')
    
    if not os.path.exists(inferred_path):
        print("Inferred graph not found.")
        return

    g = Graph()
    g.parse(inferred_path, format='turtle')
    print(f"Loaded {len(g)} triples.")

    queries = {
        "Q9 (Spicy Options)": """
            PREFIX snu: <http://snu.ac.kr/dining/>
            SELECT ?name ?price ?cuisine
            WHERE {
                ?item a snu:MenuItem ;
                      snu:menuName ?name ;
                      snu:isSpicy true .
                OPTIONAL { ?item snu:price ?price }
                OPTIONAL { ?item snu:cuisineType ?cuisine }
            } LIMIT 5
        """,
        "Q10 (Noodle Dishes)": """
            PREFIX snu: <http://snu.ac.kr/dining/>
            SELECT ?name ?venueName
            WHERE {
                ?item a snu:MenuItem ;
                      snu:menuName ?name ;
                      snu:carbType "Noodle"^^xsd:string ;
                      snu:partOfService ?ms .
                ?ms snu:providedAt ?v .
                ?v snu:name ?venueName .
            } LIMIT 5
        """,
        "Q13 (Vegetarian Options - No Meat)": """
            PREFIX snu: <http://snu.ac.kr/dining/>
            SELECT ?name ?cuisine
            WHERE {
                ?item a snu:MenuItem ;
                      snu:menuName ?name ;
                      snu:containsMeat false .
                OPTIONAL { ?item snu:cuisineType ?cuisine }
            } LIMIT 5
        """,
        "Q14 (Japanese Food)": """
            PREFIX snu: <http://snu.ac.kr/dining/>
            SELECT ?name ?price
            WHERE {
                ?item a snu:MenuItem ;
                      snu:menuName ?name ;
                      snu:cuisineType "Japanese"^^xsd:string .
                OPTIONAL { ?item snu:price ?price }
            } LIMIT 5
        """,
        "Q15 (Spicy Korean Food)": """
            PREFIX snu: <http://snu.ac.kr/dining/>
            SELECT ?name ?price
            WHERE {
                ?item a snu:MenuItem ;
                      snu:menuName ?name ;
                      snu:cuisineType "Korean"^^xsd:string ;
                      snu:isSpicy true .
                OPTIONAL { ?item snu:price ?price }
            } LIMIT 5
        """
    }

    for title, q in queries.items():
        print(f"\n--- Running {title} ---")
        try:
            results = g.query(q)
            found = False
            for row in results:
                # Format output nicely
                res_str = []
                for val in row:
                    res_str.append(str(val).replace('http://snu.ac.kr/dining/', ''))
                print(" | ".join(res_str))
                found = True
            if not found:
                print("No results found.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
