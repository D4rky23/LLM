"""Speech-to-Text functionality for Smart Librarian."""

import logging
import io
from pathlib import Path
from typing import Optional

try:
    import speech_recognition as sr

    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

import openai
from core.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transcribe_with_whisper_api(audio_file_path: Path) -> Optional[str]:
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        audio_file_path: Path to audio file

    Returns:
        Transcribed text or None if failed
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language="ro"  # Romanian
            )

        transcription = response.text
        logger.info(
            f"Whisper API transcription successful: {transcription[:50]}..."
        )
        return transcription

    except Exception as e:
        logger.error(f"Error with Whisper API: {e}")
        return None


def transcribe_with_speech_recognition(
    audio_source: str = "microphone",
    duration: int = 5,
    language: str = "ro-RO",
) -> Optional[str]:
    """
    Transcribe audio using SpeechRecognition library.

    Args:
        audio_source: "microphone" or path to audio file
        duration: Recording duration in seconds (for microphone)
        language: Language code

    Returns:
        Transcribed text or None if failed
    """
    if not SR_AVAILABLE:
        logger.error(
            "SpeechRecognition not available. Install with: pip install SpeechRecognition"
        )
        return None

    try:
        recognizer = sr.Recognizer()

        if audio_source == "microphone":
            if not PYAUDIO_AVAILABLE:
                logger.error(
                    "PyAudio not available. Install with: pip install pyaudio"
                )
                return None

            # Try different microphones
            for mic_index in [None, 0, 1]:
                try:
                    if mic_index is None:
                        microphone = sr.Microphone()
                    else:
                        microphone = sr.Microphone(device_index=mic_index)

                    # Record from microphone
                    with microphone as source:
                        logger.info("Adjusting for ambient noise...")
                        recognizer.adjust_for_ambient_noise(
                            source, duration=0.5
                        )

                        logger.info(f"Recording for {duration} seconds...")
                        audio = recognizer.listen(
                            source,
                            timeout=duration,
                            phrase_time_limit=duration,
                        )
                    break  # Successfully recorded

                except Exception as mic_error:
                    logger.warning(
                        f"Microphone {mic_index} failed: {mic_error}"
                    )
                    if mic_index == 1:  # Last attempt
                        return None
                    continue
        else:
            # Load from audio file
            with sr.AudioFile(audio_source) as source:
                audio = recognizer.record(source)

        # Try different recognition services
        try:
            # Try Google Speech Recognition (free)
            text = recognizer.recognize_google(audio, language=language)
            logger.info(
                f"Google Speech Recognition successful: {text[:50]}..."
            )
            return text
        except sr.RequestError:
            logger.warning("Google Speech Recognition unavailable")

        try:
            # Try Sphinx (offline, but might not support Romanian well)
            text = recognizer.recognize_sphinx(audio)
            logger.info(f"Sphinx recognition successful: {text[:50]}...")
            return text
        except sr.RequestError:
            logger.warning("Sphinx recognition unavailable")

        logger.error("No speech recognition service available")
        return None

    except Exception as e:
        logger.error(f"Error with speech recognition: {e}")
        return None


