"""
Standalone Streamlit app for Agentic RAG Assistant.
Can run directly without needing separate FastAPI backend.
Perfect for Streamlit Community Cloud deployment.
"""
import streamlit as st
import json
import os
from pathlib import Path

# Import the agent directly
from app.agent import AgenticRAGAssistant
from app.retriever import ingest_directory

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
    
    st.info("✅ Direct agent mode - No backend server needed!")
    
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
        if os.path.isdir(doc_path):
            try:
                with st.spinner("Ingesting documents..."):
                    chunks = ingest_directory(doc_path)
                    if chunks > 0:
                        st.success(f"✅ Ingested {chunks} document chunks!")
                        st.session_state.documents_ingested = True
                    else:
                        st.info(f"ℹ️ No documents found in {doc_path}. Add .txt or .pdf files to enable retrieval.")
            except Exception as e:
                st.error(f"❌ Error ingesting documents: {str(e)}")
        else:
            st.error(f"❌ Directory not found: {doc_path}")
    
    # Agent Configuration
    st.divider()
    st.header("🧠 Agent Settings")
    
    max_steps = st.slider(
        "Max Agent Steps",
        min_value=1,
        max_value=10,
        value=3,
        help="Maximum number of reasoning steps the agent can take"
    )
    
    if max_steps != st.session_state.assistant.max_steps:
        st.session_state.assistant = AgenticRAGAssistant(max_steps=max_steps)

# Main query interface
st.divider()
st.header("🎯 Ask the Agent")

st.markdown("""
**Examples you can try:**
- "What is 25 * 4 + 10?" *(uses calculator)*
- "What is the return policy?" *(uses retrieval if docs ingested)*
- "Tell me about Python" *(direct answer)*
""")

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

# Footer
st.divider()
st.markdown("""
---
**Agentic RAG Assistant** | An interview-ready demo of agent-based reasoning with tool-calling
- 🏗️ Built with FastAPI, Streamlit, Chroma
- 🧮 Features: Direct answer, calculator, document retrieval
- 📊 Fully deterministic with MockLLM (no API keys needed)
""")
