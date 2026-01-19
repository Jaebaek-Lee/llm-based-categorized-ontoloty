# SNU Dining Knowledge Graph RAG Service

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system grounded in a semantic Knowledge Graph for Seoul National University (SNU) campus dining services. Unlike conventional vector-based RAG approaches, this system translates natural language queries into precise SPARQL queries executed against an RDF/OWL ontology. This architecture ensures high-fidelity factual retrieval and supports complex logical reasoning, such as filtering by dietary preferences, verified operating hours, and location proximity.

## Architecture

The system utilizes a pure Python architecture without dependency on external graph databases like Neo4j:

*   **Knowledge Graph**: The backend is powered by `rdflib`, verifying data against a custom Ontology (TBox) and Data instances (ABox).
*   **Semantic RAG Pipeline**: Utilizing `gemini-3-pro-preview`, the system dynamically extracts schema information (classes, properties, and categorical values) to guide the Linked Data query generation.
*   **User Interface**: A Streamlit application provides an interactive chat interface that visualizes the reasoning process, including the generated SPARQL query, raw data results, and the final natural language synthesis.

## Project Structure

The project follows a modular structure to separate application logic, data assets, and utility scripts:

```
newtology/
├── app/                        # Application Source Code
│   ├── main.py                 # Entry point for the Streamlit web service
│   └── services/               # Core business logic modules
│       └── rag_pipeline.py     # RAG pipeline: Schema Extraction -> SPARQL Generation -> Execution
├── data/                       # Data Store
│   ├── raw/                    # Source JSON datasets (Menus, Locations)
│   ├── ontology/               # Semantic Schema (TBox in Turtle format)
│   └── knowledge_graph/        # Instantiated Graph Data (ABox in Turtle format)
├── scripts/                    # Utilities and ETL
│   ├── etl/                    # Data transformation and graph generation scripts
│   ├── validation/             # System integrity and competency question verification
│   └── debug/                  # Granular debugging tools for specific query failures
├── docs/                       # Documentation and Competency Questions
└── config.py                   # Centralized Configuration Management
```

## Prerequisites

*   Python 3.10 or higher
*   Google Gemini API Key (set as `GOOGLE_API_KEY`)

## Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/Jaebaek-Lee/llm-based-categorized-ontoloty.git
    cd newtology
    ```

2.  **Set Up Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**

    Create a `.env` file in the project root directory:

    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

## Usage

### Running the Web Service

To start the interactive web interface:

```bash
streamlit run app/main.py
```

The application will be accessible at `http://localhost:8501`.

### Verifying System Competency

To validate the system against a suite of competency questions (e.g., dietary restrictions, pricing, location):

```bash
python3 scripts/validation/verify_new_questions.py
```

## Technical Highlights

*   **Dynamic Schema Extraction**: The prompt logic automatically adapts to ontology changes by querying valid values (e.g., `mealType`, `cuisineType`) from the graph before generating queries.
*   **Robust Type Handling**: Implements casting logic (`FILTER(STR(?var) = "value")`) to handle RDF Literal type strictness gracefully.
*   **Token Optimization**: Strategies such as value limiting are employed to manage context window usage effectively while retaining high cardinality support for specific properties via keyword search.

## Overview

This project is developed as **supplementary material for the Seoul National University Ontology-based Knowledge Graph Course Final Exam Hackathon**.
