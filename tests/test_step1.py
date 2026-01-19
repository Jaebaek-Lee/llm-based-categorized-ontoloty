from rag_modules import load_graph, extract_schema_info
import sys

def main():
    print("=== Step 1 Verification ===")
    print("1. Loading Graph...")
    g = load_graph()
    
    if len(g) == 0:
        print("ERROR: Graph is empty.")
        sys.exit(1)
        
    print(f"SUCCESS: Graph loaded with {len(g)} triples.")
    
    print("\n2. Extracting Schema Info...")
    info = extract_schema_info(g)
    print("--- SCHEMA INFO START ---")
    print(info)
    print("--- SCHEMA INFO END ---")
    
    if "Classes" in info and "Properties" in info:
        print("\nSUCCESS: Schema info generated.")
    else:
        print("\nWARNING: Schema info might be incomplete.")

if __name__ == "__main__":
    main()
