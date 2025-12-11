"""
NotebookLM-Style Study Tool - Audio & Text Interface
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv
import streamlit.components.v1 as components
import google.generativeai as genai

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
from modes.qa_mode import QAMode
from modes.dialogue_mode import DialogueMode

# Page config
st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="centered"
)

# Minimal CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        max-width: 700px;
        margin: 0 auto;
        padding-top: 2rem;
    }
    
    .stSpinner {display: none !important;}
    
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Hide default chat input */
    .stChatInputContainer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_system():
    """Load RAG system silently."""
    generator = EmbeddingGenerator()
    store = VectorStore()
    
    if not store.exists():
        st.stop()
    
    store.load(generator)
    retriever = RAGRetriever(store)
    
    qa_mode = QAMode(retriever)
    dialogue_mode = DialogueMode(retriever)
    
    return qa_mode, dialogue_mode


def transcribe_audio(audio_bytes):
    """Transcribe audio using Google Gemini."""
    try:
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        # Use Gemini for audio transcription
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Save audio temporarily
        temp_file = "temp_audio.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
        
        # Upload and transcribe
        audio_file = genai.upload_file(temp_file)
        response = model.generate_content([
            "Transcribe this audio. Only return the spoken text, nothing else.",
            audio_file
        ])
        
        # Cleanup
        os.remove(temp_file)
        
        return response.text.strip()
    except Exception as e:
        return None


def text_to_speech(text):
    """Generate audio from text using browser's speech synthesis."""
    # Use JavaScript to trigger browser's text-to-speech
    speech_js = f"""
    <script>
        const text = {repr(text)};
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    </script>
    """
    st.components.v1.html(speech_js, height=0)


def main():
    # Check API key silently
    if not os.getenv("GOOGLE_API_KEY"):
        st.stop()
    
    # Load system
    qa_mode, dialogue_mode = load_system()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""
    
    # Show welcome message
    if not st.session_state.messages:
        st.markdown("### Ask me about economics")
        st.markdown("")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Custom input with mic/send icon
    input_html = """
    <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 700px; z-index: 1000;">
        <div style="display: flex; align-items: center; background: white; border: 2px solid #e0e0e0; border-radius: 25px; padding: 10px 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <input type="text" id="userInput" placeholder="Type your question..." 
                   style="flex: 1; border: none; outline: none; font-size: 16px; padding: 5px 10px;">
            <button id="actionBtn" onclick="handleAction()" 
                    style="background: none; border: none; font-size: 24px; cursor: pointer; padding: 5px 10px;">
                🎤
            </button>
        </div>
    </div>
    
    <script>
        const input = document.getElementById('userInput');
        const btn = document.getElementById('actionBtn');
        
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                btn.innerHTML = '📤';
            } else {
                btn.innerHTML = '🎤';
            }
        });
        
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                sendMessage();
            }
        });
        
        function handleAction() {
            const text = input.value.trim();
            if (text) {
                sendMessage();
            } else {
                startRecording();
            }
        }
        
        function sendMessage() {
            const text = input.value.trim();
            if (text) {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
                input.value = '';
                btn.innerHTML = '🎤';
            }
        }
        
        function startRecording() {
            alert('Voice recording feature - click mic to record (feature in development)');
        }
    </script>
    """
    
    user_input = components.html(input_html, height=100)
    
    # Process user input
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.spinner(""):
            try:
                # Get recent conversation for context
                recent_history = st.session_state.messages[-6:] if len(st.session_state.messages) > 1 else []
                context_str = "\n".join([
                    f"{'You' if msg['role'] == 'user' else 'Me'}: {msg['content']}"
                    for msg in recent_history[:-1]
                ])
                
                # Create conversational prompt
                if context_str:
                    full_prompt = f"Previous conversation:\n{context_str}\n\nStudent's new message: {user_input}\n\nRespond naturally and conversationally as a helpful teacher, referring to previous messages if relevant."
                else:
                    full_prompt = f"Respond naturally and conversationally as a helpful teacher to: {user_input}"
                
                result = qa_mode.ask_question(full_prompt, k=3)
                response = result.get('answer', str(result))
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            
            except Exception as e:
                error_msg = f"Sorry, there was an error: {str(e)[:100]}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()

if __name__ == "__main__":
    main()
