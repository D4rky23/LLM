import React, { useState } from 'react';
import { Settings, Volume2, Mic, ImageIcon, Bug, Trash2, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useSettingsStore, useSystemStatus } from '@/stores';
import { useClearChatHistory } from '@/hooks/useApi';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

interface ToggleSettingProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
  available: boolean;
  onChange: (enabled: boolean) => void;
}

const ToggleSetting: React.FC<ToggleSettingProps> = ({
  title,
  description,
  icon,
  enabled,
  available,
  onChange,
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  
  const handleToggle = (newValue: boolean) => {
    setIsAnimating(true);
    onChange(newValue);
    setTimeout(() => setIsAnimating(false), 300);
  };

  return (
    <div
      className={cn(
        'flex items-center justify-between p-2 rounded-lg border transition-all duration-300 group hover:shadow-md',
        available
          ? 'border-gray-200 hover:bg-accent/50 hover:border-blue-300'
          : 'border-gray-200 bg-muted/30 opacity-60',
        isAnimating ? 'scale-[1.02]' : 'scale-100'
      )}
    >
      <div className="flex items-center gap-2 flex-1">
        <div
          className={cn(
            'p-1.5 rounded-md transition-all duration-300 group-hover:scale-110',
            available ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
            enabled && available ? 'shadow-lg shadow-primary/20' : ''
          )}
        >
          {icon}
        </div>
        <div className="flex-1">
          <h4 className="text-xs font-medium transition-colors group-hover:text-primary">
            {title}
          </h4>
          <p className="text-xs text-muted-foreground leading-tight group-hover:text-gray-600">
            {description}
          </p>
        </div>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => handleToggle(e.target.checked)}
          disabled={!available}
          className="sr-only"
        />
        <div
          className={cn(
            'w-9 h-5 rounded-full transition-all duration-300 relative overflow-hidden',
            enabled && available
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30'
              : 'bg-gray-200 dark:bg-gray-700',
            isAnimating ? 'scale-110' : 'scale-100'
          )}
        >
          {/* Animated background for enabled state */}
          {enabled && available && (
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 animate-pulse opacity-50" />
          )}
          
          <div
            className={cn(
              'absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-all duration-300 shadow-md',
              enabled && available ? 'transform translate-x-4 shadow-lg' : '',
              isAnimating ? 'scale-110' : 'scale-100'
            )}
          >
            {/* Success indicator */}
            {enabled && available && (
              <div className="w-full h-full rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white text-xs">
                ✓
              </div>
            )}
          </div>
        </div>
        
        {/* Status indicator */}
        {available && (
          <div className={cn(
            'ml-1 w-1 h-1 rounded-full transition-all duration-300',
            enabled ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
          )} />
        )}
      </label>
    </div>
  );
};

