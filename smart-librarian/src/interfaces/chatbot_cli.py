"""Command Line Interface for Smart Librarian using Typer (moved into interfaces)."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from core.config import config
from ai.llm import get_chatbot
from vector.vector_store import initialize_vector_store
from core.data_loader import load_books_data, validate_data_consistency
from tts import speak, is_tts_available
from stt import transcribe, is_stt_available
from image_gen import generate_cover, is_image_generation_available

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Typer app
app = typer.Typer(
    name="Smart Librarian",
    help="Professional AI chatbot for book recommendations with RAG and tool calling.",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()


@app.command()
def ingest(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force rebuild of the database"
    )
):
    """Initialize the vector database with books from data files."""
    console.print(
        "[bold blue][INIT] Initializing Smart Librarian...[/bold blue]"
    )

    try:
        # Validate configuration
        config.validate()
        console.print("[CHECK] Configuration valid")

        # Validate data consistency
        validate_data_consistency()
        console.print("✅ Data consistency verified")

        # Load books data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading book data...", total=None)

            books, summaries = load_books_data()
            console.print(f"[CHECK] Loaded {len(books)} books")

            # Initialize vector store
            progress.update(task, description="Initializing vector store...")
            vector_store = initialize_vector_store(books, force_rebuild=force)

            stats = vector_store.get_collection_stats()
            console.print(
                f"[SUCCESS] Vector store initialized with {stats['total_books']} books"
            )

        console.print(
            Panel(
                "[bold green]Initialization complete![/bold green]\n"
                f"[BOOKS] Available books: {len(books)}\n"
                f"[SEARCH] Vector store: {stats['total_books']} embeddings\n"
                f"[DATA] Persistence directory: {stats['persist_directory']}",
                title="Status",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(
            f"[bold red][ERROR] Initialization failed: {e}[/bold red]"
        )
        raise typer.Exit(1)


@app.command()
def chat(
    tts: bool = typer.Option(False, "--tts", help="Enable text-to-speech"),
    voice: bool = typer.Option(False, "--voice", help="Enable speech-to-text"),
    image: bool = typer.Option(
        False, "--image", help="Generate images for books"
    ),
    history: bool = typer.Option(
        False, "--history", help="Show conversation history"
    ),
):
    """Start interactive chat with Smart Librarian."""

    # Check optional features availability
    features_status = {
        "TTS": is_tts_available()["any_available"] if tts else False,
        "STT": is_stt_available()["any_available"] if voice else False,
        "Image Gen": is_image_generation_available() if image else False,
    }

    # Display welcome message
    welcome_text = Text()
    welcome_text.append("Welcome to Smart Librarian!", style="bold")

    features_text = []
    for feature, available in features_status.items():
        if available:
            features_text.append(f"✅ {feature}")
        elif feature == "TTS" and tts:
            features_text.append(f"❌ {feature} (unavailable)")
        elif feature == "STT" and voice:
            features_text.append(f"❌ {feature} (unavailable)")
        elif feature == "Image Gen" and image:
            features_text.append(f"❌ {feature} (unavailable)")

    if features_text:
        welcome_text.append(f"\nEnabled features: {', '.join(features_text)}")

    console.print(
        Panel(welcome_text, title="Smart Librarian", border_style="blue")
    )

    # Initialize chatbot
    try:
        chatbot = get_chatbot()
        console.print("[SUCCESS] Chatbot initialized successfully")
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Chatbot initialization failed: {e}[/bold red]"
        )
        raise typer.Exit(1)

    # Show sample queries
    console.print("\n[bold]Example questions:[/bold]")
    sample_queries = [
        "I want a book about friendship and magic.",
        "What do you recommend for someone who loves war stories?",
        "I want a book about freedom and social control.",
        "What is 1984 about?",
    ]

    for i, query in enumerate(sample_queries, 1):
        console.print(f"  {i}. [italic]{query}[/italic]")

    console.print("\n[dim]Type 'exit', 'quit' to exit.[/dim]")
    console.print("[dim]Type 'clear' to clear history.[/dim]")

    if history:
        console.print(
            "[dim]Type 'history' to show conversation history.[/dim]"
        )

    # Main chat loop
    while True:
        try:
            # Get user input
            if voice and features_status["STT"]:
                console.print(
                    "\n[yellow][VOICE] Speak now (5 seconds)...[/yellow]"
                )
                user_input = transcribe("microphone", duration=5)
                if user_input:
                    console.print(f"[dim]Recognized: {user_input}[/dim]")
                else:
                    console.print(
                        "[red][ERROR] Could not recognize speech. Try again.[/red]"
                    )
                    continue
            else:
                user_input = Prompt.ask("\n[bold]Question")

            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow][GOODBYE] Goodbye![/yellow]")
                break

            # Check for clear command
            if user_input.lower() in ["clear"]:
                chatbot.clear_history()
                console.print("[green]✅ History cleared.[/green]")
                continue

            # Check for history command
            if history and user_input.lower() in ["history", "istoric"]:
                chat_history = chatbot.get_history()
                if chat_history:
                    console.print("\n[bold]Conversation History:[/bold]")
                    for msg in chat_history[-10:]:  # Show last 10 messages
                        role_icon = (
                            "User" if msg.role == "user" else "Assistant"
                        )
                        console.print(
                            f"[bold]{role_icon}:[/bold] {msg.content[:100]}..."
                        )
                else:
                    console.print("[dim]History is empty.[/dim]")
                continue

            # Process with chatbot
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Processing response...", total=None)

                response = chatbot.chat(user_input)

            # Display response
            console.print(
                Panel(response, title="Smart Librarian", border_style="green")
            )

            # Text-to-speech if enabled
            if tts and features_status["TTS"]:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Generating audio...", total=None)

                    audio_path = speak(response)
                    if audio_path:
                        console.print(
                            f"[green]Audio saved: {audio_path}[/green]"
                        )
                    else:
                        console.print("[red]Error generating audio[/red]")

            # Image generation if enabled and response contains book recommendation
            if image and features_status["Image Gen"]:
                # Simple check if response contains a book title
                # This is a basic implementation - could be improved with NLP
                if (
                    "recommend" in response.lower()
                    or "book" in response.lower()
                ):
                    try:
                        # Extract book title (basic approach)
                        # You might want to improve this with proper parsing
                        console.print("[yellow]Generating image...[/yellow]")

                        # For now, use a default approach
                        # In practice, you'd extract the actual recommended book
                        sample_title = "Recommended Book"
                        sample_themes = ["adventure", "friendship"]

                        image_path = generate_cover(
                            sample_title, sample_themes
                        )
                        if image_path:
                            console.print(
                                f"[green]Image saved: {image_path}[/green]"
                            )
                        else:
                            console.print("[red]Error generating image[/red]")
                    except Exception as e:
                        console.print(
                            f"[red]Error generating image: {e}[/red]"
                        )

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue


@app.command()
def status():
    """Display system status and feature availability."""
    console.print("[bold blue]Smart Librarian Status[/bold blue]")

    # Check configuration
    try:
        config.validate()
        config_status = "✅ Valid"
    except Exception as e:
        config_status = f"❌ Error: {e}"

    # Check data
    try:
        validate_data_consistency()
        books, _ = load_books_data()
        data_status = f"✅ {len(books)} books loaded"
    except Exception as e:
        data_status = f"❌ Error: {e}"

    # Check vector store
    try:
        from vector.vector_store import VectorStore

        vs = VectorStore()
        stats = vs.get_collection_stats()
        vector_status = f"✅ {stats['total_books']} embeddings"
    except Exception as e:
        vector_status = f"❌ Error: {e}"

    # Check optional features
    tts_status = (
        "✅ Available"
        if is_tts_available()["any_available"]
        else "❌ Unavailable"
    )
    stt_status = (
        "✅ Available"
        if is_stt_available()["any_available"]
        else "❌ Unavailable"
    )
    img_status = (
        "✅ Available" if is_image_generation_available() else "❌ Unavailable"
    )

    status_panel = f"""[bold]Core Components:[/bold]
