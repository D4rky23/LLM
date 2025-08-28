"""Image generation for Smart Librarian using OpenAI DALL-E."""

import logging
from pathlib import Path
from typing import List, Optional
import re

import openai
from PIL import Image
import requests

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = config.OPENAI_API_KEY


def create_safe_filename(title: str) -> str:
    """
    Create a safe filename from book title.

    Args:
        title: Book title

    Returns:
        Safe filename
    """
    # Remove special characters and replace spaces with underscores
    safe_name = re.sub(r"[^\w\s-]", "", title)
    safe_name = re.sub(r"[-\s]+", "_", safe_name)
    return safe_name.lower()


def generate_cover_prompt(title: str, themes: List[str]) -> str:
    """
    Generate a prompt for book cover image generation.

    Args:
        title: Book title
        themes: List of book themes

    Returns:
        Generated prompt for DALL-E
    """
    themes_str = ", ".join(
        themes[:3]
    )  # Use first 3 themes to avoid long prompts

    prompt = (
        f"Minimalist, modern book cover illustration for '{title}' "
        f"highlighting themes: {themes_str}. "
        f"High contrast, artistic style, no text, "
        f"suitable for book cover design, clean composition"
    )

    return prompt


def generate_cover_with_dalle(
    title: str,
    themes: List[str],
    size: str = "1024x1024",
    quality: str = "standard",
) -> Optional[str]:
    """
    Generate book cover using OpenAI DALL-E.

    Args:
        title: Book title
        themes: List of themes
        size: Image size ("1024x1024", "1792x1024", "1024x1792")
        quality: Image quality ("standard" or "hd")

    Returns:
        URL of generated image or None if failed
    """
    try:
        prompt = generate_cover_prompt(title, themes)

        logger.info(
            f"Generating cover for '{title}' with prompt: {prompt[:100]}..."
        )

        response = openai.images.generate(
            model="dall-e-3", prompt=prompt, size=size, quality=quality, n=1
        )

        image_url = response.data[0].url
        logger.info(f"Image generated successfully for '{title}'")

        return image_url

    except Exception as e:
        logger.error(f"Error generating image with DALL-E: {e}")
        return None


def download_image(image_url: str, output_path: Path) -> bool:
    """
    Download image from URL and save to file.

    Args:
        image_url: URL of the image
        output_path: Path to save the image

    Returns:
        True if successful
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Save to file
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Image saved to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return False


def resize_image(image_path: Path, max_size: tuple = (800, 600)) -> bool:
    """
    Resize image to fit within max dimensions.

    Args:
        image_path: Path to image file
        max_size: Maximum (width, height)

    Returns:
        True if successful
    """
    try:
        with Image.open(image_path) as img:
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save resized image
            img.save(image_path, optimize=True, quality=85)

        logger.info(f"Image resized: {image_path}")
        return True

    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return False


def generate_cover(
    title: str,
    themes: List[str],
    output_filename: str = None,
    resize: bool = True,
) -> Optional[Path]:
    """
    Generate and save book cover image.

    Args:
        title: Book title
        themes: List of themes
        output_filename: Output filename (auto-generated if None)
        resize: Whether to resize the image

    Returns:
        Path to saved image file or None if failed
    """
    if not config.OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return None

    if not title or not themes:
        logger.error("Title and themes are required")
        return None

    # Generate output filename if not provided
    if output_filename is None:
        safe_title = create_safe_filename(title)
        output_filename = f"{safe_title}_cover.png"

    output_path = config.OUTPUT_DIR / output_filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate image with DALL-E
    image_url = generate_cover_with_dalle(title, themes)
    if not image_url:
        return None

    # Download image
    if not download_image(image_url, output_path):
        return None

    # Resize if requested
    if resize:
        resize_image(output_path)

    return output_path


def is_image_generation_available() -> bool:
    """
    Check if image generation is available.

    Returns:
        True if available
    """
    return bool(config.OPENAI_API_KEY)


def get_image_info(image_path: Path) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with image information
    """
    if not image_path.exists():
        return {"error": "File not found"}

    try:
        with Image.open(image_path) as img:
            return {
                "filename": image_path.name,
                "size": img.size,
                "format": img.format,
                "mode": img.mode,
                "file_size": image_path.stat().st_size,
            }
    except Exception as e:
        return {"error": str(e)}


def create_collage(image_paths: List[Path], output_path: Path) -> bool:
    """
    Create a collage from multiple images.

    Args:
        image_paths: List of image file paths
        output_path: Path to save collage

    Returns:
        True if successful
    """
    if not image_paths:
        return False

    try:
        images = []
        for path in image_paths:
            if path.exists():
                with Image.open(path) as img:
                    images.append(img.copy())

        if not images:
            return False

        # Simple horizontal collage
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        collage = Image.new("RGB", (total_width, max_height), "white")

        x_offset = 0
        for img in images:
            collage.paste(img, (x_offset, 0))
            x_offset += img.width

        collage.save(output_path)
        logger.info(f"Collage saved to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating collage: {e}")
        return False


def test_image_generation(
    title: str = "The Hobbit", themes: List[str] = None
) -> bool:
    """
    Test image generation functionality.

    Args:
        title: Test book title
        themes: Test themes

    Returns:
        True if test successful
    """
    if themes is None:
        themes = ["adventure", "friendship", "magic"]

    logger.info("Testing image generation...")

    if not is_image_generation_available():
        print("Image generation not available (no OpenAI API key)")
        return False

    # Generate test image
    output_path = generate_cover(title, themes, "test_cover.png")

    if output_path and output_path.exists():
        info = get_image_info(output_path)
        print(f"Image generation test successful! Image info: {info}")
        return True
    else:
        print("Image generation test failed!")
        return False


if __name__ == "__main__":
    # Test image generation
    print("Testing Image Generation...")

    # Check availability
    available = is_image_generation_available()
    print(f"Image generation available: {available}")

    if available:
        # Test generation
        test_result = test_image_generation()
        print(f"Test result: {'SUCCESS' if test_result else 'FAILED'}")
    else:
        print("Configure OPENAI_API_KEY to enable image generation")
