import React from 'react';
import { User, Bot, Volume2, Image as ImageIcon, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChatMessages } from '@/stores';
import { formatTimestamp } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  audioUrl?: string;
  imageUrl?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  timestamp,
  audioUrl,
  imageUrl,
}) => {
  const isUser = role === 'user';

  const handlePlayAudio = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play().catch(console.error);
    }
  };

  return (
    <div
      className={cn(
        'flex gap-3 mb-6 slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-lg',
          isUser
            ? 'bg-gradient-to-r from-blue-500 to-purple-600 glow-effect'
            : 'bg-gradient-to-r from-green-500 to-teal-600 glow-effect'
        )}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message Content */}
      <div className={cn('flex-1 max-w-[80%]', isUser && 'flex flex-col items-end')}>
        <div
          className={cn(
            'transition-all duration-300 hover:shadow-xl',
            isUser
              ? 'chat-message-user ml-auto'
              : 'chat-message-assistant'
          )}
        >
          <div className="p-5">
            {/* Header with timestamp */}
            <div className={cn('flex items-center gap-2 mb-3', isUser ? 'justify-end' : 'justify-start')}>
              <span className="text-sm font-semibold">
                {isUser ? 'You' : 'Smart Librarian'}
              </span>
              {timestamp && (
                <div className="flex items-center gap-1 text-xs opacity-70">
                  <Clock className="w-3 h-3" />
                  {formatTimestamp(timestamp)}
                </div>
              )}
            </div>

            {/* Message content */}
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <p className="mb-0 whitespace-pre-wrap leading-relaxed">
                {content}
              </p>
            </div>

            {/* Media attachments */}
            {(audioUrl || imageUrl) && (
              <div className="mt-4 space-y-3">
                {/* Audio player */}
                {audioUrl && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handlePlayAudio}
                      className="flex items-center gap-2 glass-card hover:bg-white/10 border-white/20"
                    >
                      <Volume2 className="w-4 h-4" />
                      Play Audio
                    </Button>
                  </div>
                )}

                {/* Generated image */}
                {imageUrl && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-gray-300">
                      <ImageIcon className="w-4 h-4" />
                      AI-generated book cover
                    </div>
                    <div className="glass-card p-2 rounded-lg">
                      <img
                        src={imageUrl}
                        alt="AI-generated book cover"
                        className="max-w-sm rounded-lg border border-white/20 shadow-xl"
                        loading="lazy"
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Reaction buttons for assistant messages */}
        {!isUser && (
          <div className="flex items-center gap-1 mt-3 text-xs">
            <Button variant="ghost" size="sm" className="h-8 px-3 glass-card hover:bg-white/10 border-white/10">
              👍
            </Button>
            <Button variant="ghost" size="sm" className="h-8 px-3 glass-card hover:bg-white/10 border-white/10">
              👎
            </Button>
            <Button variant="ghost" size="sm" className="h-8 px-3 glass-card hover:bg-white/10 border-white/10">
              📋
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export const ChatHistory: React.FC = () => {
  const messages = useChatMessages();

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center max-w-md mx-auto">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center floating-element glow-effect">
            <Bot className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-2xl font-bold mb-3 gradient-text">Welcome to Smart Librarian AI!</h3>
          <p className="text-gray-300 mb-6 leading-relaxed">
            I'm your personal AI librarian, here to help you discover amazing books. 
            I can recommend books based on your preferences, explain plots, and even generate book covers!
          </p>
          <div className="glass-card p-4 rounded-xl border border-white/10">
            <p className="text-sm text-gray-400">
              ✨ Try asking me about books, genres, or use the sample questions to get started!
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}
    </div>
  );
};