def record_and_save_audio(
    duration: int = 5, output_path: Path = None
) -> Optional[Path]:
    """
    Record audio from microphone and save to file.

    Args:
        duration: Recording duration in seconds
        output_path: Path to save audio file

    Returns:
        Path to saved audio file or None if failed
    """
    if not SR_AVAILABLE or not PYAUDIO_AVAILABLE:
        logger.error("Required libraries not available for audio recording")
        return None

    if output_path is None:
        import time

        timestamp = int(time.time())
        output_path = config.OUTPUT_DIR / f"recording_{timestamp}.wav"

    try:
        recognizer = sr.Recognizer()

        # Try different microphone indices if default fails
        for mic_index in [None, 0, 1]:
            try:
                if mic_index is None:
                    microphone = sr.Microphone()
                else:
                    microphone = sr.Microphone(device_index=mic_index)

                with microphone as source:
                    logger.info("Adjusting for ambient noise...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)

                    logger.info(f"Recording for {duration} seconds...")
                    audio = recognizer.listen(
                        source, timeout=duration, phrase_time_limit=duration
                    )

                # Save audio to file
                with open(output_path, "wb") as f:
                    f.write(audio.get_wav_data())

                logger.info(f"Audio saved to: {output_path}")
                return output_path

            except Exception as mic_error:
                logger.warning(f"Microphone {mic_index} failed: {mic_error}")
                continue

        # If all microphones failed
        logger.error("All microphone attempts failed")
        return None

    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        return None


def transcribe(
    audio_source: str = "microphone",
    duration: int = 5,
    method: str = "auto",
    language: str = "ro-RO",
) -> Optional[str]:
    """
    Main transcription function.

    Args:
        audio_source: "microphone" or path to audio file
        duration: Recording duration for microphone
        method: "whisper", "speech_recognition", or "auto"
        language: Language code

    Returns:
        Transcribed text or None if failed
    """
    if audio_source == "microphone":
        # Record audio first
        temp_audio_path = record_and_save_audio(duration)
        if not temp_audio_path:
            return None
        audio_file_path = temp_audio_path
    else:
        audio_file_path = Path(audio_source)
        if not audio_file_path.exists():
            logger.error(f"Audio file not found: {audio_file_path}")
            return None

    # Choose transcription method
    if method == "auto":
        # Try Whisper API first (better quality), then SpeechRecognition
        if config.OPENAI_API_KEY:
            method = "whisper"
        elif SR_AVAILABLE:
            method = "speech_recognition"
        else:
            logger.error("No transcription method available")
            return None

    # Transcribe
    if method == "whisper":
        return transcribe_with_whisper_api(audio_file_path)
    elif method == "speech_recognition":
        return transcribe_with_speech_recognition(
            str(audio_file_path), duration, language
        )
    else:
        logger.error(f"Unknown transcription method: {method}")
        return None


def is_stt_available() -> dict:
    """
    Check which STT libraries/services are available.

    Returns:
        Dictionary with availability status
    """
    return {
        "speech_recognition": SR_AVAILABLE,
        "pyaudio": PYAUDIO_AVAILABLE,
        "whisper_api": bool(config.OPENAI_API_KEY),
        "microphone_available": SR_AVAILABLE and PYAUDIO_AVAILABLE,
        "any_available": SR_AVAILABLE or bool(config.OPENAI_API_KEY),
    }


def test_microphone() -> bool:
    """
    Test microphone functionality.

    Returns:
        True if microphone works
    """
    if not SR_AVAILABLE or not PYAUDIO_AVAILABLE:
        logger.error("Required libraries not available for microphone test")
        return False

    try:
        recognizer = sr.Recognizer()

        # List available microphones
        try:
            mic_list = sr.Microphone.list_microphone_names()
            logger.info(f"Available microphones: {len(mic_list)}")

            if not mic_list:
                logger.error("No microphones found")
                return False
        except Exception as e:
            logger.warning(f"Could not list microphones: {e}")

        # Test different microphone indices
        for mic_index in [None, 0, 1]:
            try:
                if mic_index is None:
                    microphone = sr.Microphone()
                else:
                    microphone = sr.Microphone(device_index=mic_index)

                with microphone as source:
                    logger.info(f"Testing microphone {mic_index}...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    logger.info("Microphone test successful")
                    return True

            except Exception as mic_error:
                logger.warning(
                    f"Microphone {mic_index} test failed: {mic_error}"
                )
                continue

        logger.error("All microphone tests failed")
        return False

    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return False


def test_stt(duration: int = 3) -> bool:
    """
    Test STT functionality.

    Args:
        duration: Recording duration for test

    Returns:
        True if test successful
    """
    logger.info("Testing STT functionality...")

    # Check availability
    availability = is_stt_available()
    print(f"STT Availability: {availability}")

    if not availability["any_available"]:
        print("No STT services available!")
        return False

    if availability["microphone_available"]:
        print(f"Testing microphone recording for {duration} seconds...")
        print("Please speak something...")

        # Test transcription
        result = transcribe("microphone", duration=duration)

        if result:
            print(f"STT test successful! Transcription: '{result}'")
            return True
        else:
            print("STT test failed!")
            return False
    else:
        print("Microphone not available for testing")
        return False


if __name__ == "__main__":
    # Test STT functionality
    print("Testing Speech-to-Text...")

    # Check availability
    availability = is_stt_available()
    print(f"Available STT methods: {availability}")

    if availability["microphone_available"]:
        # Test microphone
        mic_test = test_microphone()
        print(f"Microphone test: {'SUCCESS' if mic_test else 'FAILED'}")

        if mic_test:
            # Test STT
            input(
                "Press Enter to start STT test (will record for 3 seconds)..."
            )
            stt_test = test_stt(3)
            print(f"STT Test result: {'SUCCESS' if stt_test else 'FAILED'}")
    else:
        print("STT libraries not available. Install with:")
        print("pip install SpeechRecognition")
        print("pip install pyaudio")

        if availability["whisper_api"]:
            print("Whisper API is available for file transcription")
