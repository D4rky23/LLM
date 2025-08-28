import React, { useState } from 'react';
import { Send, Mic, Upload, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
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

  const { useTTS, useImageGeneration, useSTT } = useSettingsStore();
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
    <div className="space-y-4">
      {/* Transcribed text display */}
      {transcribedText && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
          <CardContent className="p-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
                  🎤 Voice Input:
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  {transcribedText}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearTranscribed}
                className="text-blue-600 hover:text-blue-800 h-auto p-1"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main input form */}
      <Card
        className={cn(
          'transition-all duration-200',
          dragActive && 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="p-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex gap-2">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={
                  transcribedText
                    ? 'Voice input ready - click send or type to edit'
                    : 'Ask me anything about books...'
                }
                disabled={disabled || isLoading}
                className="flex-1"
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
                    'transition-colors',
                    isRecording && 'bg-red-100 border-red-300 text-red-600'
                  )}
                  title="Record voice (5 seconds)"
                >
                  {isRecording ? (
                    <LoadingSpinner size="sm" className="text-red-600" />
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
                    className="relative"
                  >
                    <Upload className="w-4 h-4" />
                  </Button>
                </div>
              )}

              {/* Send button */}
              <Button
                type="submit"
                disabled={!currentText.trim() || disabled || isLoading}
                className="px-6"
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
              <div className="text-center py-4 text-blue-600 dark:text-blue-400">
                <Upload className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">Drop audio file here to transcribe</p>
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
};