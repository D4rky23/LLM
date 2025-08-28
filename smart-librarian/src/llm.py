"""LLM integration with OpenAI GPT for Smart Librarian."""

import json
import logging
from typing import List, Dict, Any, Optional

import openai

from .config import config
from .schema import ChatMessage
from .tools import TOOLS_SCHEMA, execute_tool_call, validate_tool_call
from .retriever import get_retriever
from .safety import is_offensive

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = config.OPENAI_API_KEY

# System prompt in Romanian
SYSTEM_PROMPT = """Ești Smart Librarian, un asistent AI care recomandă cărți pe baza preferințelor utilizatorilor. 

Rolul tău:
1. Primești preferințe de lectură și recomanzi o singură carte potrivită
2. Folosești RAG (retriever) pentru a găsi candidatul potrivit din baza de date
3. Răspunzi conversațional în română
4. După ce recomanzi titlul, APELEAZĂ OBLIGATORIU tool-ul `get_summary_by_title` cu titlul exact pentru a afișa rezumatul detaliat

Fluxul de lucru:
1. Analizează cererea utilizatorului
2. Caută în contextul furnizat o carte potrivită
3. Fă o recomandare clară cu titlul exact
4. Apelează automat tool-ul pentru rezumatul detaliat
5. Prezintă rezultatul final

Important:
- Recomandă DOAR o carte pe răspuns
- Folosește titlul EXACT din context pentru tool
- Fii conversațional și prietenos
- Explică de ce cartea recomandată se potrivește cu cererea
- Nu inventezi cărți care nu sunt în context

Dacă mesajul conține limbaj nepotrivit, nu apela LLM; răspunde politicos că preferi să păstrezi conversația într-un limbaj adecvat."""


