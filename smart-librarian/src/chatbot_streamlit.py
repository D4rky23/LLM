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

# Custom CSS for professional appearance and better contrast
st.markdown(
    """
<style>
.main-header {
    font-size: 2.5rem;
    color: #1a365d;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 600;
}

.chat-message {
    padding: 1.2rem;
    border-radius: 0.5rem;
    margin: 0.8rem 0;
    border: 1px solid #e2e8f0;
}

.user-message {
    background-color: #f7fafc;
    border-left: 4px solid #3182ce;
    color: #2d3748;
}

.assistant-message {
    background-color: #f0fff4;
    border-left: 4px solid #38a169;
    color: #2d3748;
}

.sample-query {
    cursor: pointer;
    padding: 0.75rem;
    border-radius: 0.375rem;
    border: 1px solid #cbd5e0;
    margin: 0.5rem 0;
    background-color: #ffffff;
    color: #2d3748;
    font-weight: 500;
}

.sample-query:hover {
    background-color: #edf2f7;
    border-color: #a0aec0;
}

.feature-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border-radius: 0.375rem;
    margin: 0.5rem 0;
    font-weight: 500;
}

.feature-available {
    background-color: #f0fff4;
    border: 1px solid #9ae6b4;
    color: #22543d;
}

.feature-unavailable {
    background-color: #fed7d7;
    border: 1px solid #feb2b2;
    color: #742a2a;
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
    st.sidebar.header("[SYSTEM] Status Overview")

    components = [
        ("config", "[CONFIG] Configuration"),
        ("data", "[DATA] Data Loading"),
        ("vector_store", "[SEARCH] Vector Store"),
        ("chatbot", "[AI] Chatbot"),
        ("tts", "[AUDIO] Text-to-Speech"),
        ("stt", "[VOICE] Speech-to-Text"),
        ("image_gen", "[IMAGE] Image Generation"),
    ]

    for key, label in components:
        if status.get(key, False):
            st.sidebar.markdown(f"**✓ {label}** - Ready")
        else:
            error_msg = errors.get(key, "Unavailable")
            st.sidebar.markdown(f"**✗ {label}** - Error")
            if key in errors:
                st.sidebar.caption(f"Details: {error_msg}")


def display_sample_queries():
    """Display sample queries that users can click."""
    st.subheader("[SAMPLES] Example Questions")

    sample_queries = [
        "I want a book about friendship and magic.",
        "What do you recommend for someone who loves war stories?",
        "I want a book about freedom and social control.",
        "What is 1984 about?",
    ]

    for i, query in enumerate(sample_queries):
        if st.button(query, key=f"sample_{i}"):
            # Store the selected query in session state for one-time use
            st.session_state.selected_query = query

    # Return and clear the selected query
    if hasattr(st.session_state, "selected_query"):
        query = st.session_state.selected_query
        del st.session_state.selected_query
        return query

    return None


def display_chat_history():
    """Display chat history."""
    if st.session_state.chat_history:
        st.subheader("[CHAT] Conversation History")

        for i, (role, message, timestamp) in enumerate(
            st.session_state.chat_history
        ):
            if role == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>[USER] You ({timestamp}):</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="chat-message assistant-message">
                    <strong>[AI] Smart Librarian ({timestamp}):</strong><br>
                    {message}
                </div>
                """,
                    unsafe_allow_html=True,
                )


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
    """Process user input and generate response."""
    if not user_input.strip():
        return

    # Add user message to history
    timestamp = time.strftime("%H:%M")
    st.session_state.chat_history.append(("user", user_input, timestamp))

    # Process with chatbot
    with st.spinner("Processing response..."):
        try:
            response = st.session_state.chatbot.chat(user_input)

            # Add assistant response to history
            st.session_state.chat_history.append(
                ("assistant", response, timestamp)
            )

            # Generate TTS if enabled
            if use_tts and st.session_state.system_status.get("tts", False):
                with st.spinner("Generating audio..."):
                    audio_path = speak(response)
                    if audio_path and audio_path.exists():
                        st.success(f"[AUDIO] Generated: {audio_path.name}")

                        # Play audio in browser
                        with open(audio_path, "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/mp3")

            # Generate image if enabled
            if use_image and st.session_state.system_status.get(
                "image_gen", False
            ):
                if (
                    "recommend" in response.lower()
                    or "book" in response.lower()
                ):
                    with st.spinner("Generating image..."):
                        try:
                            # Extract book title and themes from response
                            book_title, book_themes = (
                                extract_book_info_from_response(response)
                            )

                            st.info(
                                f"[IMAGE] Generating cover for: '{book_title}' with themes: {', '.join(book_themes)}"
                            )

                            image_path = generate_cover(
                                book_title, book_themes
                            )
                            if image_path and image_path.exists():
                                st.success(
                                    f"[IMAGE] Generated: {image_path.name}"
                                )
                                st.image(
                                    str(image_path),
                                    caption=f"Generated cover for '{book_title}'",
                                    width=300,
                                )
                        except Exception as e:
                            st.error(f"Image generation error: {e}")

        except Exception as e:
            st.error(f"Error processing response: {e}")


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

    # Header
    st.markdown(
        '<h1 class="main-header">[AI] Smart Librarian</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "*Professional AI chatbot for book recommendations with RAG and tool calling*"
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

    # Input methods
    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input(
            "[INPUT] Your Question:",
            value="",  # Always start with empty input
            placeholder="Ask about books...",
            key="user_input",
        )

    with col2:
        # Voice input button
        if use_stt and status.get("stt", False):
            if st.button("[VOICE] Speak"):
                with st.spinner("Listening... (5 seconds)"):
                    try:
                        transcribed = transcribe("microphone", duration=5)
                        if transcribed:
                            # Use session state to store transcribed text
                            st.session_state.transcribed_text = transcribed
                            st.success(f"Recognized: {transcribed}")
                        else:
                            st.error(
                                "Could not recognize speech. Please try again or use text input."
                            )
                    except Exception as e:
                        st.error(f"Speech recognition error: {str(e)}")
                        st.info(
                            "💡 **Tip**: If microphone isn't working, you can still use Whisper API for file uploads!"
                        )

        # Display transcribed text if available
        if hasattr(st.session_state, "transcribed_text"):
            if st.session_state.transcribed_text:
                st.info(
                    f"🎤 Last transcribed: {st.session_state.transcribed_text}"
                )
                if st.button("Use this text"):
                    user_input = st.session_state.transcribed_text
                    st.session_state.transcribed_text = ""  # Clear after use

    # Process input
    submit_clicked = st.button("[SEND] Submit")

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

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #4a5568; font-weight: 500;">
        Smart Librarian v1.0 | Powered by OpenAI GPT & ChromaDB
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
