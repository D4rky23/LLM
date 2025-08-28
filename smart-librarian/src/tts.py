"""Text-to-Speech functionality for Smart Librarian."""

import logging
from pathlib import Path
from typing import Optional

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from core.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def speak_with_gtts(text: str, output_path: Path, lang: str = "ro") -> bool:
    """
    Generate speech using Google Text-to-Speech (gTTS).

    Args:
        text: Text to convert to speech
        output_path: Path to save audio file
        lang: Language code (default: Romanian)

    Returns:
        True if successful
    """
    if not GTTS_AVAILABLE:
        logger.error("gTTS not available. Install with: pip install gTTS")
        return False

    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)

        # Save to file
        tts.save(str(output_path))

        logger.info(f"Audio saved to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error with gTTS: {e}")
        return False


def speak_with_pyttsx3(text: str, output_path: Path) -> bool:
    """
    Generate speech using pyttsx3 (offline).

    Args:
        text: Text to convert to speech
        output_path: Path to save audio file

    Returns:
        True if successful
    """
    if not PYTTSX3_AVAILABLE:
        logger.error(
            "pyttsx3 not available. Install with: pip install pyttsx3"
        )
        return False

    try:
        # Initialize TTS engine
        engine = pyttsx3.init()

        # Set properties
        engine.setProperty("rate", 150)  # Speaking rate
        engine.setProperty("volume", 0.8)  # Volume level (0.0 to 1.0)

        # Try to set Romanian voice if available
        voices = engine.getProperty("voices")
        for voice in voices:
            if "romania" in voice.name.lower() or "ro" in voice.id.lower():
                engine.setProperty("voice", voice.id)
                break

        # Save to file
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()

        logger.info(f"Audio saved to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error with pyttsx3: {e}")
        return False


def speak(
    text: str, output_filename: str = None, method: str = "auto"
) -> Optional[Path]:
    """
    Convert text to speech and save as audio file.

    Args:
        text: Text to convert to speech
        output_filename: Output filename (auto-generated if None)
        method: TTS method ("gtts", "pyttsx3", or "auto")

    Returns:
        Path to saved audio file if successful, None otherwise
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS")
        return None

    # Generate output filename if not provided
    if output_filename is None:
        import time

        timestamp = int(time.time())
        output_filename = f"recommendation_{timestamp}.mp3"

    output_path = config.OUTPUT_DIR / output_filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Choose TTS method
    if method == "auto":
        if GTTS_AVAILABLE:
            method = "gtts"
        elif PYTTSX3_AVAILABLE:
            method = "pyttsx3"
        else:
            logger.error("No TTS library available. Install gTTS or pyttsx3")
            return None

    # Convert to speech
    success = False

    if method == "gtts":
        success = speak_with_gtts(text, output_path)
    elif method == "pyttsx3":
        # Change extension to wav for pyttsx3
        if output_path.suffix == ".mp3":
            output_path = output_path.with_suffix(".wav")
        success = speak_with_pyttsx3(text, output_path)
    else:
        logger.error(f"Unknown TTS method: {method}")
        return None

    if success:
        return output_path
    else:
        return None


def is_tts_available() -> dict:
    """
    Check which TTS libraries are available.

    Returns:
        Dictionary with availability status
    """
    return {
        "gtts": GTTS_AVAILABLE,
        "pyttsx3": PYTTSX3_AVAILABLE,
        "any_available": GTTS_AVAILABLE or PYTTSX3_AVAILABLE,
    }


def get_available_voices() -> list:
    """
    Get list of available voices (for pyttsx3).

    Returns:
        List of voice information
    """
    if not PYTTSX3_AVAILABLE:
        return []

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        voice_list = []
        for voice in voices:
            voice_info = {
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, "languages", []),
                "gender": getattr(voice, "gender", "unknown"),
            }
            voice_list.append(voice_info)

        engine.stop()
        return voice_list

    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return []


def test_tts(
    text: str = "Aceasta este o testare a sistemului text-to-speech.",
) -> bool:
    """
    Test TTS functionality.

    Args:
        text: Test text

    Returns:
        True if test successful
    """
    logger.info("Testing TTS functionality...")

    # Check availability
    availability = is_tts_available()
    print(f"TTS Availability: {availability}")

    if not availability["any_available"]:
        print("No TTS libraries available!")
        return False

    # Test speech generation
    output_path = speak(text, "test_tts.mp3")

    if output_path and output_path.exists():
        print(f"TTS test successful! Audio saved to: {output_path}")
        return True
    else:
        print("TTS test failed!")
        return False


if __name__ == "__main__":
    # Test TTS functionality
    test_text = "Hello! This is Smart Librarian. I recommend the book 1984 by George Orwell."

    print("Testing Text-to-Speech...")

    # Check availability
    availability = is_tts_available()
    print(f"Available TTS methods: {availability}")

    if availability["any_available"]:
        # Test TTS
        result = test_tts(test_text)
        print(f"TTS Test result: {'SUCCESS' if result else 'FAILED'}")

        # Show available voices
        voices = get_available_voices()
        if voices:
            print(f"Available voices: {len(voices)}")
            for voice in voices[:3]:  # Show first 3
                print(f"- {voice['name']} ({voice['id']})")
    else:
        print("No TTS libraries installed. Install with:")
        print("pip install gTTS")
        print("pip install pyttsx3")
