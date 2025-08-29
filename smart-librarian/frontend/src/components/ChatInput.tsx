import React, { useState, useEffect } from 'react';
import { Send, Mic, Upload, X, Sparkles, BookOpen, Coffee, Star, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useSendMessage, useTranscribeFile, useTranscribeMicrophone } from '@/hooks/useApi';
import { useSettingsStore } from '@/stores';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

interface ChatInputProps {
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ disabled = false }) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const { useTTS, useImageGeneration, useSTT } = useSettingsStore();
  
  const quickSuggestions = [
    { icon: BookOpen, text: "Recommend a fantasy book", color: "text-purple-400" },
    { icon: Star, text: "Best sci-fi novels", color: "text-blue-400" },
    { icon: Coffee, text: "Cozy mystery books", color: "text-orange-400" },
    { icon: Sparkles, text: "Generate book cover", color: "text-pink-400" },
    { icon: Zap, text: "Book plot summary", color: "text-yellow-400" }
  ];
  const sendMessage = useSendMessage();
  const transcribeFile = useTranscribeFile();
  const transcribeMicrophone = useTranscribeMicrophone();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const textToSend = message.trim() || transcribedText.trim();
    
    if (!textToSend || disabled) return;

    try {
      await sendMessage.mutateAsync({
        message: textToSend,
        use_tts: useTTS,
        use_image: useImageGeneration,
      });
      
      setMessage('');
      setTranscribedText('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleVoiceRecord = async () => {
    if (!useSTT) {
      toast.error('Speech-to-text is not enabled');
      return;
    }

    setIsRecording(true);
    try {
      const result = await transcribeMicrophone.mutateAsync(5);
      setTranscribedText(result.text);
      toast.success('Voice recorded successfully');
    } catch (error) {
      console.error('Voice recording failed:', error);
    } finally {
      setIsRecording(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.type.startsWith('audio/')) {
      toast.error('Please upload an audio file');
      return;
    }

    try {
      const result = await transcribeFile.mutateAsync(file);
      setTranscribedText(result.text);
      toast.success('File transcribed successfully');
    } catch (error) {
      console.error('File transcription failed:', error);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const clearTranscribed = () => {
    setTranscribedText('');
  };

  const currentText = message || transcribedText;
  const isLoading = sendMessage.isPending || transcribeFile.isPending || isRecording;

  return (
    <div className="space-y-4 relative">
      {/* Quick Suggestions Panel */}
      {(showSuggestions || isFocused) && message.length === 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-2 fade-in-scale">
          <div className="glass-card p-3 rounded-xl border border-white/10 backdrop-blur-lg">
            <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
              <Sparkles className="w-3 h-3" />
              Quick suggestions
            </div>
            <div className="grid grid-cols-1 gap-2">
              {quickSuggestions.map((suggestion, index) => {
                const IconComponent = suggestion.icon;
                return (
                  <button
                    key={index}
                    onClick={() => {
                      setMessage(suggestion.text);
                      setShowSuggestions(false);
                    }}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-all duration-200 group text-left"
                  >
                    <IconComponent className={cn("w-4 h-4", suggestion.color)} />
                    <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                      {suggestion.text}
                    </span>
                    <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="w-1 h-1 bg-blue-400 rounded-full" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
      
      {/* Transcribed text display */}
      {transcribedText && (
        <div className="glass-card border border-blue-500/30 rounded-xl">
          <div className="p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <p className="text-sm font-semibold text-blue-300 mb-2 flex items-center gap-2">
                  🎤 Voice Input
                </p>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {transcribedText}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearTranscribed}
                className="text-blue-400 hover:text-blue-300 hover:bg-white/10 h-auto p-2 rounded-full"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Main input form */}
      <div
        className={cn(
          'glass-card rounded-xl border transition-all duration-300',
          dragActive ? 'border-blue-500/50 bg-blue-500/10' : 'border-white/10'
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="p-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex gap-3">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onFocus={() => {
                  setIsFocused(true);
                  setShowSuggestions(true);
                }}
                onBlur={() => {
                  setIsFocused(false);
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
                placeholder={
                  transcribedText
                    ? 'Voice input ready - click send or type to edit'
                    : 'Ask me anything about books...'
                }
                disabled={disabled || isLoading}
                className="flex-1 input-glass border-white/20 bg-white/5 text-white placeholder:text-gray-400 focus:border-blue-500/50 focus:bg-white/10"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />

              {/* Voice recording button */}
              {useSTT && (
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={handleVoiceRecord}
                  disabled={disabled || isLoading}
                  className={cn(
                    'glass-card border-white/20 hover:bg-white/10 transition-all duration-300',
                    isRecording && 'border-red-500/50 bg-red-500/20 text-red-400'
                  )}
                  title="Record voice (5 seconds)"
                >
                  {isRecording ? (
                    <LoadingSpinner size="sm" className="text-red-400" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </Button>
              )}

              {/* File upload button */}
              {useSTT && (
                <div className="relative">
                  <input
                    type="file"
                    accept="audio/*"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        handleFileUpload(file);
                      }
                    }}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    disabled={disabled || isLoading}
                    title="Upload audio file"
                    className="relative glass-card border-white/20 hover:bg-white/10"
                  >
                    <Upload className="w-4 h-4" />
                  </Button>
                </div>
              )}

              {/* Send button */}
              <Button
                type="submit"
                disabled={!currentText.trim() || disabled || isLoading}
                className="px-6 gradient-button"
              >
                {isLoading ? (
                  <LoadingSpinner size="sm" className="text-white" />
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Send
                  </>
                )}
              </Button>
            </div>

            {/* Drag and drop hint */}
            {dragActive && (
              <div className="text-center py-6 text-blue-400">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-medium">Drop audio file here to transcribe</p>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};