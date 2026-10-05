"""
AI-Powered YouTube Video Chatbot
Main Streamlit Application File
"""
import streamlit as st
import os
import sys

import importlib

# Add src module to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import src.utils
import src.transcript
import src.embeddings
import src.rag

# Force reload of custom src modules on each app run
importlib.reload(src.utils)
importlib.reload(src.transcript)
importlib.reload(src.embeddings)
importlib.reload(src.rag)

from src.utils import extract_video_id, validate_youtube_url, load_api_key
from src.transcript import get_youtube_transcript
from src.embeddings import get_text_chunks, create_vector_store
from src.rag import generate_summary_and_key_points, answer_question

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AI YouTube Video Chatbot",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        color: #FF0000;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    .source-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-left: 4px solid #FF0000;
        border-radius: 4px;
        font-size: 0.9rem;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "video_id" not in st.session_state:
    st.session_state.video_id = ""
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "key_points" not in st.session_state:
    st.session_state.key_points = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed" not in st.session_state:
    st.session_state.processed = False

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/youtube-play.png", width=70)
    st.title("📌 Settings & Control")
    
    # API Key Handling
    api_key = load_api_key()
    
    if not api_key or api_key == "your_gemini_api_key_here":
        st.warning("⚠️ Google Gemini API Key missing!")
        user_api_key = st.text_input("Enter Gemini API Key:", type="password", help="Get free key at https://aistudio.google.com/")
        if user_api_key:
            api_key = user_api_key.strip()
    else:
        st.success("✅ Gemini API Key Loaded")

    st.markdown("---")
    st.subheader("🎥 Process YouTube Video")
    
    url_input = st.text_input(
        "YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        value=st.session_state.video_url
    )
    
    process_btn = st.button("🚀 Process Video", use_container_width=True, type="primary")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("""
    **How to use:**
    1. Enter YouTube video link.
    2. Click **Process Video**.
    3. Review summary & key points.
    4. Ask questions in the chat!
    """)

# Main Content Header
st.markdown('<div class="main-title">🎥 AI-Powered YouTube Video Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ask questions, get summaries, and analyze any YouTube video using RAG & Google Gemini</div>', unsafe_allow_html=True)

# Processing Logic when "Process Video" button clicked
if process_btn:
    if not url_input.strip():
        st.error("❌ Please enter a YouTube video URL.")
    elif not api_key or api_key == "your_gemini_api_key_here":
        st.error("❌ Google Gemini API Key is missing. Please provide a valid key in the sidebar or .env file.")
    else:
        try:
            with st.spinner("1️⃣ Extracting YouTube Video ID..."):
                video_id = extract_video_id(url_input)
                st.session_state.video_id = video_id
                st.session_state.video_url = url_input.strip()

            with st.spinner("2️⃣ Fetching & cleaning transcript..."):
                transcript_text = get_youtube_transcript(video_id)
                st.session_state.transcript = transcript_text

            with st.spinner("3️⃣ Chunking text & building FAISS Vector Store..."):
                chunks = get_text_chunks(transcript_text)
                vector_store = create_vector_store(chunks, api_key)
                st.session_state.vector_store = vector_store

            with st.spinner("4️⃣ Generating AI Summary & Key Points..."):
                summary, key_points = generate_summary_and_key_points(transcript_text, api_key)
                st.session_state.summary = summary
                st.session_state.key_points = key_points

            st.session_state.processed = True
            st.session_state.chat_history = [] # Reset chat for new video
            st.success("🎉 Video processed successfully! You can now review the summary or ask questions below.")

        except Exception as e:
            st.session_state.processed = False
            st.error(f"❌ Error processing video: {str(e)}")

# Display Main Content if Video Processed
if st.session_state.processed and st.session_state.video_id:
    
    # Video & Preview Section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📺 Video Player")
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")
        
    with col2:
        st.subheader("📌 Key Takeaways")
        if st.session_state.key_points:
            for pt in st.session_state.key_points:
                st.markdown(f"- {pt}")
        else:
            st.info("No key points generated.")
            
    st.markdown("---")
    
    # Tabs for Summary, Transcript, and Q&A
    tab1, tab2, tab3 = st.tabs(["📝 AI Summary", "📜 Full Transcript Preview", "💬 Interactive Chat"])
    
    with tab1:
        st.markdown("### 📝 Executive Video Summary")
        st.write(st.session_state.summary)

    with tab2:
        st.markdown("### 📜 Video Transcript")
        st.text_area("Cleaned Transcript Text", st.session_state.transcript, height=300)

    with tab3:
        st.markdown("### 💬 Chat with Video")
        st.caption("Answers are strictly grounded in the video transcript.")
        
        # Display existing chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Display sources if present in message metadata
                if message.get("sources"):
                    with st.expander("🔍 View Relevant Transcript Context Snippets"):
                        for idx, snippet in enumerate(message["sources"], 1):
                            st.markdown(f"**Chunk {idx}:**\n> {snippet}")

        # User Question Input
        user_question = st.chat_input("Ask a question about this video...")
        
        if user_question:
            # Display user message
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Searching transcript and generating answer..."):
                    try:
                        answer, sources = answer_question(
                            vector_store=st.session_state.vector_store,
                            question=user_question,
                            chat_history=st.session_state.chat_history,
                            api_key=api_key
                        )
                        st.markdown(answer)
                        
                        if sources:
                            with st.expander("🔍 View Relevant Transcript Context Snippets"):
                                for idx, snippet in enumerate(sources, 1):
                                    st.markdown(f"**Chunk {idx}:**\n> {snippet}")

                        # Save to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg
                        })

else:
    # Landing page message when no video processed yet
    st.info("👈 Please enter a YouTube URL in the sidebar and click **Process Video** to get started!")
    
    st.markdown("""
    ### Features of this application:
    - 🎯 **Transcript Extraction**: Automatically fetches transcripts from YouTube videos using `youtube-transcript-api`.
    - 🧠 **RAG Pipeline**: Chunking with LangChain, embedding with Google Gemini, and similarity search with FAISS.
    - 📝 **Automated Summaries**: Generates high-level summaries and bulleted key points.
    - 💬 **Grounded Chat**: Interactive Q&A strictly grounded in transcript content to eliminate AI hallucination.
    - 🔍 **Source Snippets**: View exact transcript chunks used to generate each answer.
    """)
