"""Streamlit web interface for Smart Librarian."""

import sys
from pathlib import Path
import streamlit as st
import json
from typing import List, Optional
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from llm import get_chatbot
from vector_store import initialize_vector_store
from data_loader import load_books_data
from tts import speak, is_tts_available
from stt import transcribe, is_stt_available
from image_gen import generate_cover, is_image_generation_available
from retriever import get_retriever


# Page configuration
st.set_page_config(
    page_title="Smart Librarian",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}

.user-message {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}

.assistant-message {
    background-color: #f1f8e9;
    border-left: 4px solid #4caf50;
}

.sample-query {
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.25rem;
    border: 1px solid #ddd;
    margin: 0.25rem 0;
    background-color: #f8f9fa;
}

.sample-query:hover {
    background-color: #e9ecef;
}

.feature-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
}

.feature-available {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.feature-unavailable {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
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
    """Display system status in sidebar."""
    st.sidebar.header("📊 System Status")

    components = [
        ("config", "⚙️ Configuration"),
        ("data", "📚 Data Loading"),
        ("vector_store", "🔍 Vector Store"),
        ("chatbot", "🤖 Chatbot"),
        ("tts", "🔊 Text-to-Speech"),
        ("stt", "🎤 Speech-to-Text"),
        ("image_gen", "🖼️ Image Generation"),
    ]

    for key, label in components:
        if status.get(key, False):
            st.sidebar.markdown(f"✅ {label}")
        else:
            error_msg = errors.get(key, "Indisponibil")
            st.sidebar.markdown(f"❌ {label}")
            if key in errors:
                st.sidebar.caption(f"Error: {error_msg}")


def display_sample_queries():
    """Display sample queries that users can click."""
    st.subheader("💡 Exemple de întrebări")

    sample_queries = [
        "Vreau o carte despre prietenie și magie.",
        "Ce recomanzi pentru cineva care iubește povești de război?",
        "Vreau o carte despre libertate și control social.",
        "Ce este 1984?",
    ]

    for i, query in enumerate(sample_queries):
        if st.button(query, key=f"sample_{i}"):
            return query

    return None


def display_chat_history():
    """Display chat history."""
    if st.session_state.chat_history:
        st.subheader("💬 Conversație")

        for i, (role, message, timestamp) in enumerate(
            st.session_state.chat_history
        ):
            if role == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>👤 Tu ({timestamp}):</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Smart Librarian ({timestamp}):</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )


def process_user_input(
    user_input: str, use_tts: bool = False, use_image: bool = False
):
    """Process user input and generate response."""
    if not user_input.strip():
        return

    # Add user message to history
    timestamp = time.strftime("%H:%M")
    st.session_state.chat_history.append(("user", user_input, timestamp))

    # Process with chatbot
    with st.spinner("Procesare răspuns..."):
        try:
            response = st.session_state.chatbot.chat(user_input)

            # Add assistant response to history
            st.session_state.chat_history.append(
                ("assistant", response, timestamp)
            )

            # Generate TTS if enabled
            if use_tts and st.session_state.system_status.get("tts", False):
                with st.spinner("Generare audio..."):
                    audio_path = speak(response)
                    if audio_path and audio_path.exists():
                        st.success(f"🔊 Audio generat: {audio_path.name}")

                        # Play audio in browser
                        with open(audio_path, "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/mp3")

            # Generate image if enabled
            if use_image and st.session_state.system_status.get(
                "image_gen", False
            ):
                if (
                    "recomand" in response.lower()
                    or "carte" in response.lower()
                ):
                    with st.spinner("Generare imagine..."):
                        try:
                            # Basic approach to extract book title
                            # This could be improved with proper NLP
                            image_path = generate_cover(
                                "Cartea Recomandată", ["aventură", "prietenie"]
                            )
                            if image_path and image_path.exists():
                                st.success(
                                    f"🖼️ Imagine generată: {image_path.name}"
                                )
                                st.image(
                                    str(image_path),
                                    caption="Copertă generată",
                                    width=300,
                                )
                        except Exception as e:
                            st.error(f"Eroare la generarea imaginii: {e}")

        except Exception as e:
            st.error(f"Eroare la procesarea răspunsului: {e}")


def display_retriever_debug(user_input: str):
    """Display retriever debug information."""
    if not st.session_state.retriever_debug:
        return

    try:
        retriever = get_retriever()
        books_with_scores = retriever.search_with_scores(user_input, top_k=5)

        if books_with_scores:
            st.subheader("🔍 Debug: Rezultate căutare")

            for book, score in books_with_scores:
                with st.expander(f"{book.title} (Score: {score:.3f})"):
                    st.write(f"**Rezumat:** {book.short_summary}")
                    st.write(f"**Teme:** {', '.join(book.themes)}")
    except Exception as e:
        st.error(f"Eroare debug retriever: {e}")


def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown(
        '<h1 class="main-header">📚 Smart Librarian</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "*AI chatbot pentru recomandări de cărți cu RAG și tool calling*"
    )

    # Check system status
    status, errors = check_system_status()

    # Sidebar
    with st.sidebar:
        display_system_status(status, errors)

        st.header("⚙️ Opțiuni")

        # Feature toggles
        use_tts = st.checkbox(
            "🔊 Text-to-Speech", disabled=not status.get("tts", False)
        )
        use_stt = st.checkbox(
            "🎤 Speech-to-Text", disabled=not status.get("stt", False)
        )
        use_image = st.checkbox(
            "🖼️ Generare imagini", disabled=not status.get("image_gen", False)
        )

        # Debug options
        st.session_state.retriever_debug = st.checkbox("🔍 Debug retriever")

        # Clear history
        if st.button("🗑️ Șterge istoric"):
            st.session_state.chat_history = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.success("Istoric șters!")

        # System info
        if st.button("ℹ️ Info sistem"):
            try:
                retriever = get_retriever()
                stats = retriever.get_retriever_stats()

                st.write("**System Information:**")
                st.json(stats)
            except Exception as e:
                st.error(f"Eroare la obținerea informațiilor: {e}")

    # Main interface
    if not all([status["config"], status["data"], status["chatbot"]]):
        st.error(
            "🚫 Sistemul nu este complet inițializat. Verifică statusul din sidebar."
        )
        return

    # Sample queries
    selected_query = display_sample_queries()

    # Input methods
    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input(
            "💬 Întrebare:",
            value=selected_query if selected_query else "",
            placeholder="Întreabă despre cărți...",
        )

    with col2:
        # Voice input button
        if use_stt and status.get("stt", False):
            if st.button("🎤 Vorbește"):
                with st.spinner("Ascult... (5 secunde)"):
                    transcribed = transcribe("microphone", duration=5)
                    if transcribed:
                        user_input = transcribed
                        st.success(f"Recunoscut: {transcribed}")
                    else:
                        st.error("Nu am putut recunoaște vocea")

    # Process input
    if st.button("📤 Trimite") or selected_query:
        input_to_process = selected_query if selected_query else user_input
        if input_to_process:
            # Show debug info if enabled
            display_retriever_debug(input_to_process)

            # Process the input
            process_user_input(input_to_process, use_tts, use_image)

            # Rerun to update the interface
            st.rerun()

    # Display chat history
    display_chat_history()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666;">
        Smart Librarian v1.0 | Powered by OpenAI GPT & ChromaDB
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
