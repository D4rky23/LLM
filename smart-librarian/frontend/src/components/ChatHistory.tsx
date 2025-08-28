import React from 'react';
import { User, Bot, Volume2, Image as ImageIcon, Clock } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
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
        'flex gap-3 mb-4 animate-slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium',
          isUser
            ? 'bg-blue-600'
            : 'bg-green-600'
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message Content */}
      <div className={cn('flex-1 max-w-[80%]', isUser && 'flex flex-col items-end')}>
        <Card
          className={cn(
            'transition-all duration-200 hover:shadow-md',
            isUser
              ? 'chat-message-user ml-auto'
              : 'chat-message-assistant'
          )}
        >
          <CardContent className="p-4">
            {/* Header with timestamp */}
            <div className={cn('flex items-center gap-2 mb-2', isUser ? 'justify-end' : 'justify-start')}>
              <span className="text-sm font-medium">
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
              <div className="mt-3 space-y-2">
                {/* Audio player */}
                {audioUrl && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handlePlayAudio}
                      className="flex items-center gap-2"
                    >
                      <Volume2 className="w-4 h-4" />
                      Play Audio
                    </Button>
                  </div>
                )}

                {/* Generated image */}
                {imageUrl && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <ImageIcon className="w-4 h-4" />
                      AI-generated book cover
                    </div>
                    <img
                      src={imageUrl}
                      alt="AI-generated book cover"
                      className="max-w-sm rounded-lg border shadow-sm"
                      loading="lazy"
                    />
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Reaction buttons for assistant messages */}
        {!isUser && (
          <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
            <Button variant="ghost" size="sm" className="h-6 px-2">
              👍
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2">
              👎
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2">
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
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Welcome to Smart Librarian AI!</h3>
          <p className="text-muted-foreground mb-4">
            I'm your personal AI librarian, here to help you discover amazing books. 
            I can recommend books based on your preferences, explain plots, and even generate book covers!
          </p>
          <p className="text-sm text-muted-foreground">
            ✨ Try asking me about books, genres, or use the sample questions to get started!
          </p>
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