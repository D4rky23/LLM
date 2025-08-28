import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  ChatMessage,
  SystemStatus,
  SystemInfo,
  BookRecommendation,
} from '@/types/api';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

interface SystemState {
  status: SystemStatus | null;
  systemInfo: SystemInfo | null;
  isInitialized: boolean;
  setStatus: (status: SystemStatus) => void;
  setSystemInfo: (info: SystemInfo) => void;
  setInitialized: (initialized: boolean) => void;
}

interface SettingsState {
  useTTS: boolean;
  useSTT: boolean;
  useImageGeneration: boolean;
  debugMode: boolean;
  setUseTTS: (use: boolean) => void;
  setUseSTT: (use: boolean) => void;
  setUseImageGeneration: (use: boolean) => void;
  setDebugMode: (debug: boolean) => void;
}

interface SearchState {
  query: string;
  results: BookRecommendation[];
  isSearching: boolean;
  setQuery: (query: string) => void;
  setResults: (results: BookRecommendation[]) => void;
  setSearching: (searching: boolean) => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set) => ({
      messages: [],
      isLoading: false,
      error: null,
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      clearMessages: () => set({ messages: [] }),
    }),
    { name: 'chat-store' }
  )
);

export const useSystemStore = create<SystemState>()(
  devtools(
    (set) => ({
      status: null,
      systemInfo: null,
      isInitialized: false,
      setStatus: (status) => set({ status }),
      setSystemInfo: (systemInfo) => set({ systemInfo }),
      setInitialized: (isInitialized) => set({ isInitialized }),
    }),
    { name: 'system-store' }
  )
);

export const useSettingsStore = create<SettingsState>()(
  devtools(
    (set) => ({
      useTTS: false,
      useSTT: false,
      useImageGeneration: false,
      debugMode: false,
      setUseTTS: (useTTS) => set({ useTTS }),
      setUseSTT: (useSTT) => set({ useSTT }),
      setUseImageGeneration: (useImageGeneration) =>
        set({ useImageGeneration }),
      setDebugMode: (debugMode) => set({ debugMode }),
    }),
    { name: 'settings-store' }
  )
);

export const useSearchStore = create<SearchState>()(
  devtools(
    (set) => ({
      query: '',
      results: [],
      isSearching: false,
      setQuery: (query) => set({ query }),
      setResults: (results) => set({ results }),
      setSearching: (isSearching) => set({ isSearching }),
    }),
    { name: 'search-store' }
  )
);

// Selector hooks for better performance
export const useChatMessages = () => useChatStore((state) => state.messages);
export const useChatLoading = () => useChatStore((state) => state.isLoading);
export const useChatError = () => useChatStore((state) => state.error);

export const useSystemStatus = () => useSystemStore((state) => state.status);
export const useSystemInfo = () => useSystemStore((state) => state.systemInfo);