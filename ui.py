"""
Interactive Streamlit UI for Agentic RAG Assistant.
Perfect for interviews and demos.
"""
import streamlit as st
import requests
import json
import time
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5em;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 4px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
    }
    .trace-item {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "documents_ingested" not in st.session_state:
    st.session_state.documents_ingested = False

# Main header
st.markdown('<div class="main-header">🤖 Agentic RAG Assistant</div>', unsafe_allow_html=True)

st.markdown("""
An intelligent agent that decides whether to:
- Answer directly from its knowledge
- Calculate mathematical expressions
- Retrieve relevant documents from your knowledge base
""")

# Sidebar for configuration and document ingestion
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Configuration
    api_url = st.text_input(
        "API URL",
        value=st.session_state.api_url,
        help="Base URL of the FastAPI backend"
    )
    st.session_state.api_url = api_url
    
    # Test connection
    if st.button("🔌 Test Connection", use_container_width=True):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connected to API!")
                st.session_state.documents_ingested = True
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    st.divider()
    
    # Document Ingestion
    st.header("📚 Knowledge Base Setup")
    st.write("Upload documents to the knowledge base:")
    
    doc_path = st.text_input(
        "Document Directory Path",
        value="data/sample_docs",
        help="Path to directory containing documents to ingest (relative to app root)"
    )
    
    if st.button("📥 Ingest Documents", use_container_width=True):
        try:
            with st.spinner("Ingesting documents..."):
                response = requests.post(
                    f"{api_url}/ingest",
                    json={"directory": doc_path},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    chunks = data.get("chunks_ingested", 0)
                    st.success(f"✅ Ingested {chunks} document chunks!")
                    st.session_state.documents_ingested = True
                else:
                    st.error(f"❌ Ingestion failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Main query interface
st.divider()
st.header("🎯 Ask the Agent")

# Query input
query = st.text_area(
    "Enter your question or calculation:",
    placeholder="Examples:\n- What is the return policy?\n- Calculate 25 * 4 + 10\n- Tell me about company policies",
    height=100,
    help="The agent will decide the best way to answer your question"
)

# Query execution
col1, col2 = st.columns([3, 1])
with col1:
    submit_button = st.button("🚀 Submit Query", use_container_width=True)
with col2:
    clear_button = st.button("🔄 Clear", use_container_width=True)

if clear_button:
    st.rerun()

# Process query
if submit_button:
    if not query.strip():
        st.warning("⚠️ Please enter a query")
    else:
        try:
            with st.spinner("Agent is thinking..."):
                response = requests.post(
                    f"{api_url}/query",
                    json={"query": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display answer
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Answer")
                    st.markdown(result.get("answer", "No answer generated"))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display reasoning trace
                    st.divider()
                    st.markdown("### 🔍 Agent Reasoning Trace")
                    
                    trace = result.get("trace", [])
                    if trace:
                        for i, step in enumerate(trace, 1):
                            with st.expander(f"Step {i}: {step.get('action', 'Action')}", expanded=(i==1)):
                                st.markdown('<div class="trace-item">', unsafe_allow_html=True)
                                
                                if isinstance(step, dict):
                                    for key, value in step.items():
                                        if key != "action":
                                            st.write(f"**{key}:** {value}")
                                else:
                                    st.write(step)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No trace information available")
                else:
                    st.error(f"❌ Query failed: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the backend is running (uvicorn app.main:app --reload)")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Information section
st.divider()
with st.expander("ℹ️ How the Agent Works"):
    st.markdown("""
    #### Architecture
    
    1. **Query Processing**: Your question is sent to the agent
    2. **Agent Decision**: The LLM decides the best approach:
       - **Direct Answer**: Use built-in knowledge for straightforward questions
       - **Calculator**: Evaluate mathematical expressions safely
       - **Retriever**: Search the knowledge base for relevant documents
    3. **Iterative Reasoning**: The agent can combine multiple tools in a loop
    4. **Final Answer**: Returns the result with complete reasoning trace
    
    #### Key Features
    - **Safe Calculation**: Uses AST-based evaluation (no `eval()`)
    - **Local Vector Search**: Chroma + sentence-transformers (no API keys needed)
    - **Production-Ready**: Can swap in real LLMs via `LLM_PROVIDER` env var
    
    #### Try These Queries
    - "What is 125 * 8?"
    - "What is the return policy?"
    - "Calculate the square root of 144"
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>Built for interview demonstrations | Backend API at: """ + st.session_state.api_url + """</p>
</div>
""", unsafe_allow_html=True)