Configuration: {config_status}
Data: {data_status}
Vector Store: {vector_status}

[bold]Optional Features:[/bold]
Text-to-Speech: {tts_status}
Speech-to-Text: {stt_status}
Image Generation: {img_status}

[bold]Paths:[/bold]
Project: {config.PROJECT_ROOT}
Data: {config.DATA_DIR}
Output: {config.OUTPUT_DIR}
ChromaDB: {config.CHROMA_PERSIST_DIR}"""

    console.print(
        Panel(status_panel, title="System Status", border_style="blue")
    )


@app.command()
def test():
    """Run tests for system components."""
    console.print("[bold blue]Running Smart Librarian Tests[/bold blue]")

    tests_passed = 0
    tests_total = 0

    # Test data loading
    console.print("\n[bold]Test 1: Data Loading[/bold]")
    tests_total += 1
    try:
        validate_data_consistency()
        books, summaries = load_books_data()
        console.print(f"✅ {len(books)} books loaded successfully")
        tests_passed += 1
    except Exception as e:
        console.print(f"❌ Error: {e}")

    # Test vector store
    console.print("\n[bold]Test 2: Vector Store[/bold]")
    tests_total += 1
    try:
        from core.retriever import get_retriever

        retriever = get_retriever()
        results = retriever.search_books("friendship and magic", top_k=2)
        console.print(f"✅ Vector store functional ({len(results)} results)")
        tests_passed += 1
    except Exception as e:
        console.print(f"❌ Error: {e}")

    # Test tools
    console.print("\n[bold]Test 3: Tools[/bold]")
    tests_total += 1
    try:
        from ai.tools import get_summary_by_title, get_available_books

        books_list = get_available_books()
        if books_list:
            sample_summary = get_summary_by_title(books_list[0])
            console.print(f"✅ Tools functional ({len(books_list)} books)")
            tests_passed += 1
        else:
            console.print("❌ No books available")
    except Exception as e:
        console.print(f"❌ Error: {e}")

    # Test safety filter
    console.print("\n[bold]Test 4: Safety Filter[/bold]")
    tests_total += 1
    try:
        from safety import is_offensive, validate_safety_filter

        if validate_safety_filter():
            console.print("✅ Safety filter functional")
            tests_passed += 1
        else:
            console.print("❌ Safety filter test failed")
    except Exception as e:
        console.print(f"❌ Error: {e}")

    # Summary
    console.print(f"\n[bold]Test Results: {tests_passed}/{tests_total}[/bold]")

    if tests_passed == tests_total:
        console.print(
            Panel(
                "[bold green]All tests passed successfully![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold yellow]{tests_total - tests_passed} tests failed[/bold yellow]",
                border_style="yellow",
            )
        )


if __name__ == "__main__":
    app()
