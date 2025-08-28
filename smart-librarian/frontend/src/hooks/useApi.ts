import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { useChatStore, useSystemStore } from '@/stores';
import type { ChatRequest } from '@/types/api';
import toast from 'react-hot-toast';

// System hooks
export const useSystemStatus = () => {
  const setStatus = useSystemStore((state) => state.setStatus);

  return useQuery({
    queryKey: ['system-status'],
    queryFn: async () => {
      const response = await apiClient.getSystemStatus();
      setStatus(response.data);
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
};

export const useSystemInfo = () => {
  const setSystemInfo = useSystemStore((state) => state.setSystemInfo);

  return useQuery({
    queryKey: ['system-info'],
    queryFn: async () => {
      const response = await apiClient.getSystemInfo();
      setSystemInfo(response.data);
      return response.data;
    },
    staleTime: 60000, // Consider data stale after 1 minute
  });
};

// Chat hooks
export const useSendMessage = () => {
  const { addMessage, setLoading, setError } = useChatStore();

  return useMutation({
    mutationFn: async (request: ChatRequest) => {
      setLoading(true);
      setError(null);

      // Add user message immediately
      addMessage({
        role: 'user',
        content: request.message,
        timestamp: new Date().toISOString(),
      });

      const response = await apiClient.sendMessage(request);
      return response.data;
    },
    onSuccess: (data) => {
      // Add assistant response
      addMessage({
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
      });

      setLoading(false);
      toast.success('Response received');
    },
    onError: (error: any) => {
      const errorMessage = error.error || 'Failed to send message';
      setError(errorMessage);
      setLoading(false);
      toast.error(errorMessage);
    },
  });
};

export const useClearChatHistory = () => {
  const { clearMessages } = useChatStore();

  return useMutation({
    mutationFn: apiClient.clearChatHistory,
    onSuccess: () => {
      clearMessages();
      toast.success('Chat history cleared');
    },
    onError: (error: any) => {
      toast.error(error.error || 'Failed to clear history');
    },
  });
};

// Audio hooks
export const useTranscribeFile = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.transcribeFile(file);
      return response.data;
    },
    onSuccess: () => {
      toast.success('File transcribed successfully');
    },
    onError: (error: any) => {
      toast.error(error.error || 'Failed to transcribe file');
    },
  });
};

export const useTranscribeMicrophone = () => {
  return useMutation({
    mutationFn: async (duration: number = 5) => {
      const response = await apiClient.transcribeMicrophone(duration);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Voice transcribed successfully');
    },
    onError: (error: any) => {
      toast.error(error.error || 'Failed to transcribe voice');
    },
  });
};

// Search hooks
export const useSearchBooks = () => {
  return useMutation({
    mutationFn: async ({
      query,
      topK = 5,
    }: {
      query: string;
      topK?: number;
    }) => {
      const response = await apiClient.searchBooks(query, topK);
      return response.data;
    },
    onError: (error: any) => {
      toast.error(error.error || 'Failed to search books');
    },
  });
};

export const useAllBooks = () => {
  return useQuery({
    queryKey: ['all-books'],
    queryFn: async () => {
      const response = await apiClient.getAllBooks();
      return response.data;
    },
    staleTime: 300000, // Consider data stale after 5 minutes
  });
};

export const useBookByTitle = (title: string, enabled = true) => {
  return useQuery({
    queryKey: ['book', title],
    queryFn: async () => {
      const response = await apiClient.getBookByTitle(title);
      return response.data;
    },
    enabled: enabled && !!title,
    staleTime: 300000,
  });
};