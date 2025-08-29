import React from 'react';
import { Brain, Database, Settings, Volume2, Mic, ImageIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useSystemStatus as useSystemStatusHook } from '@/hooks/useApi';
import { cn } from '@/lib/utils';

interface StatusCardProps {
  title: string;
  description: string;
  status: boolean;
  error?: string;
  icon: React.ReactNode;
}

const StatusCard: React.FC<StatusCardProps> = ({
  title,
  description,
  status,
  error,
  icon,
}) => {
  return (
    <div
      className={cn(
        'flex items-center gap-2 p-2 rounded-lg border-l-2 transition-all duration-200',
        status
          ? 'border-l-green-500 bg-green-50 dark:bg-green-900/20'
          : 'border-l-red-500 bg-red-50 dark:bg-red-900/20'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0',
          status ? 'text-green-600' : 'text-red-600'
        )}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span
            className={cn(
              'text-xs font-medium',
              status ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
            )}
          >
            {status ? '✅' : '❌'} {title}
          </span>
        </div>
        <p
          className={cn(
            'text-xs mt-0.5 leading-tight',
            status
              ? 'text-green-600 dark:text-green-300'
              : 'text-red-600 dark:text-red-300'
          )}
        >
          {error || description}
        </p>
      </div>
    </div>
  );
};

export const SystemStatus: React.FC = () => {
  const { data: status, isLoading, error } = useSystemStatusHook();

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Settings className="w-4 h-4" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <LoadingSpinner size="md" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Settings className="w-4 h-4" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4 text-red-600">
            <p className="text-sm">Failed to load system status</p>
            <p className="text-xs text-muted-foreground mt-1">
              {error.message}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const components = [
    {
      key: 'config',
      title: 'Configuration',
      description: 'System configuration loaded',
      icon: <Settings className="w-4 h-4" />,
    },
    {
      key: 'data',
      title: 'Data Store',
      description: 'Book database loaded',
      icon: <Database className="w-4 h-4" />,
    },
    {
      key: 'vector_store',
      title: 'Search Engine',
      description: 'Vector search ready',
      icon: <Database className="w-4 h-4" />,
    },
    {
      key: 'chatbot',
      title: 'AI Assistant',
      description: 'LLM model loaded',
      icon: <Brain className="w-4 h-4" />,
    },
    {
      key: 'tts',
      title: 'Text-to-Speech',
      description: 'Audio generation available',
      icon: <Volume2 className="w-4 h-4" />,
    },
    {
      key: 'stt',
      title: 'Speech-to-Text',
      description: 'Voice recognition ready',
      icon: <Mic className="w-4 h-4" />,
    },
    {
      key: 'image_gen',
      title: 'Image Generation',
      description: 'Cover art creation enabled',
      icon: <ImageIcon className="w-4 h-4" />,
    },
  ];

  // Calculate health score
  const healthScore = Object.values(status).filter(
    (value, index) => index < 7 && value === true
  ).length;
  const totalComponents = 7;
  const healthPercentage = (healthScore / totalComponents) * 100;

  let healthStatus = 'Needs Attention';
  let healthColor = 'text-red-600';
  if (healthPercentage >= 80) {
    healthStatus = 'Excellent';
    healthColor = 'text-green-600';
  } else if (healthPercentage >= 60) {
    healthStatus = 'Good';
    healthColor = 'text-yellow-600';
  }

  return (
    <div className="space-y-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Settings className="w-4 h-4" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {components.map((component) => (
            <StatusCard
              key={component.key}
              title={component.title}
              description={component.description}
              status={status[component.key as keyof typeof status] as boolean}
              error={status.errors[component.key]}
              icon={component.icon}
            />
          ))}
        </CardContent>
      </Card>

      {/* Health Summary */}
      <Card>
        <CardContent className="p-4">
          <div className="text-center">
            <div className="mb-1">
              <span className="text-xl">
                {healthPercentage >= 80 ? '🟢' : healthPercentage >= 60 ? '🟡' : '🔴'}
              </span>
            </div>
            <h3 className={cn('text-sm font-semibold', healthColor)}>
              System Health: {healthStatus}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              {healthScore}/{totalComponents} components operational ({healthPercentage.toFixed(0)}%)
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};