import React, { useState } from 'react';
import { User, Bot, Volume2, Image as ImageIcon, Clock, Sparkles, BookOpen, Zap, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChatMessages, useResponseTime, useTotalReaders } from '@/stores';
import { formatTimestamp } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface BookStatistics {
  totalBooks: number;
  bookList: any;
  systemInfo: any;
}

interface RealMetrics {
  sessionTime: string;
  responseTime: number;
  totalReaders: number;
}

interface ChatHistoryProps {
  bookStats?: BookStatistics;
  metrics?: RealMetrics;
}

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
        'flex gap-2 mb-4 slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium shadow-lg',
          isUser
            ? 'bg-gradient-to-r from-blue-500 to-purple-600 glow-effect'
            : 'bg-gradient-to-r from-green-500 to-teal-600 glow-effect'
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
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
          <div className="p-3">
            {/* Header with timestamp */}
            <div className={cn('flex items-center gap-2 mb-2', isUser ? 'justify-end' : 'justify-start')}>
              <span className="text-xs font-semibold">
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
              <p className="mb-0 whitespace-pre-wrap leading-relaxed text-sm">
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
                      className="flex items-center gap-2 glass-card hover:bg-white/10 border-white/20 h-7 text-xs"
                    >
                      <Volume2 className="w-3 h-3" />
                      Play Audio
                    </Button>
                  </div>
                )}

                {/* Generated image */}
                {imageUrl && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                      <ImageIcon className="w-3 h-3" />
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
          <div className="flex items-center gap-1 mt-2 text-xs">
            <Button variant="ghost" size="sm" className="h-6 px-2 glass-card hover:bg-white/10 border-white/10 text-xs">
              👍
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2 glass-card hover:bg-white/10 border-white/10 text-xs">
              👎
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2 glass-card hover:bg-white/10 border-white/10 text-xs">
              📋
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export const ChatHistory: React.FC<ChatHistoryProps> = ({ bookStats, metrics }) => {
  const messages = useChatMessages();
  const [typedText, setTypedText] = useState('');
  const [showFeatures, setShowFeatures] = useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  
  // Always call hooks - never conditionally
  const responseTimeFromStore = useResponseTime();
  const totalReadersFromStore = useTotalReaders();
  
  // Use passed metrics or fallback to store
  const responseTime = metrics?.responseTime ?? responseTimeFromStore;
  const totalReaders = metrics?.totalReaders ?? totalReadersFromStore;
  
  const welcomeTexts = [
    "Welcome to Smart Librarian AI!",
    "I'm your personal AI librarian, here to help you discover amazing books.",
    "I can recommend books based on your preferences, explain plots, and even generate book covers!"
  ];
  
  const features = [
    { icon: BookOpen, text: "Smart Recommendations", color: "text-blue-400" },
    { icon: Heart, text: "Personalized for You", color: "text-pink-400" },
    { icon: Zap, text: "Lightning Fast", color: "text-yellow-400" },
    { icon: Sparkles, text: "AI-Generated Covers", color: "text-purple-400" }
  ];

  React.useEffect(() => {
    if (messages && messages.length === 0) {
      const fullText = welcomeTexts.join(' ');
      let currentIndex = 0;
      
      const typingInterval = setInterval(() => {
        if (currentIndex <= fullText.length) {
          setTypedText(fullText.slice(0, currentIndex));
          currentIndex++;
        } else {
          clearInterval(typingInterval);
          setTimeout(() => setShowFeatures(true), 500);
        }
      }, 50);

      return () => clearInterval(typingInterval);
    }
  }, [messages?.length]);

  // Scroll to bottom when new messages are added (with small delay for smooth experience)
  React.useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages.length]);

  if (messages.length === 0) {
    return (
      <div className="h-full flex items-start justify-center p-3 relative overflow-y-auto">
        {/* Animated background particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-blue-400/20 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${i * 0.3}s`,
                animationDuration: `${3 + Math.random() * 4}s`
              }}
            />
          ))}
        </div>

        {/* Floating orbs */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-500/10 rounded-full filter blur-3xl animate-pulse" />
          <div className="absolute top-3/4 right-1/4 w-24 h-24 bg-purple-500/10 rounded-full filter blur-2xl animate-pulse delay-1000" />
          <div className="absolute top-1/2 right-1/3 w-20 h-20 bg-pink-500/10 rounded-full filter blur-xl animate-pulse delay-500" />
        </div>

        <div className="text-center max-w-2xl mx-auto relative z-10 py-2">
          {/* Animated Bot Avatar */}
          <div className="relative mb-4 group">
            <div className="w-12 h-12 mx-auto rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center floating-element glow-effect transition-all duration-500 group-hover:scale-110">
              <Bot className="w-6 h-6 text-white transition-transform duration-300 group-hover:rotate-12" />
            </div>
            
            {/* Orbit rings */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-16 h-16 border-2 border-blue-400/30 rounded-full animate-spin opacity-50" style={{animationDuration: '8s'}} />
              <div className="absolute w-20 h-20 border border-purple-400/20 rounded-full animate-spin opacity-30" style={{animationDuration: '12s', animationDirection: 'reverse'}} />
            </div>
            
            {/* Pulsing dots */}
            <div className="absolute -top-1 -right-1">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-ping opacity-30" />
              </div>
            </div>
          </div>

          {/* Typed Text Animation */}
          <div className="mb-2">
            <h3 className="text-xl font-bold mb-2 gradient-text">
              {typedText.includes('Welcome') ? typedText.split('I\'m')[0] : ''}
            </h3>
            {typedText.includes('I\'m') && (
              <p className="text-gray-300 leading-relaxed text-sm mb-3">
                {typedText.split('I\'m')[1]?.split('I can')[0] ? `I'm${typedText.split('I\'m')[1].split('I can')[0]}` : ''}
              </p>
            )}
            {typedText.includes('I can') && (
              <p className="text-gray-400 leading-relaxed text-xs">
                {typedText.includes('I can') ? `I can${typedText.split('I can')[1]}` : ''}
              </p>
            )}
            
            {/* Typing cursor */}
            {typedText.length < welcomeTexts.join(' ').length && (
              <span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-1" />
            )}
          </div>

          {/* Features Grid */}
          {showFeatures && (
            <div className="mb-2 fade-in-scale">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {features.map((feature, index) => {
                  const IconComponent = feature.icon;
                  return (
                    <div
                      key={index}
                      className="glass-card p-2 rounded-lg border border-white/10 hover:border-white/20 transition-all duration-300 group cursor-pointer"
                      style={{
                        animationDelay: `${index * 150}ms`
                      }}
                    >
                      <div className="text-center">
                        <IconComponent className={cn(
                          "w-5 h-5 mx-auto mb-1 transition-all duration-300 group-hover:scale-125",
                          feature.color
                        )} />
                        <span className="text-xs text-gray-400 group-hover:text-white transition-colors">
                          {feature.text}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Interactive Stats */}
          {showFeatures && (
            <div className="glass-card p-2 rounded-lg border border-white/10 slide-up mb-2">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="group cursor-pointer">
                  <div className="text-lg font-bold gradient-text mb-1 group-hover:scale-110 transition-transform">
                    {bookStats?.totalBooks || '...'}
                  </div>
                  <div className="text-xs text-gray-400 group-hover:text-white transition-colors">Books</div>
                </div>
                <div className="group cursor-pointer">
                  <div className="text-lg font-bold text-green-400 mb-1 group-hover:scale-110 transition-transform">
                    1
                  </div>
                  <div className="text-xs text-gray-400 group-hover:text-white transition-colors">Reader{totalReaders !== 1 ? 's' : ''}</div>
                </div>
                <div className="group cursor-pointer">
                  <div className="text-lg font-bold text-purple-400 mb-1 group-hover:scale-110 transition-transform">
                    {responseTime > 0 ? `${responseTime}ms` : 'N/A'}
                  </div>
                  <div className="text-xs text-gray-400 group-hover:text-white transition-colors">Response</div>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced CTA */}
          {showFeatures && (
            <div className="glass-card p-2 rounded-lg border border-white/10 slide-up mb-2">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
                <Sparkles className="w-4 h-4 animate-pulse text-purple-400" />
                <span>
                  ✨ <strong className="text-white">Ready to explore?</strong> Try the sample questions above!
                </span>
              </div>
              
              {/* Quick action buttons */}
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {['Fantasy', 'Sci-Fi', 'Romance', 'Mystery'].map((genre, index) => (
                  <button
                    key={index}
                    className="px-2 py-1 text-xs bg-white/5 border border-white/20 rounded-full hover:bg-white/10 hover:border-white/30 transition-all duration-200 hover:scale-105"
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-3 space-y-3">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
          audioUrl={message.audioUrl}
          imageUrl={message.imageUrl}
        />
      ))}
      <div ref={messagesEndRef} />
      {/* Add some bottom padding to ensure last message is visible */}
      <div className="h-4" />
    </div>
  );
};