# Smart Librarian AI - Backend API

API REST pentru aplicația Smart Librarian - sistem inteligent de recomandări de cărți folosind AI.

## 🚀 Caracteristici

- **Chat AI**: Recomandări personalizate de cărți folosind LLM
- **Speech-to-Text**: Transcripția audio în text
- **Text-to-Speech**: Conversia răspunsurilor în audio
- **Generare Imagini**: Creare automată de coperte de cărți
- **Vector Search**: Căutare semantică în baza de date
- **System Monitoring**: Monitorizare status componente
- **File Upload**: Suport pentru upload fișiere audio

## 🛠️ Tech Stack

- **FastAPI** - Framework web modern și rapid
- **Pydantic** - Validare și serializare date
- **CORS Middleware** - Suport cross-origin requests
- **Background Tasks** - Procesare asincronă
- **File Handling** - Upload și procesare fișiere
- **Error Handling** - Tratare robustă a erorilor

## 📁 Structura API

### Chat Endpoints

#### `POST /api/chat`
Trimite un mesaj către AI și primește un răspuns personalizat.

```python
{
    "message": "Recomandă-mi o carte de SF",
    "use_tts": true,
    "generate_image": false
}
```

**Response:**
```python
{
    "response": "Îți recomand '1984' de George Orwell...",
    "audio_url": "/static/audio/response_123.mp3",
    "image_url": "/static/images/cover_123.png"
}
```

#### `DELETE /api/chat/history`
Șterge istoricul conversației curente.

**Response:**
```python
{
    "message": "Chat history cleared successfully"
}
```

### Audio Endpoints

#### `POST /api/transcribe`
Upload și transcripție fișier audio.

```python
# Form data
{
    "file": audio_file,  # .wav, .mp3, .m4a
    "language": "ro"     # optional, default: "ro"
}
```

**Response:**
```python
{
    "transcription": "Recomandă-mi o carte de aventuri"
}
```

#### `POST /api/transcribe/microphone`
Transcripție înregistrare directă de la microfon.

```python
{
    "audio_data": "base64_encoded_audio",
    "duration": 5.0
}
```

### Search Endpoints

#### `GET /api/search`
Căutare semantică în baza de date de cărți.

```python
GET /api/search?query=aventuri&limit=10
```

**Response:**
```python
{
    "results": [
        {
            "title": "Robinson Crusoe",
            "author": "Daniel Defoe",
            "summary": "...",
            "similarity_score": 0.95
        }
    ],
    "total": 25
}
```

#### `GET /api/books`
Lista completă de cărți din baza de date.

**Response:**
```python
{
    "books": [
        {
            "id": "1",
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian Fiction",
            "summary": "..."
        }
    ],
    "total": 150
}
```

### System Endpoints

#### `GET /api/status`
Status în timp real al componentelor sistemului.

**Response:**
```python
{
    "llm": {
        "status": "healthy",
        "response_time": 1.2,
        "last_check": "2024-01-15T10:30:00Z"
    },
    "tts": {
        "status": "healthy",
        "response_time": 0.8
    },
    "stt": {
        "status": "healthy",
        "response_time": 2.1
    },
    "image_gen": {
        "status": "healthy",
        "response_time": 3.5
    },
    "vector_store": {
        "status": "healthy",
        "documents": 150,
        "response_time": 0.3
    },
    "overall_health": 100
}
```

#### `GET /api/system-info`
Informații generale despre sistem.

**Response:**
```python
{
    "version": "1.0.0",
    "uptime": "2 days, 3 hours",
    "memory_usage": "45.2%",
    "cpu_usage": "12.3%",
    "active_connections": 5
}
```

## 🚀 Rulare și Configurare

### Prerequisites
- Python 3.8+
- Dependențele din `requirements.txt`
- Modelele AI configurate (OpenAI, Eleven Labs, etc.)

### Instalare

```bash
# Navighează în directorul backend
cd smart-librarian/backend

# Instalează dependențele
pip install -r requirements.txt

# Configurează variabilele de mediu
cp .env.example .env
# Editează .env cu API keys-urile tale
```

### Pornire Server

```bash
# Development server cu hot reload
python main.py

# Sau cu uvicorn direct
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Server va fi disponibil la http://localhost:8000
```

### Variables de Mediu

```env
# API Keys
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
HUGGINGFACE_API_KEY=...

# Configurare
DEBUG=true
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database
VECTOR_STORE_PATH=./data/vector_store
BOOKS_DATA_PATH=./data/book_summaries.json
```

## 📝 Integrare cu Python Modules

API-ul integrează următoarele module Python existente:

### `src/ai/llm.py`
- Chat completions cu OpenAI GPT
- Streaming responses pentru UI în timp real
- Context management pentru conversații

### `src/tts.py`
- Text-to-Speech cu Eleven Labs
- Generare fișiere audio MP3
- Voice cloning și personalizare

### `src/stt.py`
- Speech-to-Text cu Whisper
- Suport multiple formate audio
- Detectare automată limbă

### `src/image_gen.py`
- Generare imagini cu DALL-E sau Stable Diffusion
- Creare coperte de cărți personalizate
- Optimizare pentru format și calitate

### `src/vector/vector_store.py`
- Embedding-uri pentru căutare semantică
- Vector database cu Chroma/Pinecone
- Similarity search optimizat

## 🔧 Configurare CORS

API-ul este configurat pentru cross-origin requests:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "https://smart-librarian.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring și Logging

### Health Checks
- Endpoint `/api/status` pentru monitoring
- Verificări automate ale componentelor
- Alerting pentru servicii down

### Logging
```python
import logging

# Configurare centralizată
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics
- Response times pentru fiecare endpoint
- Error rates și status codes
- Resource usage (CPU, memory)

## 🛡️ Security și Best Practices

### Validare Input
- Pydantic models pentru request validation
- File type checking pentru uploads
- Rate limiting pentru API calls

### Error Handling
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### File Uploads
- Size limits pentru fișiere audio
- Validare extensii și MIME types
- Cleanup automat fișiere temporare

## 🚀 Deploy în Producție

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Production settings
export DEBUG=false
export LOG_LEVEL=warning
export CORS_ORIGINS=https://yourdomain.com
```

## 📖 API Documentation

### Swagger UI
Documentația interactivă este disponibilă la:
- Development: http://localhost:8000/docs
- Alternative: http://localhost:8000/redoc

### OpenAPI Schema
Schema completă JSON disponibilă la:
- http://localhost:8000/openapi.json

## 🤝 Contribuții

1. Fork repository-ul
2. Creează un branch nou (`git checkout -b feature/api-enhancement`)
3. Commit schimbările (`git commit -m 'Add new endpoint'`)
4. Push la branch (`git push origin feature/api-enhancement`)
5. Deschide un Pull Request

## 📄 Licență

MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

---

Dezvoltat cu ❤️ folosind FastAPI și Python moderne.