"""FastAPI backend for Smart Librarian React frontend."""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import uuid
import asyncio
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import config
from ai.llm import get_chatbot
from vector.vector_store import initialize_vector_store
from core.data_loader import load_books_data
from tts import speak, is_tts_available
from stt import transcribe, is_stt_available
from image_gen import generate_cover, is_image_generation_available
from core.retriever import get_retriever

# Initialize FastAPI app
app = FastAPI(
    title="Smart Librarian API",
    description="RESTful API for Smart Librarian AI book recommendation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated content
app.mount(
    "/static", StaticFiles(directory=str(config.OUTPUT_DIR)), name="static"
)

# Initialize global components
chatbot = None
retriever = None


# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    use_tts: bool = False
    use_image: bool = False


class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    timestamp: str


class SystemStatus(BaseModel):
    config: bool
    data: bool
    vector_store: bool
    chatbot: bool
    tts: bool
    stt: bool
    image_gen: bool
    errors: Dict[str, str] = {}


class TranscriptionRequest(BaseModel):
    method: str = "whisper"
    duration: int = 5


class TranscriptionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None


class BookRecommendation(BaseModel):
    title: str
    short_summary: str
    themes: List[str]
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    books: List[BookRecommendation]
    total_found: int


class SystemInfo(BaseModel):
    total_books: int
    vector_store_stats: Dict[str, Any]
    available_features: List[str]


# Global session storage (in production, use Redis or database)
chat_sessions: Dict[str, List[ChatMessage]] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global chatbot, retriever

    try:
        # Initialize retriever and chatbot
        retriever = get_retriever()
        chatbot = get_chatbot()
        print("✅ Smart Librarian API initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing API: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Smart Librarian API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get system component status."""
    status = SystemStatus(
        config=False,
        data=False,
        vector_store=False,
        chatbot=False,
        tts=False,
        stt=False,
        image_gen=False,
        errors={},
    )

    # Check configuration
    try:
        config.validate()
        status.config = True
    except Exception as e:
        status.errors["config"] = str(e)

    # Check data
    try:
        books, _ = load_books_data()
        status.data = len(books) > 0
    except Exception as e:
        status.errors["data"] = str(e)

    # Check vector store
    try:
        if retriever:
            stats = retriever.get_retriever_stats()
            status.vector_store = stats["total_books_in_cache"] > 0
    except Exception as e:
        status.errors["vector_store"] = str(e)

    # Check chatbot
    status.chatbot = chatbot is not None

    # Check optional features
    status.tts = is_tts_available()["any_available"]
    status.stt = is_stt_available()["any_available"]
    status.image_gen = is_image_generation_available()

    return status


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with Smart Librarian AI."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        # Get AI response
        ai_response = chatbot.chat(request.message)

        response = ChatResponse(
            response=ai_response, timestamp=datetime.now().isoformat()
        )

        # Generate TTS if requested (synchronously to include URL in response)
        if request.use_tts and is_tts_available()["any_available"]:
            try:
                audio_path = speak(ai_response)
                if audio_path and audio_path.exists():
                    response.audio_url = f"/static/{audio_path.name}"
            except Exception as e:
                print(f"TTS generation error: {e}")

        # Generate image if requested (synchronously to include URL in response)
        if request.use_image and is_image_generation_available():
            try:
                if (
                    "recommend" in ai_response.lower()
                    or "book" in ai_response.lower()
                ):
                    # Extract book info from response (simplified)
                    book_title = "Recommended Book"
                    book_themes = ["literature", "fiction"]

                    image_path = generate_cover(book_title, book_themes)
                    if image_path and image_path.exists():
                        response.image_url = f"/static/{image_path.name}"
            except Exception as e:
                print(f"Image generation error: {e}")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file."""
    if not is_stt_available()["any_available"]:
        raise HTTPException(
            status_code=400, detail="Speech-to-text not available"
        )

    try:
        # Save uploaded file temporarily
        temp_path = (
            config.OUTPUT_DIR
            / f"temp_audio_{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        )

        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Transcribe
        transcribed_text = transcribe(str(temp_path), method="whisper")

        # Clean up
        temp_path.unlink(missing_ok=True)

        if transcribed_text:
            return TranscriptionResponse(text=transcribed_text)
        else:
            raise HTTPException(
                status_code=400, detail="Could not transcribe audio"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Transcription error: {str(e)}"
        )


@app.post("/api/transcribe/microphone", response_model=TranscriptionResponse)
async def transcribe_microphone(request: TranscriptionRequest):
    """Transcribe from microphone."""
    if not is_stt_available()["any_available"]:
        raise HTTPException(
            status_code=400, detail="Speech-to-text not available"
        )

    try:
        transcribed_text = transcribe("microphone", duration=request.duration)

        if transcribed_text:
            return TranscriptionResponse(text=transcribed_text)
        else:
            raise HTTPException(
                status_code=400, detail="Could not recognize speech"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Microphone transcription error: {str(e)}"
        )


@app.get("/api/search", response_model=SearchResponse)
async def search_books(query: str, top_k: int = 5):
    """Search books by query."""
    if not retriever:
        raise HTTPException(status_code=500, detail="Search not available")

    try:
        books_with_scores = retriever.search_with_scores(query, top_k=top_k)

        books = []
        for book, score in books_with_scores:
            books.append(
                BookRecommendation(
                    title=book.title,
                    short_summary=book.short_summary,
                    themes=book.themes,
                    score=score,
                )
            )

        return SearchResponse(query=query, books=books, total_found=len(books))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/books")
async def get_all_books():
    """Get list of all available books."""
    try:
        books, _ = load_books_data()
        return {"books": [book.title for book in books], "total": len(books)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading books: {str(e)}"
        )


@app.get("/api/book/{title}")
async def get_book_by_title(title: str):
    """Get detailed information about a specific book."""
    try:
        books, _ = load_books_data()
        book = next(
            (b for b in books if b.title.lower() == title.lower()), None
        )

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        return {
            "title": book.title,
            "short_summary": book.short_summary,
            "full_summary": getattr(book, "full_summary", book.short_summary),
            "themes": book.themes,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving book: {str(e)}"
        )


@app.get("/api/system-info", response_model=SystemInfo)
async def get_system_info():
    """Get detailed system information."""
    try:
        books, _ = load_books_data()

        system_info = SystemInfo(
            total_books=len(books),
            vector_store_stats={},
            available_features=[],
        )

        # Get vector store stats
        if retriever:
            system_info.vector_store_stats = retriever.get_retriever_stats()

        # Check available features
        if is_tts_available()["any_available"]:
            system_info.available_features.append("text-to-speech")
        if is_stt_available()["any_available"]:
            system_info.available_features.append("speech-to-text")
        if is_image_generation_available():
            system_info.available_features.append("image-generation")

        return system_info

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting system info: {str(e)}"
        )


@app.delete("/api/chat/history")
async def clear_chat_history():
    """Clear chat history."""
    try:
        if chatbot:
            chatbot.clear_history()
        chat_sessions.clear()
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error clearing history: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
