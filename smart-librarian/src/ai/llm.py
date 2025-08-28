"""LLM integration for Smart Librarian (moved into ai package)."""

from typing import List, Dict, Any
import json
from openai import OpenAI

from core.config import config
from core.schema import ChatMessage
from ai.tools import get_summary_by_title, get_available_books
from core.retriever import get_retriever


class SmartLibrarian:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.conversation_history = []
        self.retriever = get_retriever()

        # Define available functions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_available_books",
                    "description": "Get the list of all available book titles in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_summary_by_title",
                    "description": "Get detailed summary for a specific book by its title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The exact title of the book",
                            }
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_books",
                    "description": "Search for books in the database using semantic search based on themes, concepts, or descriptions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query describing themes, genres, or concepts (e.g., 'friendship and magic', 'dystopian future', 'war stories')",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of books to return (default: 3)",
                                "default": 3,
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

    def _call_function(
        self, function_name: str, arguments: Dict[str, Any]
    ) -> str:
        """Execute the requested function and return results."""
        try:
            if function_name == "get_available_books":
                books = get_available_books()
                return f"Available books in database: {', '.join(books)}"

            elif function_name == "get_summary_by_title":
                title = arguments.get("title", "")
                summary = get_summary_by_title(title)
                if summary:
                    return f"Summary for '{title}':\n{summary}"
                else:
                    return f"No summary found for '{title}'. Available books are: {', '.join(get_available_books())}"

            elif function_name == "search_books":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 3)
                results = self.retriever.search_books(query, top_k=top_k)

                if results:
                    search_results = []
                    for book in results:
                        search_results.append(
                            f"**{book.title}** - {book.short_summary} (Themes: {', '.join(book.themes)})"
                        )
                    return (
                        f"Found {len(results)} books matching '{query}':\n"
                        + "\n\n".join(search_results)
                    )
                else:
                    return f"No books found matching '{query}'. Available books: {', '.join(get_available_books())}"

            else:
                return f"Unknown function: {function_name}"

        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"

    def chat(self, user_input: str) -> str:
        """Chat with function calling support."""
        # Add user message to history
        self.conversation_history.append(
            {"role": "user", "content": user_input}
        )

        # System message
        system_message = {
            "role": "system",
            "content": """You are Smart Librarian, a professional AI assistant specialized in book recommendations. You have access to a curated database of classic books and can search and provide detailed information about them.

Your capabilities:
- Search books by themes, concepts, or genres using the search_books function
- Get the complete list of available books using get_available_books function  
- Provide detailed summaries for specific books using get_summary_by_title function

Always use your functions to provide accurate information from the database. When users ask about books, search the database first. Be helpful, professional, and provide specific recommendations with explanations.""",
        }

        # Prepare messages for API call
        messages = [system_message] + self.conversation_history[
            -10:
        ]  # Keep last 10 messages for context

        # First API call with function calling
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=config.TEMPERATURE,
        )

        response_message = response.choices[0].message

        # Check if function calling is needed
        if response_message.tool_calls:
            # Add assistant's response to conversation
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in response_message.tool_calls
                    ],
                }
            )

            # Execute function calls
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                function_result = self._call_function(function_name, arguments)

                # Add function result to conversation
                self.conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result,
                    }
                )

            # Second API call to generate final response
            final_response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[system_message]
                + self.conversation_history[-15:],  # Include function results
                temperature=config.TEMPERATURE,
            )

            assistant_content = final_response.choices[0].message.content
        else:
            assistant_content = response_message.content

        # Add final response to history
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_content}
        )

        return assistant_content

    def get_history(self) -> List[ChatMessage]:
        """Get conversation history."""
        history = []
        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                history.append(
                    ChatMessage(role=msg["role"], content=msg["content"])
                )
        return history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


_global_chatbot = None


def get_chatbot() -> SmartLibrarian:
    global _global_chatbot
    if _global_chatbot is None:
        _global_chatbot = SmartLibrarian()
    return _global_chatbot
