import streamlit as st
import time
import sys
import os

# Add project root to sys.path to ensure imports work
# Current file: app/main.py -> Project Root: ..
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import time
from app.services.rag_pipeline import load_graph, extract_schema_info, generate_sparql, execute_sparql, generate_answer, generate_explanation

# Page Config
st.set_page_config(page_title="SNU Dining Graph RAG", layout="wide")

st.title("🎓 SNU Dining Graph RAG")
st.markdown("서울대 학식 온톨로지를 기반으로 질문에 답변합니다.")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    with st.spinner("Loading Knowledge Graph..."):
        st.session_state.graph = load_graph()
        st.session_state.schema = extract_schema_info(st.session_state.graph)
    st.success("Graph Loaded!")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there are details, show them
        if "details" in message:
            details = message["details"]
            
            with st.expander("🔍 [1단계] 논리적 근거 (SPARQL Query)"):
                st.code(details["sparql"], language="sparql")
                
            with st.expander("🧠 [2단계] 쿼리 해석"):
                st.write(details["explanation"])
                
            with st.expander("📊 [3단계] 팩트 체크 (Raw Data)"):
                st.json(details["raw_data"])

# Chat Input
if prompt := st.chat_input("질문을 입력하세요 (예: 301동 식당 메뉴 알려줘)"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 1. Generate SPARQL
            with st.status("Thinking (generating SPARQL)...", expanded=False) as status:
                sparql_query = generate_sparql(prompt, st.session_state.schema)
                status.write("SPARQL Generated.")
                status.update(label="Thinking (executing Query)...", state="running")
                
                # 2. Execute SPARQL
                raw_data = execute_sparql(sparql_query, st.session_state.graph)
                status.write(f"Data Retrieved: {len(raw_data)} items.")
                status.update(label="Thinking (generating Answer)...", state="running")

                # 3. Generate Answer
                answer_text = generate_answer(prompt, raw_data)
                
                # 4. Generate Explanation
                explanation_text = generate_explanation(prompt, sparql_query)
                
                status.update(label="Complete!", state="complete", expanded=False)

            # Display Answer
            message_placeholder.markdown(answer_text)

            # Display Details
            with st.expander("🔍 [1단계] 논리적 근거 (SPARQL Query)"):
                st.code(sparql_query, language="sparql")
            
            with st.expander("🧠 [2단계] 쿼리 해석"):
                st.write(explanation_text)

            with st.expander("📊 [3단계] 팩트 체크 (Raw Data)"):
                st.json(raw_data)

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "details": {
                    "sparql": sparql_query,
                    "raw_data": raw_data,
                    "explanation": explanation_text
                }
            })
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

