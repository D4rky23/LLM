"""Command Line Interface for Smart Librarian using Typer."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from llm import get_chatbot
from vector_store import initialize_vector_store
from data_loader import load_books_data, validate_data_consistency
from tts import speak, is_tts_available
from stt import transcribe, is_stt_available
from image_gen import generate_cover, is_image_generation_available

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Typer app
app = typer.Typer(
    name="Smart Librarian",
    help="AI chatbot pentru recomandări de cărți cu RAG și tool calling.",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()


@app.command()
def ingest(
    force: bool = typer.Option(
        False, "--force", "-f", help="Forțează reconstruirea bazei de date"
    )
):
    """Inițializează baza de date vectorială cu cărțile din fișierele de date."""
    console.print("[bold blue]🔄 Inițializare Smart Librarian...[/bold blue]")

    try:
        # Validate configuration
        config.validate()
        console.print("✅ Configurare validă")

        # Validate data consistency
        validate_data_consistency()
        console.print("✅ Consistența datelor verificată")

        # Load books data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Încărcare date cărți...", total=None)

            books, summaries = load_books_data()
            console.print(f"✅ Încărcate {len(books)} cărți")

            # Initialize vector store
            progress.update(task, description="Inițializare vector store...")
            vector_store = initialize_vector_store(books, force_rebuild=force)

            stats = vector_store.get_collection_stats()
            console.print(
                f"✅ Vector store inițializat cu {stats['total_books']} cărți"
            )

        console.print(
            Panel(
                "[bold green]Inițializare completă![/bold green]\n"
                f"📚 Cărți disponibile: {len(books)}\n"
                f"🔍 Vector store: {stats['total_books']} embeddings\n"
                f"📁 Director persistență: {stats['persist_directory']}",
                title="Status",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[bold red]❌ Eroare la inițializare: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def chat(
    tts: bool = typer.Option(False, "--tts", help="Activează text-to-speech"),
    voice: bool = typer.Option(
        False, "--voice", help="Activează speech-to-text"
    ),
    image: bool = typer.Option(
        False, "--image", help="Generează imagini pentru cărți"
    ),
    history: bool = typer.Option(
        False, "--history", help="Afișează istoricul conversației"
    ),
):
    """Pornește chat-ul interactiv cu Smart Librarian."""

    # Check optional features availability
    features_status = {
        "TTS": is_tts_available()["any_available"] if tts else False,
        "STT": is_stt_available()["any_available"] if voice else False,
        "Image Gen": is_image_generation_available() if image else False,
    }

    # Display welcome message
    welcome_text = Text()
    welcome_text.append("🤖 ", style="bold blue")
    welcome_text.append("Bun venit la Smart Librarian!", style="bold")

    features_text = []
    for feature, available in features_status.items():
        if available:
            features_text.append(f"✅ {feature}")
        elif (
            feature in ["TTS", "STT", "Image Gen"]
            and locals()[feature.lower().replace(" gen", "").replace(" ", "_")]
        ):
            features_text.append(f"❌ {feature} (indisponibil)")

    if features_text:
        welcome_text.append(f"\nFuncții activate: {', '.join(features_text)}")

    console.print(
        Panel(welcome_text, title="Smart Librarian", border_style="blue")
    )

    # Initialize chatbot
    try:
        chatbot = get_chatbot()
        console.print("✅ Chatbot inițializat cu succes")
    except Exception as e:
        console.print(
            f"[bold red]❌ Eroare la inițializarea chatbot-ului: {e}[/bold red]"
        )
        raise typer.Exit(1)

    # Show sample queries
    console.print("\n[bold]Exemple de întrebări:[/bold]")
    sample_queries = [
        "Vreau o carte despre prietenie și magie.",
        "Ce recomanzi pentru cineva care iubește povești de război?",
        "Vreau o carte despre libertate și control social.",
        "Ce este 1984?",
    ]

    for i, query in enumerate(sample_queries, 1):
        console.print(f"  {i}. [italic]{query}[/italic]")

    console.print(
        "\n[dim]Tastează 'exit', 'quit' sau 'ieșire' pentru a ieși.[/dim]"
    )
    console.print(
        "[dim]Tastează 'clear' sau 'șterge' pentru a șterge istoricul.[/dim]"
    )

    if history:
        console.print(
            "[dim]Tastează 'history' sau 'istoric' pentru a afișa istoricul.[/dim]"
        )

    # Main chat loop
    while True:
        try:
            # Get user input
            if voice and features_status["STT"]:
                console.print(
                    "\n[yellow]🎤 Vorbește acum (5 secunde)...[/yellow]"
                )
                user_input = transcribe("microphone", duration=5)
                if user_input:
                    console.print(f"[dim]Recunoscut: {user_input}[/dim]")
                else:
                    console.print(
                        "[red]❌ Nu am putut recunoaște vocea. Încearcă din nou.[/red]"
                    )
                    continue
            else:
                user_input = Prompt.ask("\n[bold]Întrebare")

            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "ieșire", "q"]:
                console.print("[yellow]👋 La revedere![/yellow]")
                break

            # Check for clear command
            if user_input.lower() in ["clear", "șterge"]:
                chatbot.clear_history()
                console.print("[green]✅ Istoric șters.[/green]")
                continue

            # Check for history command
            if history and user_input.lower() in ["history", "istoric"]:
                chat_history = chatbot.get_history()
                if chat_history:
                    console.print("\n[bold]Istoricul conversației:[/bold]")
                    for msg in chat_history[-10:]:  # Show last 10 messages
                        role_emoji = "👤" if msg.role == "user" else "🤖"
                        console.print(
                            f"{role_emoji} [bold]{msg.role}:[/bold] {msg.content[:100]}..."
                        )
                else:
                    console.print("[dim]Istoricul este gol.[/dim]")
                continue

            # Process with chatbot
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Procesare răspuns...", total=None)

                response = chatbot.chat(user_input)

            # Display response
            console.print(
                Panel(
                    response, title="🤖 Smart Librarian", border_style="green"
                )
            )

            # Text-to-speech if enabled
            if tts and features_status["TTS"]:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Generare audio...", total=None)

                    audio_path = speak(response)
                    if audio_path:
                        console.print(
                            f"[green]🔊 Audio salvat: {audio_path}[/green]"
                        )
                    else:
                        console.print(
                            "[red]❌ Eroare la generarea audio[/red]"
                        )

            # Image generation if enabled and response contains book recommendation
            if image and features_status["Image Gen"]:
                # Simple check if response contains a book title
                # This is a basic implementation - could be improved with NLP
                if (
                    "recomand" in response.lower()
                    or "carte" in response.lower()
                ):
                    try:
                        # Extract book title (basic approach)
                        # You might want to improve this with proper parsing
                        console.print(
                            "[yellow]🎨 Generare imagine...[/yellow]"
                        )

                        # For now, use a default approach
                        # In practice, you'd extract the actual recommended book
                        sample_title = "Cartea Recomandată"
                        sample_themes = ["aventură", "prietenie"]

                        image_path = generate_cover(
                            sample_title, sample_themes
                        )
                        if image_path:
                            console.print(
                                f"[green]🖼️ Imagine salvată: {image_path}[/green]"
                            )
                        else:
                            console.print(
                                "[red]❌ Eroare la generarea imaginii[/red]"
                            )
                    except Exception as e:
                        console.print(
                            f"[red]❌ Eroare la generarea imaginii: {e}[/red]"
                        )

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 La revedere![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Eroare: {e}[/red]")
            continue


@app.command()
def status():
    """Afișează statusul sistemului și disponibilitatea funcțiilor."""
    console.print("[bold blue]📊 Status Smart Librarian[/bold blue]")

    # Check configuration
    try:
        config.validate()
        config_status = "✅ Valid"
    except Exception as e:
        config_status = f"❌ Eroare: {e}"

    # Check data
    try:
        validate_data_consistency()
        books, _ = load_books_data()
        data_status = f"✅ {len(books)} cărți încărcate"
    except Exception as e:
        data_status = f"❌ Eroare: {e}"

    # Check vector store
    try:
        from vector_store import VectorStore

        vs = VectorStore()
        stats = vs.get_collection_stats()
        vector_status = f"✅ {stats['total_books']} embeddings"
    except Exception as e:
        vector_status = f"❌ Eroare: {e}"

    # Check optional features
    tts_status = (
        "✅ Disponibil"
        if is_tts_available()["any_available"]
        else "❌ Indisponibil"
    )
    stt_status = (
        "✅ Disponibil"
        if is_stt_available()["any_available"]
        else "❌ Indisponibil"
    )
    img_status = (
        "✅ Disponibil"
        if is_image_generation_available()
        else "❌ Indisponibil"
    )

    status_panel = f"""[bold]Core Components:[/bold]
