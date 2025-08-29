import React from 'react';
import { Settings, Volume2, Mic, ImageIcon, Bug, Trash2 } from 'lucide-react';
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
  return (
    <div
      className={cn(
        'flex items-center justify-between p-2 rounded-lg border transition-all duration-200',
        available
          ? 'border-gray-200 hover:bg-accent/50'
          : 'border-gray-200 bg-muted/30 opacity-60'
      )}
    >
      <div className="flex items-center gap-2 flex-1">
        <div
          className={cn(
            'p-1.5 rounded-md',
            available ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
          )}
        >
          {icon}
        </div>
        <div className="flex-1">
          <h4 className="text-xs font-medium">{title}</h4>
          <p className="text-xs text-muted-foreground leading-tight">{description}</p>
        </div>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onChange(e.target.checked)}
          disabled={!available}
          className="sr-only"
        />
        <div
          className={cn(
            'w-9 h-5 rounded-full transition-colors duration-200',
            enabled && available
              ? 'bg-primary'
              : 'bg-gray-200 dark:bg-gray-700'
          )}
        >
          <div
            className={cn(
              'dot absolute left-0.5 top-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-200',
              enabled && available ? 'transform translate-x-4' : ''
            )}
          />
        </div>
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

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
      try {
        await clearHistory.mutateAsync();
      } catch (error) {
        console.error('Failed to clear history:', error);
      }
    }
  };

  const handleExportChat = () => {
    // This would export chat history as JSON or text
    toast('Export feature coming soon!');
  };

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
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Settings className="w-4 h-4" />
          Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Feature toggles */}
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Features
          </h4>
          {settings.map((setting) => (
            <ToggleSetting
              key={setting.key}
              title={setting.title}
              description={setting.description}
              icon={setting.icon}
              enabled={setting.enabled}
              available={setting.available}
              onChange={setting.onChange}
            />
          ))}
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Actions
          </h4>
          
          <Button
            variant="outline"
            onClick={handleClearHistory}
            disabled={clearHistory.isPending}
            className="w-full justify-start h-8 text-xs"
          >
            <Trash2 className="w-3 h-3 mr-2" />
            Clear Chat History
          </Button>

          <Button
            variant="outline"
            onClick={handleExportChat}
            className="w-full justify-start h-8 text-xs"
          >
            <Settings className="w-3 h-3 mr-2" />
            Export Chat
          </Button>
        </div>

        {/* Info */}
        <div className="text-xs text-muted-foreground space-y-1 leading-tight">
          <p>• Features require backend services</p>
          <p>• Debug mode shows technical info</p>
          <p>• Settings saved locally</p>
        </div>
      </CardContent>
    </Card>
  );
};