class SmartLibrarian:
    """OpenAI-powered chatbot for book recommendations."""

    def __init__(self, model: str = None):
        """
        Initialize the Smart Librarian.

        Args:
            model: OpenAI model to use (default from config)
        """
        self.model = model or config.OPENAI_MODEL
        self.retriever = get_retriever()
        self.conversation_history: List[ChatMessage] = []

    def _create_context_message(self, query: str) -> str:
        """
        Create context from retriever results.

        Args:
            query: User query

        Returns:
            Context string with relevant books
        """
        try:
            books = self.retriever.search_books(
                query, top_k=config.DEFAULT_TOP_K
            )

            if not books:
                return "Nu am găsit cărți relevante pentru această căutare în baza de date."

            context_parts = ["Cărți relevante din baza de date:"]

            for i, book in enumerate(books, 1):
                themes_str = ", ".join(book.themes)
                context_parts.append(
                    f"{i}. **{book.title}** - {book.short_summary} (Teme: {themes_str})"
                )

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error creating context: {e}")
            return "Eroare la căutarea în baza de date."

    def _prepare_messages(self, user_query: str) -> List[Dict[str, str]]:
        """
        Prepare messages for OpenAI API call.

        Args:
            user_query: User's query

        Returns:
            List of messages
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in self.conversation_history[-6:]:  # Keep last 6 messages
            messages.append({"role": msg.role, "content": msg.content})

        # Add context from retriever
        context = self._create_context_message(user_query)
        messages.append(
            {
                "role": "system",
                "content": f"Context pentru această căutare:\n{context}",
            }
        )

        # Add user query
        messages.append({"role": "user", "content": user_query})

        return messages

    def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        """
        Handle tool calls from OpenAI response.

        Args:
            tool_calls: List of tool calls

        Returns:
            Tool execution results
        """
        results = []

        for tool_call in tool_calls:
            try:
                # Extract tool information
                function_name = tool_call.get("function", {}).get("name", "")
                function_args = tool_call.get("function", {}).get(
                    "arguments", "{}"
                )

                # Parse arguments
                if isinstance(function_args, str):
                    try:
                        arguments = json.loads(function_args)
                    except json.JSONDecodeError:
                        results.append(
                            f"Eroare la parsarea argumentelor pentru {function_name}"
                        )
                        continue
                else:
                    arguments = function_args

                # Execute tool
                result = execute_tool_call(function_name, arguments)
                results.append(result)

            except Exception as e:
                logger.error(f"Error executing tool call: {e}")
                results.append(f"Eroare la executarea tool-ului: {e}")

        return "\n\n".join(results)

    def chat(self, user_input: str) -> str:
        """
        Process user input and return chatbot response.

        Args:
            user_input: User's message

        Returns:
            Chatbot response
        """
        try:
            # Safety check
            if is_offensive(user_input):
                safety_response = "Aș prefera să păstrăm conversația într-un limbaj adecvat. Poți reformula, te rog?"

                # Add to conversation history
                self.conversation_history.append(
                    ChatMessage(role="user", content=user_input)
                )
                self.conversation_history.append(
                    ChatMessage(role="assistant", content=safety_response)
                )

                return safety_response

            # Prepare messages
            messages = self._prepare_messages(user_input)

            # Make API call
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )

            assistant_message = response.choices[0].message

            # Handle tool calls if present
            final_response = assistant_message.content or ""

            if (
                hasattr(assistant_message, "tool_calls")
                and assistant_message.tool_calls
            ):
                tool_results = self._handle_tool_calls(
                    assistant_message.tool_calls
                )

                if tool_results:
                    # Send tool results back to model for final response
                    follow_up_messages = messages + [
                        {"role": "assistant", "content": final_response},
                        {
                            "role": "system",
                            "content": f"Rezultate tool: {tool_results}",
                        },
                    ]

                    follow_up_response = openai.chat.completions.create(
                        model=self.model,
                        messages=follow_up_messages,
                        temperature=config.TEMPERATURE,
                        max_tokens=config.MAX_TOKENS,
                    )

                    final_response = follow_up_response.choices[
                        0
                    ].message.content

            # Add to conversation history
            self.conversation_history.append(
                ChatMessage(role="user", content=user_input)
            )
            self.conversation_history.append(
                ChatMessage(role="assistant", content=final_response)
            )

            logger.info(f"Generated response for query: {user_input[:50]}...")
            return final_response

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_response = f"Ne pare rău, a apărut o eroare: {e}. Te rog încearcă din nou."

            # Add to conversation history
            self.conversation_history.append(
                ChatMessage(role="user", content=user_input)
            )
            self.conversation_history.append(
                ChatMessage(role="assistant", content=error_response)
            )

            return error_response

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def get_history(self) -> List[ChatMessage]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def set_model(self, model: str):
        """Set OpenAI model."""
        self.model = model
        logger.info(f"Model changed to: {model}")


# Global chatbot instance
_global_chatbot = None


def get_chatbot() -> SmartLibrarian:
    """
    Get the global chatbot instance (singleton pattern).

    Returns:
        SmartLibrarian instance
    """
    global _global_chatbot
    if _global_chatbot is None:
        _global_chatbot = SmartLibrarian()
    return _global_chatbot


def chat_with_librarian(user_input: str) -> str:
    """
    Convenience function for chatting with the librarian.

    Args:
        user_input: User's message

    Returns:
        Chatbot response
    """
    chatbot = get_chatbot()
    return chatbot.chat(user_input)


if __name__ == "__main__":
    # Test LLM functionality
    try:
        librarian = SmartLibrarian()

        # Test queries
        test_queries = [
            "Vreau o carte despre prietenie și magie.",
            "Ce recomanzi pentru cineva care iubește povești de război?",
            "Vreau o carte despre libertate și control social.",
        ]

        for query in test_queries:
            print(f"\nUser: {query}")
            response = librarian.chat(query)
            print(f"Librarian: {response}")
            print("-" * 50)

        # Test history
        history = librarian.get_history()
        print(f"\nConversation history: {len(history)} messages")

    except Exception as e:
        print(f"Error: {e}")
