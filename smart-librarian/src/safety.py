"""Safety filter for Smart Librarian to detect offensive content."""

import re
import logging
from typing import List, Set

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Offensive words in Romanian and English
OFFENSIVE_WORDS: Set[str] = {
    # Romanian offensive words (keep it simple and basic)
    "injurii",
    "blasfemii",
    "vulgară",
    "obscenități",
    "jigniri",
    "ură",
    "violență",
    "agresiv",
    "amenințare",
    "discriminare",
    # English offensive words (basic)
    "hate",
    "violence",
    "offensive",
    "racism",
    "sexism",
    "discrimination",
    "harassment",
    "threat",
    "abuse",
    # Additional from config
    *config.OFFENSIVE_WORDS,
}

# Patterns for detecting inappropriate content
OFFENSIVE_PATTERNS = [
    r"\b(hate|ură)\s+(speech|vorbire)\b",
    r"\b(kill|ucide|omor)\b",
    r"\b(violence|violență)\b",
    r"\b(racist|rasist)\b",
    r"\b(sexist|sexist)\b",
    r"\b(discrimination|discriminare)\b",
]


def normalize_text(text: str) -> str:
    """
    Normalize text for offensive content detection.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text.strip())

    # Remove punctuation for word detection
    text = re.sub(r"[^\w\s]", " ", text)

    return text


def contains_offensive_words(text: str) -> bool:
    """
    Check if text contains offensive words.

    Args:
        text: Text to check

    Returns:
        True if offensive words found
    """
    normalized = normalize_text(text)
    words = normalized.split()

    for word in words:
        if word in OFFENSIVE_WORDS:
            logger.warning(f"Offensive word detected: {word}")
            return True

    return False


def contains_offensive_patterns(text: str) -> bool:
    """
    Check if text matches offensive patterns.

    Args:
        text: Text to check

    Returns:
        True if offensive patterns found
    """
    normalized = normalize_text(text)

    for pattern in OFFENSIVE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            logger.warning(f"Offensive pattern detected: {pattern}")
            return True

    return False


def is_aggressive_tone(text: str) -> bool:
    """
    Detect aggressive tone using simple heuristics.

    Args:
        text: Text to check

    Returns:
        True if aggressive tone detected
    """
    # Count exclamation marks and caps
    exclamations = text.count("!")
    caps_words = sum(
        1 for word in text.split() if word.isupper() and len(word) > 2
    )

    # Simple heuristic: too many exclamations or caps words
    if exclamations > 3 or caps_words > 2:
        logger.warning("Aggressive tone detected")
        return True

    return False


def is_offensive(text: str) -> bool:
    """
    Main function to check if text is offensive.

    Args:
        text: Text to check

    Returns:
        True if text is considered offensive
    """
    if not text or not text.strip():
        return False

    try:
        # Check for offensive words
        if contains_offensive_words(text):
            return True

        # Check for offensive patterns
        if contains_offensive_patterns(text):
            return True

        # Check for aggressive tone
        if is_aggressive_tone(text):
            return True

        return False

    except Exception as e:
        logger.error(f"Error in safety check: {e}")
        # In case of error, be conservative and allow the text
        return False


def get_safety_response() -> str:
    """
    Get the standard safety response message.

    Returns:
        Safety response in Romanian
    """
    return "Aș prefera să păstrăm conversația într-un limbaj adecvat. Poți reformula, te rog?"


def add_offensive_word(word: str):
    """
    Add a word to the offensive words set.

    Args:
        word: Word to add
    """
    OFFENSIVE_WORDS.add(word.lower())
    logger.info(f"Added offensive word: {word}")


def remove_offensive_word(word: str):
    """
    Remove a word from the offensive words set.

    Args:
        word: Word to remove
    """
    OFFENSIVE_WORDS.discard(word.lower())
    logger.info(f"Removed offensive word: {word}")


def get_offensive_words() -> List[str]:
    """
    Get current list of offensive words (for debugging).

    Returns:
        List of offensive words
    """
    return sorted(list(OFFENSIVE_WORDS))


def validate_safety_filter() -> bool:
    """
    Validate the safety filter with test cases.

    Returns:
        True if all tests pass
    """
    test_cases = [
        # Should be flagged as offensive
        ("This is hate speech", True),
        ("I hate violence", True),
        ("STOP SHOUTING!!!", True),
        # Should be safe
        ("Vreau o carte despre prietenie", False),
        ("Ce recomanzi pentru o poveste frumoasă?", False),
        ("Mulțumesc pentru recomandare!", False),
    ]

    all_passed = True

    for text, expected in test_cases:
        result = is_offensive(text)
        if result != expected:
            logger.error(
                f"Safety test failed: '{text}' -> {result}, expected {expected}"
            )
            all_passed = False
        else:
            logger.info(f"Safety test passed: '{text}' -> {result}")

    return all_passed


if __name__ == "__main__":
    # Test safety filter
    print("Testing safety filter...")

    # Test cases
    test_texts = [
        "Vreau o carte despre prietenie și magie",
        "Ce recomanzi pentru povești de război?",
        "This is hate speech and violence!",
        "STOP SHOUTING AT ME!!!",
        "Mulțumesc pentru recomandare",
        "hate violence discrimination",
    ]

    for text in test_texts:
        is_bad = is_offensive(text)
        print(f"'{text}' -> {'OFFENSIVE' if is_bad else 'SAFE'}")

    # Run validation
    print(
        f"\nValidation result: {'PASSED' if validate_safety_filter() else 'FAILED'}"
    )

    # Show offensive words count
    print(f"Total offensive words loaded: {len(OFFENSIVE_WORDS)}")
