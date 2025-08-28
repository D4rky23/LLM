# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

# Smart Librarian React Frontend

O interfață modernă React TypeScript pentru aplicația Smart Librarian AI - un sistem inteligent de recomandări de cărți.

## 🚀 Caracteristici

- **💬 Chat Inteligent**: Interfață conversațională cu AI pentru recomandări de cărți
- **🎤 Intrare Vocală**: Transcripție audio folosind Speech-to-Text
- **🔊 Text-to-Speech**: Redare audio a răspunsurilor AI
- **🎨 Generare Imagini**: Creare automatizată de coperte de cărți
- **📊 Monitorizare Sistem**: Dashboard pentru statusul componentelor
- **🔍 Căutare Semantică**: Căutare avansată în baza de date de cărți
- **📱 Design Responsiv**: Optimizat pentru toate dispozitivele

## 🛠️ Tech Stack

### Frontend
- **React 19** - Framework UI modern
- **TypeScript** - Type safety și IntelliSense
- **Vite** - Build tool ultra-rapid
- **Tailwind CSS v4** - Framework CSS utility-first
- **Lucide React** - Icoane moderne și consistente

### State Management & API
- **Zustand** - State management simplu și performant
- **TanStack Query** - Data fetching și caching
- **Axios** - HTTP client robust
- **React Hook Form** - Gestionare forme performantă

### Developer Experience
- **ESLint** - Linting pentru cod consistent
- **Prettier** - Formatare automatizată
- **PostCSS** - Procesare CSS avansată
- **Hot Toast** - Notificări elegante

## 📁 Structura Proiectului

```
frontend/
├── src/
│   ├── components/           # Componente React reutilizabile
│   │   ├── ui/              # Componente UI de bază (Button, Input, etc.)
│   │   ├── ChatHistory.tsx  # Istoricul conversației
│   │   ├── ChatInput.tsx    # Input pentru mesaje
│   │   ├── SystemStatus.tsx # Status sistem
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   │   └── useApi.ts        # Hooks pentru API calls
│   ├── lib/                 # Utilities și configurări
│   │   ├── api.ts           # Client API cu Axios
│   │   └── utils.ts         # Funcții utility
│   ├── stores/              # Zustand stores
│   │   └── index.ts         # State management global
│   ├── types/               # TypeScript type definitions
│   │   └── api.ts           # Tipuri pentru API
│   ├── App.tsx              # Componenta principală
│   ├── main.tsx             # Entry point
│   └── index.css            # Stiluri globale
├── public/                  # Fișiere statice
├── tailwind.config.js       # Configurare Tailwind CSS
├── tsconfig.json           # Configurare TypeScript
├── vite.config.ts          # Configurare Vite
└── package.json            # Dependențe și scripturi
```

## 🚀 Cum să pornești

### Prerequisite
- Node.js 18+ și npm/yarn
- Backend API rulând pe http://localhost:8000

### Instalare și pornire

```bash
# Clonează repository-ul și navighează în directorul frontend
cd smart-librarian/frontend

# Instalează dependențele
npm install

# Pornește serverul de development
npm run dev

# Aplicația va fi disponibilă la http://localhost:3000
```

### Scripturi disponibile

```bash
npm run dev          # Pornește serverul de development
npm run build        # Creează build pentru producție
npm run preview      # Preview build-ul de producție
npm run lint         # Verifică codul cu ESLint
npm run lint:fix     # Corectează automat problemele ESLint
npm run format       # Formatează codul cu Prettier
npm run type-check   # Verifică tipurile TypeScript
```

## 🔧 Configurare

### Variables de mediu
Creează un fișier `.env.local` pentru configurările locale:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Smart Librarian AI
```

### Proxy API
Vite este configurat să facă proxy către backend pe portul 8000:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/static': 'http://localhost:8000'
  }
}
```

## 📱 Componente Principale

### ChatHistory
- Afișează conversația între utilizator și AI
- Suport pentru mesaje audio și imagini
- Butoane de feedback și reacții

### ChatInput
- Input text cu suport pentru Enter
- Înregistrare vocală (5 secunde)
- Upload fișiere audio pentru transcriere
- Drag & drop pentru fișiere

### SystemStatus
- Monitorizare în timp real a componentelor
- Indicatori vizuali pentru status (✅/❌)
- Calculare automată a health score-ului

### SettingsPanel
- Toggle pentru funcționalități (TTS, STT, Image Gen)
- Acțiuni pentru managementul chat-ului
- Informații despre availabilitatea serviciilor

## 🎨 Design System

### Culori
Folosește CSS custom properties pentru teme:
- `--primary`: Culoarea principală (albastru)
- `--secondary`: Culoarea secundară (gri deschis)
- `--background`: Fundalul aplicației
- `--foreground`: Culoarea textului

### Componente UI
Bazate pe design system modern cu Tailwind CSS:
- `Button`: Variante multiple (default, outline, destructive)
- `Input`: Stilizat consistent cu focus states
- `Card`: Container pentru secțiuni de conținut
- `LoadingSpinner`: Animație de loading

### Animații
- `fade-in`: Pentru apariția elementelor
- `slide-up`: Pentru mesajele din chat
- Hover effects pentru interactivitate

## 🔌 Integrare API

### Endpoints principale
```typescript
// Chat
POST /api/chat              # Trimite mesaj
DELETE /api/chat/history    # Șterge istoricul

// Audio
POST /api/transcribe        # Upload fișier audio
POST /api/transcribe/microphone # Înregistrare de la microfon

// Search
GET /api/search?query=...   # Căutare cărți
GET /api/books              # Lista toate cărțile

// System
GET /api/status             # Status componente
GET /api/system-info        # Informații sistem
```

### Error Handling
- Interceptori Axios pentru tratarea erorilor
- Toast notifications pentru feedback utilizator
- Retry logic pentru request-uri eșuate

## 🧪 Testing (În dezvoltare)

Planuri pentru implementarea testelor:

```bash
# Unit tests cu Vitest
npm run test

# Integration tests
npm run test:integration

# E2E tests cu Playwright
npm run test:e2e
```

## 📦 Build și Deploy

### Build pentru producție
```bash
npm run build
```

Generează fișiere optimizate în directorul `dist/`:
- Minificiere și compresie
- Tree shaking pentru bundle size mic
- Source maps pentru debugging

### Deploy
Poate fi deploy-at pe orice serviciu de static hosting:
- Vercel
- Netlify
- GitHub Pages
- Firebase Hosting

## 🛡️ Best Practices

### Code Style
- Folosește TypeScript strict mode
- Componentele sunt funcționale cu hooks
- Custom hooks pentru logica reutilizabilă
- Proper error boundaries

### Performance
- Lazy loading pentru componentele mari
- Memoization cu React.memo și useMemo
- Optimistic updates pentru UX mai bun
- Bundle splitting automat cu Vite

### Accessibility
- Semantic HTML
- ARIA labels și roles
- Keyboard navigation
- Screen reader support

## 🤝 Contribuții

1. Fork repository-ul
2. Creează un branch nou (`git checkout -b feature/amazing-feature`)
3. Commit schimbările (`git commit -m 'Add amazing feature'`)
4. Push la branch (`git push origin feature/amazing-feature`)
5. Deschide un Pull Request

## 📄 Licență

MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 📞 Support

Pentru întrebări sau probleme:
- Deschide un Issue pe GitHub
- Contactează echipa de dezvoltare

---

Dezvoltat cu ❤️ folosind React TypeScript și tehnologii moderne.

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