📋 Configurare: {config_status}
📚 Date: {data_status}
🔍 Vector Store: {vector_status}

[bold]Optional Features:[/bold]
🔊 Text-to-Speech: {tts_status}
🎤 Speech-to-Text: {stt_status}
🖼️ Image Generation: {img_status}

[bold]Paths:[/bold]
📁 Proiect: {config.PROJECT_ROOT}
📁 Date: {config.DATA_DIR}
📁 Output: {config.OUTPUT_DIR}
📁 ChromaDB: {config.CHROMA_PERSIST_DIR}"""

    console.print(
        Panel(status_panel, title="System Status", border_style="blue")
    )


@app.command()
def test():
    """Rulează teste pentru componentele sistemului."""
    console.print("[bold blue]🧪 Rulare teste Smart Librarian[/bold blue]")

    tests_passed = 0
    tests_total = 0

    # Test data loading
    console.print("\n[bold]Test 1: Încărcare date[/bold]")
    tests_total += 1
    try:
        validate_data_consistency()
        books, summaries = load_books_data()
        console.print(f"✅ {len(books)} cărți încărcate cu succes")
        tests_passed += 1
    except Exception as e:
        console.print(f"❌ Eroare: {e}")

    # Test vector store
    console.print("\n[bold]Test 2: Vector Store[/bold]")
    tests_total += 1
    try:
        from retriever import get_retriever

        retriever = get_retriever()
        results = retriever.search_books("prietenie și magie", top_k=2)
        console.print(f"✅ Vector store funcțional ({len(results)} rezultate)")
        tests_passed += 1
    except Exception as e:
        console.print(f"❌ Eroare: {e}")

    # Test tools
    console.print("\n[bold]Test 3: Tools[/bold]")
    tests_total += 1
    try:
        from tools import get_summary_by_title, get_available_books

        books_list = get_available_books()
        if books_list:
            sample_summary = get_summary_by_title(books_list[0])
            console.print(f"✅ Tools funcționale ({len(books_list)} cărți)")
            tests_passed += 1
        else:
            console.print("❌ Nu există cărți disponibile")
    except Exception as e:
        console.print(f"❌ Eroare: {e}")

    # Test safety filter
    console.print("\n[bold]Test 4: Safety Filter[/bold]")
    tests_total += 1
    try:
        from safety import is_offensive, validate_safety_filter

        if validate_safety_filter():
            console.print("✅ Safety filter funcțional")
            tests_passed += 1
        else:
            console.print("❌ Safety filter test failed")
    except Exception as e:
        console.print(f"❌ Eroare: {e}")

    # Summary
    console.print(
        f"\n[bold]Rezultate teste: {tests_passed}/{tests_total}[/bold]"
    )

    if tests_passed == tests_total:
        console.print(
            Panel(
                "[bold green]🎉 Toate testele au trecut cu succes![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold yellow]⚠️ {tests_total - tests_passed} teste au eșuat[/bold yellow]",
                border_style="yellow",
            )
        )


if __name__ == "__main__":
    app()
