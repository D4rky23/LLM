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

interface MetricsState {
  sessionStartTime: number;
  responseTimes: number[];
  averageResponseTime: number;
  currentUsers: number;
  totalReaders: number;
  lastResponseTime: number | null;
  initializeSession: () => void;
  addResponseTime: (time: number) => void;
  setCurrentUsers: (users: number) => void;
  incrementReaders: () => void;
  getSessionDuration: () => number;
  getFormattedSessionTime: () => string;
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

export const useMetricsStore = create<MetricsState>()(
  devtools(
    (set, get) => ({
      sessionStartTime: Date.now(),
      responseTimes: [],
      averageResponseTime: 0,
      currentUsers: 1, // Start with 1 user (current user)
      totalReaders: 1, // Start with 1 reader (current user)
      lastResponseTime: null,
      
      initializeSession: () => {
        set({ 
          sessionStartTime: Date.now(),
          responseTimes: [],
          averageResponseTime: 0,
          lastResponseTime: null
        });
      },
      
      addResponseTime: (time) => {
        set((state) => {
          const newResponseTimes = [...state.responseTimes, time].slice(-20); // Keep last 20 response times
          const average = newResponseTimes.reduce((sum, t) => sum + t, 0) / newResponseTimes.length;
          
          return {
            responseTimes: newResponseTimes,
            averageResponseTime: Math.round(average),
            lastResponseTime: time
          };
        });
      },
      
      setCurrentUsers: (users) => set({ currentUsers: users }),
      
      incrementReaders: () => {
        set((state) => ({ totalReaders: state.totalReaders + 1 }));
      },
      
      getSessionDuration: () => {
        return Date.now() - get().sessionStartTime;
      },
      
      getFormattedSessionTime: () => {
        const duration = get().getSessionDuration();
        const minutes = Math.floor(duration / 60000);
        const seconds = Math.floor((duration % 60000) / 1000);
        
        if (minutes > 0) {
          return `${minutes}m ${seconds}s`;
        }
        return `${seconds}s`;
      }
    }),
    { name: 'metrics-store' }
  )
);

// Selector hooks for better performance
export const useChatMessages = () => useChatStore((state) => state.messages);
export const useChatLoading = () => useChatStore((state) => state.isLoading);
export const useChatError = () => useChatStore((state) => state.error);

export const useSystemStatus = () => useSystemStore((state) => state.status);
export const useSystemInfo = () => useSystemStore((state) => state.systemInfo);

// Metrics selector hooks
export const useSessionTime = () => useMetricsStore((state) => state.getFormattedSessionTime());
export const useResponseTime = () => useMetricsStore((state) => state.averageResponseTime);
export const useLastResponseTime = () => useMetricsStore((state) => state.lastResponseTime);
export const useCurrentUsers = () => useMetricsStore((state) => state.currentUsers);
export const useTotalReaders = () => useMetricsStore((state) => state.totalReaders);