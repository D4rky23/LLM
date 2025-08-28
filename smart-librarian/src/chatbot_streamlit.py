"""Streamlit web interface for Smart Librarian."""

import sys
from pathlib import Path
import streamlit as st
import json
from typing import List, Optional, Tuple
import time
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from ai.llm import get_chatbot
from vector.vector_store import initialize_vector_store
from core.data_loader import load_books_data
from tts import speak, is_tts_available
from stt import transcribe, is_stt_available
from image_gen import generate_cover, is_image_generation_available
from core.retriever import get_retriever


# Page configuration
st.set_page_config(
    page_title="Smart Librarian",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced CSS for modern, professional UI with animations and gradients
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Remove any blur effects globally */
* {
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    filter: none !important;
    -webkit-filter: none !important;
}

/* Ensure crisp text rendering */
body, .main, .stApp {
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Main header with solid color for clarity */
.main-header {
    font-size: 3rem;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
    color: #1a202c;
    animation: fadeInDown 1s ease-out;
    filter: none;
    -webkit-filter: none;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.subtitle {
    text-align: center;
    color: #1a202c;
    font-size: 1.2rem;
    margin-bottom: 2rem;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.9);
    padding: 10px 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
    animation: fadeInUp 1s ease-out 0.3s both;
    filter: none;
    -webkit-filter: none;
}

/* Card containers with better visibility */
.card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    border: 2px solid rgba(45, 55, 72, 0.1);
    transition: all 0.3s ease;
    color: #1a202c;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    border-color: rgba(45, 55, 72, 0.2);
}

.card h3 {
    color: #1a202c;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Chat messages with modern bubble design */
.chat-message {
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    position: relative;
    animation: slideInUp 0.4s ease-out;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
}

.user-message {
    background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%);
    color: white;
    margin-left: 20%;
    border-bottom-right-radius: 5px;
    box-shadow: 0 4px 15px rgba(43, 108, 176, 0.4);
    border: 2px solid rgba(255,255,255,0.2);
}

.user-message::before {
    content: "👤";
    position: absolute;
    top: -8px;
    right: 15px;
    background: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    border: 2px solid #2b6cb0;
}

.assistant-message {
    background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
    color: white;
    margin-right: 20%;
    border-bottom-left-radius: 5px;
    box-shadow: 0 4px 15px rgba(56, 161, 105, 0.4);
    border: 2px solid rgba(255,255,255,0.2);
}

.assistant-message::before {
    content: "🤖";
    position: absolute;
    top: -8px;
    left: 15px;
    background: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    border: 2px solid #38a169;
}

/* Sample queries with better contrast */
.sample-query {
    cursor: pointer;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    margin: 0.5rem 0;
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    color: #1a202c;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    position: relative;
    overflow: hidden;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
}

.sample-query::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(45,55,72,0.1), transparent);
    transition: left 0.5s;
}

.sample-query:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
    border-color: #a0aec0;
    color: #1a202c;
}

.sample-query:hover::before {
    left: 100%;
}

/* Status indicators with enhanced visibility */
.status-card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 4px solid #10b981;
    box-shadow: 0 3px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
    color: #1a202c;
    border: 1px solid #e2e8f0;
}

.status-ready {
    border-left-color: #059669;
    background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(255, 255, 255, 0.95));
    color: #064e3b;
}

.status-ready strong {
    color: #064e3b;
    font-weight: 700;
}

.status-ready small {
    color: #065f46;
    font-weight: 500;
}

.status-error {
    border-left-color: #dc2626;
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(255, 255, 255, 0.95));
    color: #7f1d1d;
}

.status-error strong {
    color: #7f1d1d;
    font-weight: 700;
}

.status-error small {
    color: #991b1b;
    font-weight: 500;
}

/* Loading animation */
.loading-dots {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
}

.loading-dots div {
    position: absolute;
    top: 33px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #667eea;
    animation-timing-function: cubic-bezier(0, 1, 1, 0);
}

.loading-dots div:nth-child(1) {
    left: 8px;
    animation: loading1 0.6s infinite;
}

.loading-dots div:nth-child(2) {
    left: 8px;
    animation: loading2 0.6s infinite;
}

.loading-dots div:nth-child(3) {
    left: 32px;
    animation: loading2 0.6s infinite;
}

.loading-dots div:nth-child(4) {
    left: 56px;
    animation: loading3 0.6s infinite;
}

