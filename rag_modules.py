import os
import re
import json
import google.generativeai as genai
import rdflib
from rdflib import RDF, RDFS, OWL

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load .env manually to avoid external dependencies like python-dotenv
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash" # Updated to available 2.0 model

if API_KEY:
    genai.configure(api_key=API_KEY)


def load_graph():
    """
    Loads TBox and ABox into an rdflib Graph.
    Expected paths:
      - ontology/tbox.ttl
      - abox_inferred.ttl
    """
    g = rdflib.Graph()
    
    # Define absolute paths based on the project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tbox_path = os.path.join(base_dir, "ontology/tbox.ttl")
    abox_path = os.path.join(base_dir, "abox_inferred.ttl")

    try:
        g.parse(tbox_path, format="turtle")
        print(f"Loaded TBox from {tbox_path}: {len(g)} triples so far")
    except Exception as e:
        print(f"Error loading TBox: {e}")

    try:
        g.parse(abox_path, format="turtle")
        print(f"Loaded ABox from {abox_path}. Total triples: {len(g)}")
    except Exception as e:
        print(f"Error loading ABox: {e}")
    
    return g

def extract_schema_info(graph):
    """
    Extracts classes, properties, and sample triples to describe the graph structure.
    Returns a string summary.
    """
    # Classes
    classes = set()
    for s, p, o in graph.triples((None, RDF.type, OWL.Class)):
        classes.add(s.n3(graph.namespace_manager))
    for s, p, o in graph.triples((None, RDF.type, RDFS.Class)):
        classes.add(s.n3(graph.namespace_manager))
        
    # Properties
    properties = set()
    for s, p, o in graph.triples((None, RDF.type, OWL.ObjectProperty)):
        properties.add(s.n3(graph.namespace_manager))
    for s, p, o in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
        properties.add(s.n3(graph.namespace_manager))

    # Sample Relations (avoiding type definitions to see actual data links)
    relations = []
    # Simple query to get some interesting connections
    q = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
        FILTER (?p != rdf:type)
        FILTER (!isLiteral(?o)) 
    }
    LIMIT 5
    """
    try:
        for row in graph.query(q):
            s_str = row.s.n3(graph.namespace_manager)
            p_str = row.p.n3(graph.namespace_manager)
            o_str = row.o.n3(graph.namespace_manager)
            relations.append(f"{s_str} {p_str} {o_str}")
    except Exception as e:
        print(f"Error sampling relations: {e}")

    schema_info = f"""
## Classes
{', '.join(sorted(classes)) if classes else "No classes found"}

## Properties
{', '.join(sorted(properties)) if properties else "No properties found"}

## Sample Relations
{chr(10).join(relations) if relations else "No relations found"}
"""
    return schema_info

def generate_sparql(question, schema_info):
    """
    Generates a SPARQL query based on the question and schema info using Gemini.
    """
    if not API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")

    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    You are an expert in SPARQL and Ontologies.
    Convert the following natural language question into a SPARQL 1.1 query.
    Use the provided Schema Information to understand the classes and properties.
    
    # Schema Information
    {schema_info}
    
    # Prefixes
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX : <http://snu.ac.kr/dining/>
    
    # Question
    {question}
    
    # Requirements
    - Return ONLY the SPARQL query code.
    - Do not include markdown code blocks (```sparql ... ```).
    - Use only the classes and properties defined in the schema if possible.
    - For names (venues, menus), ALWAYS query the `:name` or `:menuName` property and filter it. Do NOT filter the Subject URI.
    - Example: `SELECT ?v WHERE {{ ?v a :Venue ; :name ?n . FILTER(CONTAINS(?n, "301")) }}`
    - CRITICAL: The path from Venue to Menu is: `?venue :offers ?service . ?service :hasMenu ?menuItem`. Use this path.
    - If the user asks about a general concept (e.g., "Engineering Zone"), rely on 'partOf' relationships or specific building names if you can infer them.
    """
    
    try:
        response = model.generate_content(prompt)
        query = response.text.strip()
        # Clean up markdown if present
        if query.startswith("```"):
            query = re.sub(r"^```\w*\n", "", query)
            query = re.sub(r"\n```$", "", query)
        return query.strip()
    except Exception as e:
        print(f"Error generating SPARQL: {e}")
        return ""

def execute_sparql(query, graph):
    """
    Executes the SPARQL query on the graph.
    Returns a list of dictionaries (keys as variables).
    """
    try:
        results = graph.query(query)
        data = []
        for row in results:
            item = {}
            if hasattr(results, 'vars'): # Select query
                for var in results.vars:
                    val = row[var]
                    if val is not None:
                         # Convert simple literals to string, URIs to string
                        item[str(var)] = str(val)
                data.append(item)
            else: # Construct/Ask? Handling Select primarily
                 data.append(row.asdict()) 
        return data
    except Exception as e:
        print(f"Error executing SPARQL: {e}")
        return []

def generate_answer(question, raw_data):
    """
    Generates a natural language answer based on the raw data.
    """
    if not API_KEY:
         raise ValueError("GOOGLE_API_KEY is not set.")
         
    model = genai.GenerativeModel(MODEL_NAME)
    
    data_str = json.dumps(raw_data, ensure_ascii=False, indent=2)
    
    prompt = f"""
    You are a helpful assistant for Seoul National University cafeteria info.
    Answer the user's question based on the provided Data.
    
    # Question
    {question}
    
    # Data (SPARQL Results)
    {data_str}
    
    # Instructions
    - Provide a polite, concise, and accurate answer.
    - If data is empty, define that no satisfying results were found.
    - Mention specific names and prices if available.
    - Answer in Korean.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."

def generate_explanation(question, query):
    """
    Explains the SPARQL query in plain Korean.
    """
    if not API_KEY:
         raise ValueError("GOOGLE_API_KEY is not set.")
         
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    You are an expert in Semantic Web and SPARQL.
    Explain WHY this SPARQL query was constructed to answer the user's question.
    
    # User Question
    {question}
    
    # SPARQL Query
    {query}
    
    # Instructions
    - Explain the logic step-by-step.
    - Mention which properties were used (e.g., 'filtered by name', 'traversed partOfService').
    - Speak in Korean.
    - Be concise (2-3 sentences).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "쿼리 해석을 생성할 수 없습니다."

