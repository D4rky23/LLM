# Quick Start Guide - Smart Librarian AI

## 📋 Prereq Check
- [x] Node.js 18+ installed
- [x] Python 3.8+ installed  
- [ ] OpenAI API key ready

## ⚡ Super Quick Setup (5 minutes)

### 1. Get the Code
```bash
git clone <repository-url>
cd smart-librarian
```

### 2. Backend Setup
```bash
# Install Python deps
pip install -r requirements.txt

# Add your OpenAI key
echo "OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE" > .env
```

### 3. Frontend Setup
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

### 4. Run Both Services
```bash
# Terminal 1 - Backend
python backend/main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

### 5. Open & Test
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## 🎯 Test It Works
1. Open http://localhost:3000
2. Type: "Recomandă-mi o carte de aventuri"
3. See AI response + book recommendation
4. ✅ You're ready to go!

## 🔧 Optional Features
Add these to `.env` for extra functionality:
```env
ELEVENLABS_API_KEY=your_key    # For text-to-speech
HUGGINGFACE_API_KEY=hf_key     # For image generation
```

## 🚨 Troubleshooting
- **CORS errors**: Check backend is running on port 8000
- **API errors**: Verify OpenAI key in `.env` file
- **Build fails**: Run `npm install` again in frontend/

## 📚 Next Steps
- Check [Frontend README](./frontend/README.md) for UI details
- Check [Backend README](./backend/README.md) for API docs
- Browse sample books in `data/book_summaries.json`