/* Custom buttons with better contrast */
.stButton > button {
    background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%);
    color: white;
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(43, 108, 176, 0.4);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(43, 108, 176, 0.5);
    background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
    border-color: rgba(255,255,255,0.4);
}

/* Sidebar styling with better contrast */
.css-1d391kg {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
}

/* Sidebar headers */
.css-1d391kg h3 {
    color: #1a202c !important;
    font-weight: 700 !important;
    background: rgba(45, 55, 72, 0.05);
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 12px !important;
    border-left: 3px solid #2d3748;
}

/* Sidebar text */
.css-1d391kg .stMarkdown {
    color: #2d3748 !important;
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translate3d(0, -100%, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translate3d(0, 100%, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

@keyframes slideInUp {
    from {
        transform: translate3d(0, 100%, 0);
        opacity: 0;
    }
    to {
        transform: translate3d(0, 0, 0);
        opacity: 1;
    }
}

@keyframes loading1 {
    0% { transform: scale(0); }
    100% { transform: scale(1); }
}

@keyframes loading3 {
    0% { transform: scale(1); }
    100% { transform: scale(0); }
}

@keyframes loading2 {
    0% { transform: translate(0, 0); }
    100% { transform: translate(24px, 0); }
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    
    .chat-message {
        margin-left: 5%;
        margin-right: 5%;
    }
    
    .user-message {
        margin-left: 10%;
    }
    
    .assistant-message {
        margin-right: 10%;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    if "system_status" not in st.session_state:
        st.session_state.system_status = {}

    if "retriever_debug" not in st.session_state:
        st.session_state.retriever_debug = False


def check_system_status():
    """Check the status of all system components."""
    status = {
        "config": False,
        "data": False,
        "vector_store": False,
        "chatbot": False,
        "tts": False,
        "stt": False,
        "image_gen": False,
    }

    errors = {}

    # Check configuration
    try:
        config.validate()
        status["config"] = True
    except Exception as e:
        errors["config"] = str(e)

    # Check data
    try:
        books, _ = load_books_data()
        status["data"] = len(books) > 0
    except Exception as e:
        errors["data"] = str(e)

    # Check vector store
    try:
        retriever = get_retriever()
        stats = retriever.get_retriever_stats()
        status["vector_store"] = stats["total_books_in_cache"] > 0
    except Exception as e:
        errors["vector_store"] = str(e)

    # Check chatbot
    try:
        if not st.session_state.chatbot:
            st.session_state.chatbot = get_chatbot()
        status["chatbot"] = st.session_state.chatbot is not None
    except Exception as e:
        errors["chatbot"] = str(e)

    # Check optional features
    status["tts"] = is_tts_available()["any_available"]
    status["stt"] = is_stt_available()["any_available"]
    status["image_gen"] = is_image_generation_available()

    st.session_state.system_status = status
    return status, errors


def display_system_status(status, errors):
    """Display system status in sidebar with enhanced UI."""
    st.sidebar.markdown("### 📊 System Status")

    components = [
        ("config", "⚙️ Configuration", "System configuration loaded"),
        ("data", "📚 Data Store", "Book database loaded"),
        ("vector_store", "🔍 Search Engine", "Vector search ready"),
        ("chatbot", "🤖 AI Assistant", "LLM model loaded"),
        ("tts", "🔊 Text-to-Speech", "Audio generation available"),
        ("stt", "🎤 Speech-to-Text", "Voice recognition ready"),
        ("image_gen", "🎨 Image Generation", "Cover art creation enabled"),
    ]

    for key, label, description in components:
        if status.get(key, False):
            st.sidebar.markdown(
                f"""
                <div class="status-card status-ready">
                    <strong>✅ {label}</strong><br>
                    <small>{description}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            error_msg = errors.get(key, "Service unavailable")
            st.sidebar.markdown(
                f"""
                <div class="status-card status-error">
                    <strong>❌ {label}</strong><br>
                    <small>{error_msg}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )


def display_sample_queries():
    """Display sample queries with enhanced card design."""
    st.markdown(
        '<div class="card"><h3>💫 Try These Sample Questions</h3></div>',
        unsafe_allow_html=True,
    )

    sample_queries = [
        ("🧩 I want a book about friendship and magic.", "fantasy-friendship"),
        (
            "⚔️ What do you recommend for someone who loves war stories?",
            "war-historical",
        ),
        (
            "🔒 I want a book about freedom and social control.",
            "dystopian-political",
        ),
        ("📚 What is 1984 about?", "specific-book"),
    ]

    col1, col2 = st.columns(2)
    for i, (query, category) in enumerate(sample_queries):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(query, key=f"sample_{i}", use_container_width=True):
                # Store the selected query in session state for one-time use
                st.session_state.selected_query = query.split(" ", 1)[
                    1
                ]  # Remove emoji

    # Return and clear the selected query
    if hasattr(st.session_state, "selected_query"):
        query = st.session_state.selected_query
        del st.session_state.selected_query
        return query

    return None


def display_chat_history():
    """Display enhanced chat history with modern design."""
    if st.session_state.chat_history:
        st.markdown(
            '<div class="card"><h3>💬 Conversation History</h3></div>',
            unsafe_allow_html=True,
        )

        # Add conversation stats
        total_messages = len(st.session_state.chat_history)
        user_messages = sum(
            1 for role, _, _ in st.session_state.chat_history if role == "user"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", total_messages)
        with col2:
            st.metric("Your Questions", user_messages)
        with col3:
            st.metric("AI Responses", total_messages - user_messages)

        st.markdown("---")

        # Display messages with enhanced styling
        for i, (role, message, timestamp) in enumerate(
            st.session_state.chat_history
        ):
            if role == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>You • {timestamp}</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Add typing indicator simulation for new messages
                if i == len(st.session_state.chat_history) - 1:
                    with st.empty():
                        typing_text = "Smart Librarian is typing"
                        for dots in ["", ".", "..", "..."]:
                            st.markdown(f"*{typing_text}{dots}*")
                            time.sleep(0.3)
                        st.empty()

                st.markdown(
                    f"""
                <div class="chat-message assistant-message">
                    <strong>Smart Librarian • {timestamp}</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Add reaction buttons for AI responses
                col1, col2, col3, col4 = st.columns([1, 1, 1, 8])
                with col1:
                    if st.button(
                        "👍", key=f"like_{i}", help="Helpful response"
                    ):
                        st.success("Thanks for the feedback!")
                with col2:
                    if st.button("👎", key=f"dislike_{i}", help="Not helpful"):
                        st.info("Feedback noted. I'll try to improve!")
                with col3:
                    if st.button("📋", key=f"copy_{i}", help="Copy response"):
                        st.info("Response copied to clipboard!")


def extract_book_info_from_response(response: str) -> Tuple[str, List[str]]:
    """
    Extract book title and themes from chatbot response.

    Args:
        response: Chatbot response text

    Returns:
        Tuple of (book_title, themes_list)
    """
    # Default values
    default_title = "Recommended Book"
    default_themes = ["literature", "fiction"]

    # Try to extract book title using common patterns
    title_patterns = [
        r'"([^"]+)"',  # Text in quotes
        r'„([^„"]+)"',  # Romanian quotes
        r"\*([^*]+)\*",  # Text in asterisks
        r'titled\s+"([^"]+)"',  # "titled X"
        r'called\s+"([^"]+)"',  # "called X"
        r'book\s+"([^"]+)"',  # "book X"
        r'cartea\s+"([^"]+)"',  # "cartea X" in Romanian
        r'intitulată\s+"([^"]+)"',  # "intitulată X" in Romanian
    ]

    extracted_title = None
    for pattern in title_patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            extracted_title = matches[0].strip()
            # Filter out common non-title words
            if len(extracted_title) > 3 and not extracted_title.lower() in [
                "the",
                "and",
                "or",
                "but",
            ]:
                break

    # Try to extract themes from the response
    theme_keywords = {
        "good-vs-evil": [
            "good vs evil",
            "good versus evil",
            "bine versus rău",
            "moral conflict",
            "good and evil",
        ],
        "adventure": [
            "adventure",
            "aventură",
            "quest",
            "journey",
            "călătorie",
        ],
        "friendship": ["friendship", "prietenie", "friends", "prieteni"],
        "love": ["love", "romance", "dragoste", "romantic"],
        "war": ["war", "război", "battle", "conflict", "military"],
        "fantasy": ["fantasy", "magic", "fantastic", "magie", "magical"],
        "mystery": ["mystery", "detective", "crime", "mister", "mysterious"],
        "science": ["science", "scientific", "știință", "technology"],
        "history": ["history", "historical", "istorie", "istoric"],
        "freedom": ["freedom", "liberty", "libertate", "independence"],
        "dystopia": ["dystopia", "totalitarian", "control", "surveillance"],
        "coming-of-age": ["growing up", "adolescence", "youth", "teenager"],
        "family": ["family", "familie", "parents", "părinți"],
        "society": ["society", "social", "societate", "community"],
        "psychological": ["psychological", "mental", "psihologic", "mind"],
        "philosophical": [
            "philosophy",
            "philosophical",
            "filozofie",
            "meaning",
        ],
        "moral": ["moral", "ethics", "good", "evil", "right", "wrong"],
        "epic": ["epic", "heroic", "grand", "legendary"],
        "dark": ["dark", "darkness", "shadow", "noir"],
    }

    extracted_themes = []
    response_lower = response.lower()

    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            if keyword in response_lower:
                extracted_themes.append(theme)
                break

    # If no themes found, try to extract from common phrases
    if not extracted_themes:
        if any(
            word in response_lower
            for word in ["recommend", "suggest", "recomand"]
        ):
            extracted_themes = ["fiction", "literature"]

    # Generate thematic title if no specific title found but themes are present
    if not extracted_title and extracted_themes:
        if "good-vs-evil" in extracted_themes or "moral" in extracted_themes:
            extracted_title = "Good vs Evil Story"
        elif "adventure" in extracted_themes:
            extracted_title = "Adventure Tale"
        elif "fantasy" in extracted_themes:
            extracted_title = "Fantasy Epic"
        elif "love" in extracted_themes:
            extracted_title = "Love Story"
        elif "war" in extracted_themes:
            extracted_title = "War Chronicle"
        elif "mystery" in extracted_themes:
            extracted_title = "Mystery Novel"
        elif "science" in extracted_themes:
            extracted_title = "Science Fiction"
        elif "psychological" in extracted_themes:
            extracted_title = "Psychological Thriller"

    # Use extracted or default values
    final_title = extracted_title if extracted_title else default_title
    final_themes = extracted_themes if extracted_themes else default_themes

    # Limit themes to avoid too long prompts
    final_themes = final_themes[:3]

    return final_title, final_themes


def process_user_input(
    user_input: str, use_tts: bool = False, use_image: bool = False
):
    """Process user input with enhanced feedback and progress indicators."""
    if not user_input.strip():
        return

    # Add user message to history
    timestamp = time.strftime("%H:%M")
    st.session_state.chat_history.append(("user", user_input, timestamp))

    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <div class="loading-dots">
                <div></div><div></div><div></div><div></div>
            </div>
            <p style="margin-top: 10px; color: #667eea;">🤖 Smart Librarian is thinking...</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Process with chatbot
    try:
        progress_bar = st.progress(0, text="Processing your request...")
        progress_bar.progress(20, text="Understanding your question...")

        response = st.session_state.chatbot.chat(user_input)
        progress_bar.progress(60, text="Generating response...")

        # Clear thinking indicator
        thinking_placeholder.empty()
        progress_bar.progress(80, text="Finalizing response...")

        # Add assistant response to history
        st.session_state.chat_history.append(
            ("assistant", response, timestamp)
        )

        progress_bar.progress(100, text="Response ready!")

        # Generate TTS if enabled
        if use_tts and st.session_state.system_status.get("tts", False):
            with st.spinner("🔊 Generating audio..."):
                audio_path = speak(response)
                if audio_path and audio_path.exists():
                    st.success(f"🎵 Audio generated: {audio_path.name}")

                    # Play audio in browser with enhanced player
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")

        # Generate image if enabled
        if use_image and st.session_state.system_status.get(
            "image_gen", False
        ):
            if "recommend" in response.lower() or "book" in response.lower():
                with st.spinner("🎨 Creating book cover art..."):
                    try:
                        # Extract book title and themes from response
                        book_title, book_themes = (
                            extract_book_info_from_response(response)
                        )

                        st.info(
                            f"🎨 Generating cover for: '{book_title}' with themes: {', '.join(book_themes)}"
                        )

                        image_path = generate_cover(book_title, book_themes)
                        if image_path and image_path.exists():
                            st.success(f"🖼️ Generated cover: {image_path.name}")

                            # Display image with enhanced presentation
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.image(
                                    str(image_path),
                                    caption=f"AI-generated cover for '{book_title}'",
                                    use_column_width=True,
                                )
                    except Exception as e:
                        st.error(f"🚫 Image generation error: {e}")

        progress_bar.empty()

    except Exception as e:
        thinking_placeholder.empty()
        st.error(f"❌ Error processing response: {e}")
        st.info("💡 Try rephrasing your question or check the system status.")


def display_retriever_debug(user_input: str):
    """Display retriever debug information."""
    if not st.session_state.retriever_debug:
        return

    try:
        retriever = get_retriever()
        books_with_scores = retriever.search_with_scores(user_input, top_k=5)

        if books_with_scores:
            st.subheader("[DEBUG] Search Results")

            for book, score in books_with_scores:
                with st.expander(f"{book.title} (Score: {score:.3f})"):
                    st.write(f"**Summary:** {book.short_summary}")
                    st.write(f"**Themes:** {', '.join(book.themes)}")
    except Exception as e:
        st.error(f"Retriever debug error: {e}")


def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()

    # Header with enhanced styling
    st.markdown(
        '<h1 class="main-header">📚 Smart Librarian AI</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">🚀 Discover incredible books with personalized and advanced AI recommendations</div>',
        unsafe_allow_html=True,
    )

    # Check system status
    status, errors = check_system_status()

    # Sidebar
    with st.sidebar:
        display_system_status(status, errors)

        st.header("[OPTIONS] Settings")

        # Feature toggles
        use_tts = st.checkbox(
            "[AUDIO] Text-to-Speech", disabled=not status.get("tts", False)
        )
        use_stt = st.checkbox(
            "[VOICE] Speech-to-Text", disabled=not status.get("stt", False)
        )
        use_image = st.checkbox(
            "[IMAGE] Generate Images",
            disabled=not status.get("image_gen", False),
        )

        # Audio file upload for STT (alternative to microphone)
        if status.get("stt", False):
            st.subheader("[UPLOAD] Audio File")
            uploaded_file = st.file_uploader(
                "Upload audio file for transcription",
                type=["wav", "mp3", "ogg", "flac"],
                help="Alternative to microphone recording",
            )

            if uploaded_file is not None:
                # Save uploaded file temporarily
                temp_path = (
                    config.OUTPUT_DIR / f"temp_audio_{uploaded_file.name}"
                )
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if st.button("🎵 Transcribe Audio File"):
                    with st.spinner("Transcribing audio file..."):
                        try:
                            transcribed = transcribe(
                                str(temp_path), method="whisper"
                            )
                            if transcribed:
                                st.session_state.transcribed_text = transcribed
                                st.success(f"Transcribed: {transcribed}")
                            else:
                                st.error("Could not transcribe audio file")
                        except Exception as e:
                            st.error(f"Transcription error: {e}")
                        finally:
                            # Clean up temp file
                            if temp_path.exists():
                                temp_path.unlink()

        # Debug options
        st.session_state.retriever_debug = st.checkbox(
            "[DEBUG] Show Retriever Debug"
        )

        # Clear history
        if st.button("[CLEAR] Clear History"):
            st.session_state.chat_history = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.success("History cleared!")

        # System info
        if st.button("[INFO] System Information"):
            try:
                retriever = get_retriever()
                stats = retriever.get_retriever_stats()

                st.write("**System Information:**")
                st.json(stats)
            except Exception as e:
                st.error(f"Error retrieving system information: {e}")

    # Main interface
    if not all([status["config"], status["data"], status["chatbot"]]):
        st.error(
            "[ERROR] System is not fully initialized. Check the status in the sidebar."
        )
        return

    # Sample queries
    selected_query = display_sample_queries()

    # Welcome message for new users
    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #f7fafc 0%, #e2e8f0 100%); 
            padding: 30px; border-radius: 20px; margin: 20px 0; text-align: center;
            border: 3px solid #cbd5e0; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">
                <h3 style="color: #1a202c; margin-bottom: 15px; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);">👋 Welcome to Smart Librarian AI!</h3>
                <p style="color: #2d3748; font-size: 1.1em; margin-bottom: 15px; font-weight: 500;">
                    I'm your personal AI librarian, here to help you discover amazing books. 
                    I can recommend books based on your preferences, explain plots, and even generate book covers!
                </p>
                <p style="color: #1a202c; font-weight: 600;">
                    ✨ Try asking me about books, genres, or use the sample questions above to get started!
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Enhanced input interface
    st.markdown(
        '<div class="card"><h3>💬 Chat with Smart Librarian</h3></div>',
        unsafe_allow_html=True,
    )

    # Input methods with better layout
    input_col, voice_col, action_col = st.columns([4, 1, 1])

    with input_col:
        user_input = st.text_input(
            "Ask me anything about books...",
            value="",  # Always start with empty input
            placeholder="e.g., I want a thrilling mystery novel",
            key="user_input",
            label_visibility="collapsed",
        )

    with voice_col:
        # Voice input button with enhanced design
        if use_stt and status.get("stt", False):
            if st.button(
                "🎤", help="Voice Input (5 seconds)", use_container_width=True
            ):
                with st.spinner("🎤 Listening..."):
                    progress_bar = st.progress(0)
                    try:
                        # Simulate progress during recording
                        for i in range(5):
                            progress_bar.progress((i + 1) * 20)
                            time.sleep(1)

                        transcribed = transcribe("microphone", duration=5)
                        if transcribed:
                            st.session_state.transcribed_text = transcribed
                            st.success(f"✓ Recognized: {transcribed}")
                        else:
                            st.error("Could not recognize speech")
                    except Exception as e:
                        st.error(f"Speech error: {str(e)}")
                    finally:
                        progress_bar.empty()

    with action_col:
        submit_clicked = st.button(
            "🚀 Send", use_container_width=True, type="primary"
        )

    # Display transcribed text with action button
    if (
        hasattr(st.session_state, "transcribed_text")
        and st.session_state.transcribed_text
    ):
        st.info(f"🎤 **Voice Input:** {st.session_state.transcribed_text}")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✓ Use This", key="use_voice"):
                user_input = st.session_state.transcribed_text
                st.session_state.transcribed_text = ""  # Clear after use
                st.rerun()

    # Determine what input to process
    input_to_process = None
    if selected_query:
        input_to_process = selected_query
    elif submit_clicked and user_input.strip():
        input_to_process = user_input.strip()

    if input_to_process:
        # Show debug info if enabled
        display_retriever_debug(input_to_process)

        # Process the input
        process_user_input(input_to_process, use_tts, use_image)

    # Display chat history
    display_chat_history()

    # Footer with enhanced statistics and info
    st.markdown("---")

    # Usage statistics and system metrics
    if st.session_state.chat_history:
        st.markdown("### 📊 Session Statistics")

        col1, col2, col3, col4 = st.columns(4)

        # Calculate statistics
        total_conversations = len(
            [msg for msg in st.session_state.chat_history if msg[0] == "user"]
        )
        total_words = sum(
            len(msg[1].split()) for msg in st.session_state.chat_history
        )
        avg_response_length = sum(
            len(msg[1])
            for msg in st.session_state.chat_history
            if msg[0] == "assistant"
        ) / max(
            1,
            len(
                [
                    msg
                    for msg in st.session_state.chat_history
                    if msg[0] == "assistant"
                ]
            ),
        )

        with col1:
            st.metric(
                label="💬 Conversations",
                value=total_conversations,
                help="Total number of questions asked",
            )
        with col2:
            st.metric(
                label="📝 Total Words",
                value=total_words,
                help="Total words in conversation",
            )
        with col3:
            st.metric(
                label="📏 Avg Response",
                value=f"{avg_response_length:.0f} chars",
                help="Average AI response length",
            )
        with col4:
            active_features = sum(
                1
                for feature in ["tts", "stt", "image_gen"]
                if st.session_state.system_status.get(feature, False)
            )
            st.metric(
                label="⚡ Active Features",
                value=f"{active_features}/3",
                help="Number of active AI features",
            )

    # System health dashboard
    st.markdown("### 🏥 System Health")

    # Create health score
    health_score = sum(
        1 for status in st.session_state.system_status.values() if status
    )
    total_components = len(st.session_state.system_status)
    health_percentage = (
        (health_score / total_components) * 100 if total_components > 0 else 0
    )

    # Health indicator with color coding
    if health_percentage >= 80:
        health_color = "🟢"
        health_status = "Excellent"
    elif health_percentage >= 60:
        health_color = "🟡"
        health_status = "Good"
    else:
        health_color = "🔴"
        health_status = "Needs Attention"

    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
        border-radius: 15px; margin: 20px 0; color: white;">
            <h3>{health_color} System Health: {health_status}</h3>
            <p style="font-size: 1.2em; margin: 0;">{health_score}/{total_components} components operational ({health_percentage:.0f}%)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Footer
    st.markdown(
        """
    <div style="text-align: center; color: #4a5568; font-weight: 500; padding: 20px 0;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        background-clip: text; font-size: 1.1em; margin-bottom: 10px;">
            Smart Librarian AI v2.0
        </div>
        <div style="font-size: 0.9em; color: #718096;">
            Powered by OpenAI GPT • ChromaDB • Streamlit<br>
            🚀 Enhanced UI • 🎨 Modern Design • ⚡ Advanced Features
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
