import React, { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { BookOpen, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatHistory } from '@/components/ChatHistory';
import { ChatInput } from '@/components/ChatInput';
import { SystemStatus } from '@/components/SystemStatus';
import { SampleQueries } from '@/components/SampleQueries';
import { SettingsPanel } from '@/components/SettingsPanel';
import { useSendMessage } from '@/hooks/useApi';
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
  const messages = useChatMessages();
  const sendMessage = useSendMessage();
  const { useTTS, useImageGeneration } = useSettingsStore();

  const handleSampleQuery = async (query: string) => {
    try {
      await sendMessage.mutateAsync({
        message: query,
        use_tts: useTTS,
        use_image: useImageGeneration,
      });
    } catch (error) {
      console.error('Failed to send sample query:', error);
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
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Messages Today</span>
                  <span className="text-xs font-bold text-blue-400">{Math.floor(Math.random() * 50) + 10}</span>
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
        <header className="header-glass p-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden hover:bg-white/10"
              >
                <Menu className="w-5 h-5" />
              </Button>
              
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center floating-element glow-effect">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold gradient-text">
                    Smart Librarian AI
                  </h1>
                  <p className="text-xs text-gray-300">
                    Discover incredible books with personalized AI recommendations
                  </p>
                </div>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="hidden sm:flex items-center gap-2 glass-card px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-300">Online</span>
            </div>
          </div>
        </header>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full h-full">
            {/* Sample Queries - Show only when no messages */}
            {messages.length === 0 && (
              <div className="p-3 flex-shrink-0">
                <SampleQueries onQuerySelect={handleSampleQuery} />
              </div>
            )}

            {/* Chat History */}
            <div className="flex-1 overflow-hidden">
              <ChatHistory />
            </div>

            {/* Chat Input */}
            <div className="p-3 header-glass flex-shrink-0">
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