export const SettingsPanel: React.FC = () => {
  const {
    useTTS,
    useSTT,
    useImageGeneration,
    debugMode,
    setUseTTS,
    setUseSTT,
    setUseImageGeneration,
    setDebugMode,
  } = useSettingsStore();

  const systemStatus = useSystemStatus();
  const clearHistory = useClearChatHistory();
  
  const [isExpanded, setIsExpanded] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
      try {
        await clearHistory.mutateAsync();
        toast('Chat history cleared successfully! ✨');
      } catch (error) {
        console.error('Failed to clear history:', error);
        toast('Failed to clear history. Please try again.');
      }
    }
  };

  const handleExportChat = () => {
    toast('🚀 Export feature coming soon!');
  };

  // Count enabled features
  const enabledFeatures = [useTTS, useSTT, useImageGeneration, debugMode].filter(Boolean).length;
  const totalFeatures = 4;

  const settings = [
    {
      key: 'tts',
      title: 'Text-to-Speech',
      description: 'Generate audio for AI responses',
      icon: <Volume2 className="w-4 h-4" />,
      enabled: useTTS,
      available: systemStatus?.tts || false,
      onChange: setUseTTS,
    },
    {
      key: 'stt',
      title: 'Speech-to-Text',
      description: 'Voice input and file transcription',
      icon: <Mic className="w-4 h-4" />,
      enabled: useSTT,
      available: systemStatus?.stt || false,
      onChange: setUseSTT,
    },
    {
      key: 'image',
      title: 'Image Generation',
      description: 'Generate book cover art',
      icon: <ImageIcon className="w-4 h-4" />,
      enabled: useImageGeneration,
      available: systemStatus?.image_gen || false,
      onChange: setUseImageGeneration,
    },
    {
      key: 'debug',
      title: 'Debug Mode',
      description: 'Show search results and debug info',
      icon: <Bug className="w-4 h-4" />,
      enabled: debugMode,
      available: true,
      onChange: setDebugMode,
    },
  ];

  return (
    <Card className="overflow-hidden">
      <CardHeader 
        className="pb-2 cursor-pointer hover:bg-accent/5 transition-all duration-200 group"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <CardTitle className="flex items-center justify-between text-base">
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4 transition-transform duration-300 group-hover:rotate-90" />
            Settings
          </div>
          <div className="flex items-center gap-2">
            {/* Features counter */}
            <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
              {enabledFeatures}/{totalFeatures}
            </div>
            <button className="transition-transform duration-300">
              {isExpanded ? 
                <ChevronUp className="w-4 h-4" /> : 
                <ChevronDown className="w-4 h-4" />
              }
            </button>
          </div>
        </CardTitle>
      </CardHeader>
      
      <div className={cn(
        'transition-all duration-500 ease-in-out overflow-hidden',
        isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
      )}>
        <CardContent className="space-y-4 pt-0">
          {/* Feature toggles */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Features
              </h4>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors duration-200"
              >
                {showAdvanced ? 'Basic' : 'Advanced'}
              </button>
            </div>
            
            <div className="space-y-2">
              {settings.map((setting, index) => (
                <div
                  key={setting.key}
                  className="transition-all duration-300"
                  style={{
                    animationDelay: `${index * 75}ms`,
                    animation: isExpanded ? 'slideInUp 0.4s ease-out forwards' : 'none'
                  }}
                >
                  <ToggleSetting
                    title={setting.title}
                    description={setting.description}
                    icon={setting.icon}
                    enabled={setting.enabled}
                    available={setting.available}
                    onChange={setting.onChange}
                  />
                </div>
              ))}
            </div>
            
            {/* Advanced options */}
            {showAdvanced && (
              <div className="mt-3 p-3 bg-black/20 rounded-lg space-y-2 slide-up">
                <h5 className="text-xs font-medium text-blue-400">Advanced Options</h5>
                <div className="text-xs text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Auto-save Settings:</span>
                    <span className="text-green-400">Enabled</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Performance Mode:</span>
                    <span className="text-yellow-400">Balanced</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cache Size:</span>
                    <span className="text-blue-400">50MB</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Actions
            </h4>
            
            <div className="grid grid-cols-1 gap-2">
              <Button
                variant="outline"
                onClick={handleClearHistory}
                disabled={clearHistory.isPending}
                className="w-full justify-start h-8 text-xs group hover:bg-red-50 hover:border-red-300 hover:text-red-600 transition-all duration-200"
              >
                <Trash2 className="w-3 h-3 mr-2 group-hover:animate-bounce" />
                Clear Chat History
                {clearHistory.isPending && (
                  <div className="ml-auto w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                )}
              </Button>

              <Button
                variant="outline"
                onClick={handleExportChat}
                className="w-full justify-start h-8 text-xs group hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-all duration-200"
              >
                <Sparkles className="w-3 h-3 mr-2 group-hover:rotate-180 transition-transform duration-500" />
                Export Chat
              </Button>
            </div>
          </div>

          {/* Enhanced Info Section */}
          <div className="text-xs text-muted-foreground space-y-1 leading-tight border-t border-white/10 pt-3">
            <div className="flex items-center gap-1">
              <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse"></span>
              <span>Features auto-sync with backend</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-1 h-1 bg-blue-400 rounded-full animate-pulse"></span>
              <span>Debug mode shows technical details</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-1 h-1 bg-purple-400 rounded-full animate-pulse"></span>
              <span>Settings saved locally & securely</span>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );
};