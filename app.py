"""
NotebookLM-Style Study Tool
Main Streamlit Application
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
from modes.qa_mode import QAMode
from modes.dialogue_mode import DialogueMode
from modes.video_summary_mode import VideoSummaryMode


# Page configuration
st.set_page_config(
    page_title="NotebookLM Study Tool",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .mode-header {
        font-size: 1.8rem;
        color: #ff7f0e;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .dialogue-student {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    .dialogue-teacher {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_system():
    """Load and cache the RAG system."""
    try:
        # Initialize embedding generator
        generator = EmbeddingGenerator()
        
        # Load vector store
        store = VectorStore()
        if not store.exists():
            st.error("❌ Vector store not found. Please run build_vector_store.py first.")
            st.stop()
        
        store.load(generator)
        
        # Initialize retriever
        retriever = RAGRetriever(store)
        
        # Initialize modes
        qa_mode = QAMode(retriever)
        dialogue_mode = DialogueMode(retriever)
        video_mode = VideoSummaryMode(retriever)
        
        return qa_mode, dialogue_mode, video_mode
    
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        st.stop()


def main():
    """Main application."""
    
    # Header
    st.markdown('<p class="main-header">📚 NotebookLM Study Tool</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY not found in environment variables. Please set it in the .env file.")
        st.stop()
    
    # Load system
    with st.spinner("Loading study tool..."):
        qa_mode, dialogue_mode, video_mode = load_system()
    
    # Sidebar - Mode Selection
    st.sidebar.title("🎯 Select Mode")
    mode = st.sidebar.radio(
        "Choose study mode:",
        ["💬 Q&A Mode", "🎭 Dialogue Tutor", "🎥 Video Summary"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **About This Tool:**
    
    An AI-powered study assistant for economics education, featuring:
    - 💬 **Q&A**: Ask questions about the chapter
    - 🎭 **Dialogue**: Student-Teacher conversations
    - 🎥 **Summary**: Video-style chapter overviews
    
    All responses are grounded in the provided PDF and video transcripts.
    """)
    
    # Main content area
    if mode == "💬 Q&A Mode":
        render_qa_mode(qa_mode)
    
    elif mode == "🎭 Dialogue Tutor":
        render_dialogue_mode(dialogue_mode)
    
    elif mode == "🎥 Video Summary":
        render_video_mode(video_mode)


def render_qa_mode(qa_mode: QAMode):
    """Render Q&A mode interface."""
    
    st.markdown('<p class="mode-header">💬 Question & Answer Mode</p>', unsafe_allow_html=True)
    st.write("Ask questions about the economics chapter. Answers are grounded in the provided materials.")
    
    # Suggested questions
    with st.expander("💡 Suggested Questions"):
        suggested = qa_mode.get_suggested_questions()
        cols = st.columns(2)
        for i, question in enumerate(suggested):
            with cols[i % 2]:
                if st.button(question, key=f"suggest_{i}"):
                    st.session_state.qa_question = question
    
    # Question input
    question = st.text_input(
        "Your Question:",
        value=st.session_state.get('qa_question', ''),
        placeholder="e.g., What is supply and demand?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary")
    with col2:
        num_sources = st.slider("Number of sources:", 3, 10, 5, key="qa_sources")
    
    if ask_button and question:
        with st.spinner("Thinking..."):
            result = qa_mode.ask_question(question, k=num_sources)
        
        # Display answer
        st.markdown("### 📝 Answer")
        st.write(result['answer'])
        
        # Display sources
        st.markdown("### 📚 Sources Used")
        for source in result['sources']:
            with st.expander(f"Source {source['number']} - {source['type'].upper()} (Score: {source['similarity_score']:.3f})"):
                st.markdown(f"**Source:** `{source['source_name']}`")
                st.markdown(f"**Preview:**\n\n{source['text_preview']}")


def render_dialogue_mode(dialogue_mode: DialogueMode):
    """Render dialogue mode interface."""
    
    st.markdown('<p class="mode-header">🎭 Dialogue Tutor Mode</p>', unsafe_allow_html=True)
    st.write("Experience a two-person conversation between a Student and Teacher about economics concepts.")
    
    # Topic selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Suggested topics
        with st.expander("💡 Suggested Topics"):
            suggested = dialogue_mode.get_suggested_topics()
            cols = st.columns(2)
            for i, topic in enumerate(suggested):
                with cols[i % 2]:
                    if st.button(topic, key=f"topic_{i}"):
                        st.session_state.dialogue_topic = topic
        
        topic = st.text_input(
            "Topic for Dialogue:",
            value=st.session_state.get('dialogue_topic', ''),
            placeholder="e.g., Supply and Demand",
            key="topic_input"
        )
    
    with col2:
        num_exchanges = st.number_input(
            "Number of Exchanges:",
            min_value=3,
            max_value=10,
            value=5,
            key="dialogue_exchanges"
        )
    
    if st.button("🎭 Generate Dialogue", type="primary"):
        if topic:
            with st.spinner("Creating dialogue..."):
                result = dialogue_mode.generate_dialogue(topic, num_exchanges=num_exchanges)
            
            st.markdown(f"### 📖 Dialogue: {result['topic']}")
            st.markdown("---")
            
            # Display exchanges
            for i, exchange in enumerate(result['exchanges'], 1):
                st.markdown(f'<div class="dialogue-student"><b>🎓 Student:</b> {exchange["student"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dialogue-teacher"><b>👨‍🏫 Teacher:</b> {exchange["teacher"]}</div>', unsafe_allow_html=True)
                if i < len(result['exchanges']):
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # Show sources
            with st.expander(f"📚 View Sources ({len(result['sources'])} used)"):
                for i, source in enumerate(result['sources'], 1):
                    st.markdown(f"**{i}. {source['type'].upper()}** - {source['source']}")
                    st.caption(source['text'][:200] + "...")
                    st.markdown("---")
        else:
            st.warning("Please enter a topic for the dialogue.")


def render_video_mode(video_mode: VideoSummaryMode):
    """Render video summary mode interface."""
    
    st.markdown('<p class="mode-header">🎥 Video Summary Mode</p>', unsafe_allow_html=True)
    st.write("Generate structured, video-style summaries of chapter content with key concepts, definitions, and exam tips.")
    
    # Section selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Suggested sections
        with st.expander("💡 Suggested Sections"):
            suggested = video_mode.get_suggested_sections()
            cols = st.columns(2)
            for i, section in enumerate(suggested):
                with cols[i % 2]:
                    if st.button(section, key=f"section_{i}"):
                        st.session_state.video_section = section
        
        section = st.text_input(
            "Topic/Section to Summarize:",
            value=st.session_state.get('video_section', 'Complete Chapter Overview'),
            placeholder="e.g., Supply and Demand Basics",
            key="section_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🎬 Generate Summary", type="primary")
    
    if generate_button:
        if section:
            with st.spinner("Creating comprehensive summary..."):
                result = video_mode.generate_summary(topic=section)
            
            # Display summary
            st.markdown("### 📺 Video-Style Summary")
            st.markdown("---")
            st.markdown(result['summary'])
            
            # Download option
            st.download_button(
                label="📥 Download Summary",
                data=result['summary'],
                file_name=f"summary_{section.replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
            # Show sources
            with st.expander(f"📚 View Sources ({result['num_sources']} used)"):
                for i, source in enumerate(result['sources'], 1):
                    st.markdown(f"**{i}. {source['type'].upper()}** - {source['source']}")
                    st.caption(source['text'][:200] + "...")
                    st.markdown("---")
        else:
            st.warning("Please enter a topic or section to summarize.")


if __name__ == "__main__":
    main()
