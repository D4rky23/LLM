export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  audioUrl?: string;
  imageUrl?: string;
}

export interface ChatRequest {
  message: string;
  use_tts?: boolean;
  use_image?: boolean;
}

export interface ChatResponse {
  response: string;
  audio_url?: string;
  image_url?: string;
  timestamp: string;
}

export interface SystemStatus {
  config: boolean;
  data: boolean;
  vector_store: boolean;
  chatbot: boolean;
  tts: boolean;
  stt: boolean;
  image_gen: boolean;
  errors: Record<string, string>;
}

export interface TranscriptionRequest {
  method?: string;
  duration?: number;
}

export interface TranscriptionResponse {
  text: string;
  confidence?: number;
}

export interface BookRecommendation {
  title: string;
  short_summary: string;
  themes: string[];
  score?: number;
}

export interface SearchResponse {
  query: string;
  books: BookRecommendation[];
  total_found: number;
}

export interface SystemInfo {
  total_books: number;
  vector_store_stats: Record<string, any>;
  available_features: string[];
}

export interface ApiError {
  error: string;
  status_code: number;
}