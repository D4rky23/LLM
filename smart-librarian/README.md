# Smart Librarian – RAG + Tool Completion

Un chatbot AI inteligent care recomandă cărți pe baza preferințelor utilizatorilor și afișează automat rezumate detaliate folosind **OpenAI GPT** pentru conversație și **ChromaDB** pentru căutare semantică.

## 🚀 Caracteristici

- **Recomandări inteligente de cărți** folosind RAG (Retrieval-Augmented Generation)
- **Tool calling automat** pentru rezumate detaliate
- **Răspunsuri în română** cu sistem de siguranță integrat
- **Interfață CLI** cu Typer și Rich
- **Interfață web** cu Streamlit (opțional)
- **Text-to-Speech** pentru răspunsuri audio (opțional)
- **Speech-to-Text** pentru input vocal (opțional)
- **Generare imagini** pentru coperți de cărți (opțional)
- **Vector store local** cu ChromaDB (persistat local)

## 📚 Dataset

Proiectul include un dataset cu **12 cărți clasice** cu rezumate în română:
- 1984 (George Orwell)
- The Hobbit (J.R.R. Tolkien)
- Dune (Frank Herbert)
- To Kill a Mockingbird (Harper Lee)
- The Catcher in the Rye (J.D. Salinger)
- The Lord of the Rings (J.R.R. Tolkien)
- Pride and Prejudice (Jane Austen)
- The Name of the Wind (Patrick Rothfuss)
- The Book Thief (Markus Zusak)
- The Kite Runner (Khaled Hosseini)
- Brave New World (Aldous Huxley)
- Fahrenheit 451 (Ray Bradbury)

## 🛠️ Arhitectură

```
User Input → Safety Filter → RAG Retriever → LLM (GPT) → Tool Calling → Final Response
                ↓              ↓              ↓           ↓
            Offensive      ChromaDB       OpenAI API   get_summary_by_title()
            Detection      Embeddings     + Tools      + JSON Database
```

### Componente principale:

1. **Safety Filter** - Filtrează limbajul ofensiv
2. **RAG Retriever** - Căutare semantică în ChromaDB
3. **LLM Integration** - OpenAI GPT cu function calling
4. **Tools** - Funcție pentru rezumate detaliate
5. **UI Interfaces** - CLI (Typer) și Web (Streamlit)

## 📦 Instalare

### 1. Clonează proiectul

```bash
git clone <repository-url>
cd smart-librarian
```

### 2. Creează mediul virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalează dependențele

```bash
pip install -r requirements.txt
```

### 4. Configurează mediul

```bash
# Copiază fișierul de exemplu
copy .env.example .env

# Editează .env și adaugă API key-ul OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 Utilizare

### Inițializare

Prima dată, inițializează baza de date vectorială:

```bash
python -m src.chatbot_cli ingest
```

### Chat CLI (Interfața principală)

```bash
# Chat simplu
python -m src.chatbot_cli chat

# Cu funcții opționale
python -m src.chatbot_cli chat --tts --voice --image
```

### Interfață Web (Streamlit)

```bash
streamlit run src/chatbot_streamlit.py
```

### Verificare status

```bash
python -m src.chatbot_cli status
```

### Teste

```bash
python -m src.chatbot_cli test
```

## 💬 Exemple de utilizare

### Întrebări de test:

1. **"Vreau o carte despre prietenie și magie."**
   - Răspuns: Recomandă "The Hobbit" sau "The Lord of the Rings"
   - Apelează automat tool-ul pentru rezumatul detaliat

2. **"Ce recomanzi pentru cineva care iubește povești de război?"**
   - Răspuns: Recomandă "The Book Thief" sau "The Kite Runner"
   - Afișează rezumatul complet

3. **"Vreau o carte despre libertate și control social."**
   - Răspuns: Recomandă "1984" sau "Brave New World"
   - Prezintă analiza detaliată

4. **"Ce este 1984?"**
   - Răspuns: Explicație despre carte + rezumatul complet

### Fluxul conversației:

```
👤 User: "Vreau o carte despre prietenie și magie."

🤖 Smart Librarian: "Îți recomand cu căldură 'The Hobbit' de J.R.R. Tolkien! 
Această carte se potrivește perfect cu preferințele tale despre prietenie și magie..."

🔧 [Apel automat tool: get_summary_by_title("The Hobbit")]

📖 "Rezumat detaliat: Bilbo Baggins este un hobbit pașnic din Shire care 
trăiește o viață confortabilă și previzibilă... [4-6 paragrafe complete]"
```

## ⚙️ Opțiuni CLI

```bash
# Comenzi principale
python -m src.chatbot_cli ingest [--force]    # Inițializare/rebuild vector store
python -m src.chatbot_cli chat [opțiuni]      # Chat interactiv
python -m src.chatbot_cli status              # Status sistem
python -m src.chatbot_cli test                # Rulare teste

