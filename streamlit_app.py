"""
Standalone Streamlit app for Agentic RAG Assistant.
Can run directly without needing separate FastAPI backend.
Perfect for Streamlit Community Cloud deployment.
"""
import streamlit as st
import json
import os
import tempfile
from pathlib import Path

# Import the agent directly
from app.agent import AgenticRAGAssistant
from app.retriever import ingest_file, ingest_directory

# Page configuration
st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit Cloud secrets are not automatically exposed as environment variables.
for secret_name in ("GROQ_API_KEY", "LLM_PROVIDER", "GROQ_MODEL"):
    if secret_name in st.secrets:
        os.environ[secret_name] = str(st.secrets[secret_name])

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
if "assistant" not in st.session_state:
    st.session_state.assistant = AgenticRAGAssistant()
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
    
    st.divider()
    
    # Document Ingestion
    st.header("📚 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Select PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload one or more PDF or TXT files"
    )
    
    if uploaded_files and st.button("📥 Upload & Index", use_container_width=True):
        total_chunks = 0
        try:
            with st.spinner("Processing documents..."):
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    chunks = ingest_file(tmp_path)
                    total_chunks += chunks
                    os.unlink(tmp_path)
                
                if total_chunks > 0:
                    st.success(f"✅ Indexed {total_chunks} chunks from {len(uploaded_files)} file(s)")
                    st.session_state.documents_ingested = True
                else:
                    st.warning("No content extracted from files")
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
    
    # Agent Configuration
    st.divider()
    st.header("⚙️ Agent Settings")
    
    max_steps = st.slider(
           "Maximum Tool Steps",
        min_value=1,
           max_value=5,
        value=3
    )
    
    if max_steps != st.session_state.assistant.max_steps:
        st.session_state.assistant = AgenticRAGAssistant(max_steps=max_steps)

# Main query interface
st.divider()
st.header("🎯 Query")

# Query input
query = st.text_area(
    "Ask a question or request a calculation:",
    placeholder="Example: What is 25 * 4 + 10?",
    height=100
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
                # Run the agent directly
                state = st.session_state.assistant.run(query)
                
                # Display results
                st.divider()
                
                # Answer section
                st.markdown("### 💡 Agent's Answer")
                st.markdown(f"""
<div class="success-box">
{state.final_answer}
</div>
                """, unsafe_allow_html=True)
                
                # Reasoning trace
                if state.history:
                    st.markdown("### 📋 Reasoning Trace")
                    for step in state.history:
                        st.markdown(f"""
<div class="trace-item">
{step}
</div>
                        """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Error processing query: {str(e)}")
            import traceback
            st.error(traceback.format_exc())


