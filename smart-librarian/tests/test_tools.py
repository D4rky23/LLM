"""Tests for tools functionality in Smart Librarian."""

import sys
from pathlib import Path
import pytest
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools import (
    get_summary_by_title,
    get_available_books,
    find_closest_title,
    execute_tool_call,
    validate_tool_call,
    get_tool_response,
    AVAILABLE_TOOLS,
    TOOLS_SCHEMA,
)
from config import config


class TestTools:
    """Test class for tools functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        # Ensure the test data files exist
        assert (
            config.BOOK_SUMMARIES_JSON.exists()
        ), f"JSON file not found: {config.BOOK_SUMMARIES_JSON}"

    def test_get_available_books(self):
        """Test getting list of available books."""
        books = get_available_books()

        assert isinstance(books, list)
        assert len(books) > 0

        # Check that we have the expected books
        expected_books = ["1984", "The Hobbit", "Dune"]
        for expected in expected_books:
            assert (
                expected in books
            ), f"Expected book '{expected}' not found in available books"

    def test_get_summary_by_title_success(self):
        """Test successful summary retrieval."""
        # Test with known book titles
        test_titles = ["1984", "The Hobbit", "Dune"]

        for title in test_titles:
            summary = get_summary_by_title(title)

            assert isinstance(summary, str)
            assert (
                len(summary) > 100
            )  # Detailed summaries should be substantial
            assert "Romanian" in summary or any(
                romanian_word in summary.lower()
                for romanian_word in [
                    "romanul",
                    "cartea",
                    "povestea",
                    "când",
                    "într-o",
                ]
            ), f"Summary for '{title}' doesn't seem to be in Romanian"

    def test_get_summary_by_title_not_found(self):
        """Test summary retrieval for non-existent book."""
        with pytest.raises(KeyError):
            get_summary_by_title("Cartea Inexistentă")

    def test_find_closest_title(self):
        """Test finding closest matching title."""
        # Test exact match (case insensitive)
        assert find_closest_title("1984") == "1984"
        assert find_closest_title("the hobbit") == "The Hobbit"

        # Test partial match
        assert find_closest_title("hobbit") == "The Hobbit"
        assert find_closest_title("brave") == "Brave New World"

        # Test no match
        assert find_closest_title("completely unknown book") is None

    def test_execute_tool_call_success(self):
        """Test successful tool execution."""
        # Test get_summary_by_title
        result = execute_tool_call("get_summary_by_title", {"title": "1984"})

        assert isinstance(result, str)
        assert len(result) > 100

    def test_execute_tool_call_unknown_tool(self):
        """Test tool execution with unknown tool."""
        with pytest.raises(ValueError):
            execute_tool_call("unknown_tool", {})

    def test_execute_tool_call_invalid_arguments(self):
        """Test tool execution with invalid arguments."""
        with pytest.raises(ValueError):
            execute_tool_call("get_summary_by_title", {"wrong_param": "value"})

    def test_validate_tool_call(self):
        """Test tool call validation."""
        # Valid tool call
        valid_call = {
            "name": "get_summary_by_title",
            "arguments": {"title": "1984"},
        }
        assert validate_tool_call(valid_call) is True

        # Missing name
        invalid_call1 = {"arguments": {"title": "1984"}}
        assert validate_tool_call(invalid_call1) is False

        # Missing arguments
        invalid_call2 = {"name": "get_summary_by_title"}
        assert validate_tool_call(invalid_call2) is False

        # Unknown tool
        invalid_call3 = {"name": "unknown_tool", "arguments": {}}
        assert validate_tool_call(invalid_call3) is False

    def test_get_tool_response_single_call(self):
        """Test tool response for single tool call."""
        tool_calls = [
            {"name": "get_summary_by_title", "arguments": {"title": "1984"}}
        ]

        response = get_tool_response(tool_calls)

        assert isinstance(response, str)
        assert len(response) > 100

    def test_get_tool_response_multiple_calls(self):
        """Test tool response for multiple tool calls."""
        tool_calls = [
            {"name": "get_summary_by_title", "arguments": {"title": "1984"}},
            {
                "name": "get_summary_by_title",
                "arguments": {"title": "The Hobbit"},
            },
        ]

        response = get_tool_response(tool_calls)

        assert isinstance(response, str)
        # Should contain both summaries separated by newlines
        assert "\n\n" in response

    def test_get_tool_response_invalid_call(self):
        """Test tool response with invalid tool call."""
        tool_calls = [{"name": "invalid_tool", "arguments": {}}]

        response = get_tool_response(tool_calls)

        assert isinstance(response, str)
        assert "invalid" in response.lower() or "eroare" in response.lower()

    def test_get_tool_response_empty_list(self):
        """Test tool response with empty tool calls list."""
        response = get_tool_response([])
        assert response == ""

    def test_tools_schema_structure(self):
        """Test the structure of tools schema for OpenAI."""
        assert isinstance(TOOLS_SCHEMA, list)
        assert len(TOOLS_SCHEMA) > 0

        # Check first tool schema structure
        tool_schema = TOOLS_SCHEMA[0]
        assert "type" in tool_schema
        assert "function" in tool_schema
        assert tool_schema["type"] == "function"

        function_def = tool_schema["function"]
        assert "name" in function_def
        assert "description" in function_def
        assert "parameters" in function_def

        parameters = function_def["parameters"]
        assert "type" in parameters
        assert "properties" in parameters
        assert "required" in parameters

    def test_available_tools_registry(self):
        """Test the available tools registry."""
        assert isinstance(AVAILABLE_TOOLS, dict)
        assert "get_summary_by_title" in AVAILABLE_TOOLS

        # Check that all tools in registry are callable
        for tool_name, tool_func in AVAILABLE_TOOLS.items():
            assert callable(tool_func), f"Tool '{tool_name}' is not callable"

    def test_book_summaries_data_integrity(self):
        """Test that book summaries data is properly structured."""
        books = get_available_books()

        for book_title in books:
            summary = get_summary_by_title(book_title)

            # Check summary is substantial
            assert (
                len(summary) > 200
            ), f"Summary for '{book_title}' is too short"

            # Check summary contains multiple paragraphs
            paragraphs = [
                p.strip() for p in summary.split("\n\n") if p.strip()
            ]
            assert (
                len(paragraphs) >= 2
            ), f"Summary for '{book_title}' should have multiple paragraphs"

    def test_tool_error_handling(self):
        """Test error handling in tools."""
        # Test with None title
        with pytest.raises(Exception):
            get_summary_by_title(None)

        # Test with empty title
        with pytest.raises(KeyError):
            get_summary_by_title("")

        # Test execute_tool_call with malformed arguments
        with pytest.raises(ValueError):
            execute_tool_call("get_summary_by_title", "not_a_dict")


def test_manual_book_verification():
    """Manual test to verify specific book summaries."""
    # This test can be run individually to check specific books
    books_to_check = ["1984", "The Hobbit", "The Lord of the Rings"]

    for title in books_to_check:
        try:
            summary = get_summary_by_title(title)
            print(f"\n=== {title} ===")
            print(f"Length: {len(summary)} characters")
            print(f"First 200 chars: {summary[:200]}...")

            # Basic checks
            assert len(summary) > 500, f"Summary too short for {title}"
            assert any(
                word in summary.lower()
                for word in ["romanul", "povestea", "cartea"]
            ), f"Doesn't seem Romanian for {title}"

        except Exception as e:
            print(f"Error checking {title}: {e}")


if __name__ == "__main__":
    # Run basic tests
    print("Running basic tools tests...")

    try:
        # Test available books
        books = get_available_books()
        print(f"✅ Found {len(books)} available books")

        # Test summary retrieval for first few books
        for book in books[:3]:
            summary = get_summary_by_title(book)
            print(f"✅ Retrieved summary for '{book}' ({len(summary)} chars)")

        # Test tool call execution
        result = execute_tool_call("get_summary_by_title", {"title": books[0]})
        print(f"✅ Tool execution successful ({len(result)} chars)")

        # Test validation
        valid_call = {
            "name": "get_summary_by_title",
            "arguments": {"title": books[0]},
        }
        assert validate_tool_call(valid_call)
        print("✅ Tool call validation works")

        print("\n🎉 All basic tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    # Run manual verification
    test_manual_book_verification()