# Opțiuni chat
--tts       # Text-to-Speech (salvează MP3)
--voice     # Speech-to-Text (input vocal)
--image     # Generare imagini pentru coperți
--history   # Afișează istoric conversație
```

## 🔧 Configurare avansată

### Variabile de mediu (.env)

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=.chroma
```

### Structura proiectului

```
smart-librarian/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── book_summaries.md        # Rezumate scurte + teme
│   └── book_summaries.json      # Rezumate detaliate
├── src/
│   ├── __init__.py
│   ├── config.py                # Configurare
│   ├── schema.py                # Modele Pydantic
│   ├── data_loader.py           # Încărcare date
│   ├── embeddings.py            # OpenAI embeddings
│   ├── vector_store.py          # ChromaDB
│   ├── retriever.py             # Căutare semantică
│   ├── tools.py                 # Function calling
│   ├── llm.py                   # Integrare OpenAI
│   ├── safety.py                # Filtru siguranță
│   ├── tts.py                   # Text-to-Speech
│   ├── stt.py                   # Speech-to-Text
│   ├── image_gen.py             # Generare imagini
│   ├── chatbot_cli.py           # Interfață CLI
│   └── chatbot_streamlit.py     # Interfață web
├── tests/
│   ├── __init__.py
│   ├── test_tools.py            # Teste tools
│   └── test_retriever.py        # Teste retriever
└── output/                      # Fișiere generate
```

## 🧪 Teste

### Rulare teste individuale

```bash
# Teste tools
python tests/test_tools.py

# Teste retriever
python tests/test_retriever.py

# Teste complete cu pytest
pytest tests/ -v
```

### Validare sistem

```bash
python -m src.chatbot_cli test
```

Testele verifică:
- ✅ Încărcarea și consistența datelor
- ✅ Funcționalitatea vector store
- ✅ Tool calling pentru rezumate
- ✅ Filtrul de siguranță
- ✅ Căutarea semantică

## 🎨 Funcții opționale

### Text-to-Speech

```bash
python -m src.chatbot_cli chat --tts
```
- Folosește gTTS (Google) sau pyttsx3 (offline)
- Salvează răspunsurile ca MP3/WAV în `output/`

### Speech-to-Text

```bash
python -m src.chatbot_cli chat --voice
```
- Suportă OpenAI Whisper API sau SpeechRecognition
- Înregistrare de 5 secunde prin microfon

### Generare imagini

```bash
python -m src.chatbot_cli chat --image
```
- Folosește OpenAI DALL-E 3
- Generează coperți pentru cărțile recomandate
- Salvează în `output/`

## 🔍 De ce ChromaDB?

ChromaDB a fost ales în locul OpenAI Vector Store pentru:

1. **Control local** - Datele rămân pe sistemul local
2. **Persistență** - Baza de date se păstrează între rulări
3. **Performanță** - Acces rapid fără API calls pentru căutare
4. **Configurabilitate** - Control complet asupra indexării
5. **Cost** - Nu consumă credite OpenAI pentru storage

## 🚨 Troubleshooting

### Probleme frecvente:

**1. ChromaDB nu se inițializează**
```bash
# Șterge directorul Chroma și reinițializează
rmdir /s .chroma
python -m src.chatbot_cli ingest --force
```

**2. OpenAI API errors**
```bash
# Verifică API key
python -m src.chatbot_cli status

# Verifică quota și billing
```

**3. Dependențe lipsă**
```bash
# Reinstalează dependențele
pip install -r requirements.txt --force-reinstall
```

**4. Audio nu funcționează**
```bash
# Pentru TTS
pip install gTTS

# Pentru STT
pip install pyaudio SpeechRecognition
```

### Alternative dacă ChromaDB nu funcționează:

Proiectul poate fi adaptat să folosească Faiss sau alte vector stores:

```python
# În vector_store.py, înlocuiește ChromaDB cu Faiss
import faiss
# Implementare alternativă...
```

## 📈 Extensii viitoare

- [ ] Suport pentru mai multe limbi
- [ ] Integrare cu Goodreads API
- [ ] Recomandări bazate pe istoric
- [ ] Export conversații în PDF
- [ ] API REST pentru integrări
- [ ] Plugin pentru browser
- [ ] Integrare cu biblioteci online

## 📄 Licență

MIT License

## 🤝 Contribuții

Contribuțiile sunt binevenite! Urmează pașii:

1. Fork proiectul
2. Creează o branță pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push la branță (`git push origin feature/AmazingFeature`)
5. Deschide un Pull Request

## 📞 Support

Pentru probleme sau întrebări:

1. Verifică README-ul și documentația
2. Rulează `python -m src.chatbot_cli test` pentru diagnostice
3. Verifică issues în repository
4. Creează un issue nou cu detalii complete

---

**Smart Librarian v1.0** - Powered by OpenAI GPT & ChromaDB 📚🤖