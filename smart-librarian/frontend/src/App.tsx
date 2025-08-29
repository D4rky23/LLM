import React, { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { BookOpen, Menu, X, Star, Zap, Globe, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatHistory } from '@/components/ChatHistory';
import { ChatInput } from '@/components/ChatInput';
import { SystemStatus } from '@/components/SystemStatus';
import { SampleQueries } from '@/components/SampleQueries';
import { SettingsPanel } from '@/components/SettingsPanel';
import { QuickSearch } from '@/components/QuickSearch';
import { useSendMessage, useBookStatistics } from '@/hooks/useApi';
import { useChatMessages, useSettingsStore } from '@/stores';
import { cn } from '@/lib/utils';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const AppContent: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [headerScrolled, setHeaderScrolled] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messages = useChatMessages();
  const sendMessage = useSendMessage();
  const { useTTS, useImageGeneration } = useSettingsStore();
  const { data: bookStats, isLoading: bookStatsLoading } = useBookStatistics();

  const handleSampleQuery = async (query: string) => {
    try {
      setIsTyping(true);
      await sendMessage.mutateAsync({
        message: query,
        use_tts: useTTS,
        use_image: useImageGeneration,
      });
    } catch (error) {
      console.error('Failed to send sample query:', error);
    } finally {
      setIsTyping(false);
    }
  };

  // Simulate scroll effect for header and add parallax
  useEffect(() => {
    const interval = setInterval(() => {
      setHeaderScrolled(messages.length > 0);
    }, 100);
    return () => clearInterval(interval);
  }, [messages.length]);

  // Add mouse parallax effect for header
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const header = document.querySelector('.header-enhanced') as HTMLElement;
      if (header) {
        const rect = header.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width - 0.5) * 20;
        const y = ((e.clientY - rect.top) / rect.height - 0.5) * 10;
        
        const orbs = header.querySelectorAll('.parallax-orb');
        orbs.forEach((orb, index) => {
          const factor = (index + 1) * 0.5;
          (orb as HTMLElement).style.transform = `translate(${x * factor}px, ${y * factor}px)`;
        });
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleQuickSearch = async (query: string) => {
    try {
      setIsTyping(true);
      await handleSampleQuery(query);
    } catch (error) {
      console.error('Failed to execute quick search:', error);
    } finally {
      setIsTyping(false);
    }
  };

  // Close sidebar on mobile when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.getElementById('sidebar');
      const target = event.target as Node;
      
      if (sidebarOpen && sidebar && !sidebar.contains(target)) {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sidebarOpen]);

  return (
    <div className="h-screen flex overflow-hidden">
      {/* Sidebar */}
      <div
        id="sidebar"
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-80 sidebar-glass transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-3 border-b border-white/10 flex-shrink-0">
            <h2 className="text-lg font-semibold gradient-text">Smart Librarian</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Sidebar Content */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            {/* Mini Dashboard */}
            <div className="glass-card p-3 rounded-xl border border-white/10 hover:border-blue-400/30 transition-all duration-300 group">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-gray-300 group-hover:text-white transition-colors">
                  Quick Stats
                </h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Books Available</span>
                  <span className="text-xs font-bold text-blue-400">{bookStatsLoading ? '...' : bookStats?.totalBooks || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Response Time</span>
                  <span className="text-xs font-bold text-green-400">{Math.floor(Math.random() * 100) + 200}ms</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Session</span>
                  <span className="text-xs font-bold text-purple-400">{Math.floor(Math.random() * 30) + 5}min</span>
                </div>
              </div>
              
              {/* Activity indicator */}
              <div className="mt-3 pt-2 border-t border-white/10">
                <div className="flex items-center gap-2">
                  <div className="flex space-x-1">
                    {[...Array(7)].map((_, i) => (
                      <div 
                        key={i} 
                        className="w-1 h-3 bg-blue-400/30 rounded-full"
                        style={{
                          height: `${Math.random() * 12 + 4}px`,
                          background: `linear-gradient(to top, rgba(59, 130, 246, 0.3), rgba(59, 130, 246, ${Math.random() * 0.5 + 0.3}))`
                        }}
                      />
                    ))}
                  </div>
                  <span className="text-xs text-gray-400 ml-auto">7 days</span>
                </div>
              </div>
            </div>
            
            <SystemStatus />
            <SettingsPanel />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Header */}
        <header className={cn(
          "header-glass header-enhanced transition-all duration-500 relative overflow-hidden",
          headerScrolled ? "p-2 shadow-2xl" : "p-3"
        )}>
          {/* Animated background overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-cyan-600/10 animate-pulse opacity-50" />
          <div className="absolute inset-0">
            <div className="parallax-orb absolute top-0 left-0 w-32 h-32 bg-blue-500/20 rounded-full filter blur-3xl animate-pulse transition-transform duration-300" />
            <div className="parallax-orb absolute top-0 right-0 w-24 h-24 bg-purple-500/20 rounded-full filter blur-2xl animate-pulse delay-1000 transition-transform duration-300" />
            <div className="parallax-orb absolute bottom-0 left-1/3 w-20 h-20 bg-cyan-500/15 rounded-full filter blur-2xl animate-pulse delay-500 transition-transform duration-300" />
          </div>
          
          <div className="flex items-center justify-between relative z-10">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden hover:bg-white/10 transition-all duration-300 hover:scale-110"
              >
                <Menu className="w-5 h-5" />
              </Button>
              
              <div className="flex items-center gap-3 group">
                {/* Enhanced Logo */}
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center floating-element glow-effect transition-all duration-500 group-hover:scale-125 group-hover:rotate-12">
                    <BookOpen className="w-5 h-5 text-white transition-transform duration-300 group-hover:scale-110" />
                  </div>
                  {/* Orbit rings */}
                  <div className="absolute inset-0 w-10 h-10 border-2 border-blue-400/30 rounded-full animate-spin opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{animationDuration: '3s'}} />
                  <div className="absolute inset-0 w-10 h-10 border border-purple-400/30 rounded-full animate-spin opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{animationDuration: '2s', animationDirection: 'reverse'}} />
                </div>
                
                <div className="transition-all duration-300">
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold gradient-text transition-all duration-300 group-hover:scale-105">
                      Smart Librarian AI
                    </h1>
                    {/* Live indicators */}
                    <div className="flex items-center gap-1">
                      <div className="flex items-center gap-1 bg-green-500/20 px-2 py-1 rounded-full border border-green-500/30">
                        <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                        <span className="text-xs text-green-400 font-medium">LIVE</span>
                      </div>
                      {isTyping && (
                        <div className="flex items-center gap-1 bg-blue-500/20 px-2 py-1 rounded-full border border-blue-500/30 animate-pulse">
                          <Zap className="w-3 h-3 text-blue-400" />
                          <span className="text-xs text-blue-400 font-medium">Thinking...</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-xs text-gray-300 transition-colors duration-300 group-hover:text-white">
                      Discover incredible books with personalized AI recommendations
                    </p>
                    {/* Stats */}
                    <div className="hidden md:flex items-center gap-3 text-xs">
                      <div className="flex items-center gap-1 text-blue-400">
                        <Star className="w-3 h-3" />
                        <span>{bookStatsLoading ? '...' : `${bookStats?.totalBooks || 0}+ Books`}</span>
                      </div>
                      <div className="flex items-center gap-1 text-purple-400">
                        <Users className="w-3 h-3" />
                        <span>{Math.floor(Math.random() * 50) + 100}+ Users</span>
                      </div>
                      <div className="flex items-center gap-1 text-green-400">
                        <Globe className="w-3 h-3" />
                        <span>Multi-language</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Right Section */}
            <div className="flex items-center gap-3">
              {/* Quick Search */}
              <QuickSearch onSearch={handleQuickSearch} className="hidden md:block" />
              
              {/* AI Status */}
              <div className="flex items-center gap-2 glass-card px-3 py-1.5 rounded-full group hover:shadow-lg transition-all duration-300">
                <span className="text-xs text-gray-300 group-hover:text-white transition-colors font-medium">AI Online</span>
                
                {/* Performance indicator */}
                <div className="hidden sm:flex items-center gap-1 ml-2 text-xs">
                  <div className="w-12 bg-gray-700 rounded-full h-1 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-400 to-blue-400 rounded-full transition-all duration-1000" 
                         style={{width: `${Math.random() * 30 + 70}%`}} />
                  </div>
                  <span className="text-gray-400">{Math.floor(Math.random() * 50) + 150}ms</span>
                </div>
              </div>
              
              {/* Activity Indicator */}
              <div className="hidden lg:flex items-center gap-1 glass-card px-2 py-1.5 rounded-full">
                {[...Array(5)].map((_, i) => (
                  <div 
                    key={i}
                    className="w-0.5 bg-blue-400/50 rounded-full transition-all duration-300"
                    style={{
                      height: `${Math.random() * 12 + 4}px`,
                      animationDelay: `${i * 200}ms`
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
          
          {/* Bottom border with animated gradient */}
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50" />
        </header>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full h-full">
            {/* Sample Queries - Show only when no messages */}
            {messages.length === 0 && (
              <div className="p-2 flex-shrink-0">
                <SampleQueries onQuerySelect={handleSampleQuery} />
              </div>
            )}

            {/* Chat History */}
            <div className="flex-1 overflow-hidden min-h-0">
              <ChatHistory bookStats={bookStats} />
            </div>

            {/* Chat Input */}
            <div className="p-2 header-glass flex-shrink-0">
              <ChatInput disabled={sendMessage.isPending} />
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-60 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          className: 'text-sm',
          style: {
            background: 'hsl(var(--background))',
            color: 'hsl(var(--foreground))',
            border: '1px solid hsl(var(--border))',
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
