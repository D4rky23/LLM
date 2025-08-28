"""Tools for OpenAI function calling in Smart Librarian."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Callable

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load detailed summaries
book_summaries_dict = {}


def load_summaries_dict():
    """Load book summaries dictionary from JSON file."""
    global book_summaries_dict
    if not book_summaries_dict:
        try:
            with open(config.BOOK_SUMMARIES_JSON, "r", encoding="utf-8") as f:
                book_summaries_dict = json.load(f)
            logger.info(f"Loaded {len(book_summaries_dict)} book summaries")
        except Exception as e:
            logger.error(f"Error loading book summaries: {e}")
            book_summaries_dict = {}


def get_summary_by_title(title: str) -> str:
    """
    Get detailed summary for a book by exact title.

    Args:
        title: Exact book title

    Returns:
        Detailed book summary

    Raises:
        KeyError: If book title is not found
    """
    load_summaries_dict()

    if title not in book_summaries_dict:
        available_titles = list(book_summaries_dict.keys())
        logger.error(
            f"Book '{title}' not found. Available titles: {available_titles}"
        )
        raise KeyError(f"Cartea '{title}' nu a fost găsită în baza de date.")

    logger.info(f"Retrieved detailed summary for: {title}")
    return book_summaries_dict[title]


def get_available_books() -> list[str]:
    """
    Get list of all available book titles.

    Returns:
        List of book titles
    """
    load_summaries_dict()
    return list(book_summaries_dict.keys())


def find_closest_title(partial_title: str) -> str | None:
    """
    Find the closest matching title for a partial title.

    Args:
        partial_title: Partial or approximate title

    Returns:
        Closest matching title or None
    """
    load_summaries_dict()

    partial_lower = partial_title.lower()

    # First try exact match (case insensitive)
    for title in book_summaries_dict.keys():
        if title.lower() == partial_lower:
            return title

    # Then try partial match
    for title in book_summaries_dict.keys():
        if partial_lower in title.lower() or title.lower() in partial_lower:
            return title

    return None


# OpenAI Function Schema for get_summary_by_title
GET_SUMMARY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_summary_by_title",
        "description": "Returnează rezumatul detaliat pentru titlul exact al unei cărți. Folosește titlul exact așa cum apare în recomandare.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Titlul exact al cărții pentru care se dorește rezumatul detaliat",
                }
            },
            "required": ["title"],
        },
    },
}

# Tool registry for function calling
AVAILABLE_TOOLS = {"get_summary_by_title": get_summary_by_title}

# Tools schema for OpenAI
TOOLS_SCHEMA = [GET_SUMMARY_SCHEMA]


def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool call with given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments for the tool

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool is not found or execution fails
    """
    if tool_name not in AVAILABLE_TOOLS:
        available_tools = list(AVAILABLE_TOOLS.keys())
        raise ValueError(
            f"Tool '{tool_name}' not found. Available tools: {available_tools}"
        )

    try:
        tool_function = AVAILABLE_TOOLS[tool_name]
        result = tool_function(**arguments)
        logger.info(f"Successfully executed tool: {tool_name}")
        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise ValueError(f"Eroare la executarea tool-ului {tool_name}: {e}")


def validate_tool_call(tool_call: Dict[str, Any]) -> bool:
    """
    Validate a tool call structure.

    Args:
        tool_call: Tool call dictionary

    Returns:
        True if valid
    """
    required_fields = ["name", "arguments"]

    for field in required_fields:
        if field not in tool_call:
            return False

    if tool_call["name"] not in AVAILABLE_TOOLS:
        return False

    return True


def get_tool_response(tool_calls: list[Dict[str, Any]]) -> str:
    """
    Process multiple tool calls and return formatted response.

    Args:
        tool_calls: List of tool call dictionaries

    Returns:
        Formatted response with tool results
    """
    if not tool_calls:
        return ""

    responses = []

    for tool_call in tool_calls:
        try:
            if not validate_tool_call(tool_call):
                responses.append(f"Tool call invalid: {tool_call}")
                continue

            result = execute_tool_call(
                tool_call["name"], tool_call["arguments"]
            )
            responses.append(result)

        except Exception as e:
            error_msg = f"Eroare la executarea tool-ului: {e}"
            responses.append(error_msg)

    return "\n\n".join(responses)


if __name__ == "__main__":
    # Test tools functionality
    try:
        # Test loading summaries
        load_summaries_dict()
        print(f"Loaded {len(book_summaries_dict)} summaries")

        # Test get_summary_by_title
        test_titles = ["1984", "The Hobbit"]
        for title in test_titles:
            try:
                summary = get_summary_by_title(title)
                print(f"\n{title}: {summary[:100]}...")
            except KeyError as e:
                print(f"Error for {title}: {e}")

        # Test tool execution
        tool_call = {
            "name": "get_summary_by_title",
            "arguments": {"title": "1984"},
        }

        result = execute_tool_call(tool_call["name"], tool_call["arguments"])
        print(f"\nTool execution result: {result[:100]}...")

        # Test available books
        books = get_available_books()
        print(f"\nAvailable books: {books[:3]}...")

    except Exception as e:
        print(f"Error: {e}")
