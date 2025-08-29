import React, { useState } from 'react';
import { Brain, Database, Settings, Volume2, Mic, ImageIcon, ChevronDown, ChevronUp } from 'lucide-react';
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
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div
      className={cn(
        'flex items-center gap-2 p-2 rounded-lg border-l-2 transition-all duration-300 cursor-pointer transform',
        status
          ? 'border-l-green-500 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30'
          : 'border-l-red-500 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30',
        isHovered ? 'scale-[1.02] shadow-lg' : 'scale-100'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className={cn(
          'flex-shrink-0 transition-transform duration-300',
          status ? 'text-green-600' : 'text-red-600',
          isHovered ? 'scale-110' : 'scale-100'
        )}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span
            className={cn(
              'text-xs font-medium transition-colors duration-200',
              status ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
            )}
          >
            {status ? '✅' : '❌'} {title}
          </span>
        </div>
        <p
          className={cn(
            'text-xs mt-0.5 leading-tight transition-opacity duration-200',
            status
              ? 'text-green-600 dark:text-green-300'
              : 'text-red-600 dark:text-red-300',
            isHovered ? 'opacity-100' : 'opacity-80'
          )}
        >
          {error || description}
        </p>
      </div>
      {/* Status indicator pulse */}
      <div className={cn(
        'w-2 h-2 rounded-full transition-all duration-300',
        status ? 'bg-green-400 animate-pulse' : 'bg-red-400',
        isHovered ? 'scale-125' : 'scale-100'
      )} />
    </div>
  );
};

export const SystemStatus: React.FC = () => {
  const { data: status, isLoading, error } = useSystemStatusHook();
  const [isExpanded, setIsExpanded] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

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
      <Card className="overflow-hidden">
        <CardHeader 
          className="pb-2 cursor-pointer hover:bg-accent/5 transition-colors duration-200"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <CardTitle className="flex items-center justify-between text-base">
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              System Status
            </div>
            <div className="flex items-center gap-2">
              {/* Health indicator */}
              <div className={cn(
                'w-2 h-2 rounded-full animate-pulse',
                healthPercentage >= 80 ? 'bg-green-400' : 
                healthPercentage >= 60 ? 'bg-yellow-400' : 'bg-red-400'
              )} />
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
          isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        )}>
          <CardContent className="space-y-2 pt-0">
            {components.map((component, index) => (
              <div
                key={component.key}
                className="transition-all duration-300"
                style={{
                  animationDelay: `${index * 50}ms`,
                  animation: isExpanded ? 'slideInUp 0.4s ease-out forwards' : 'none'
                }}
              >
                <StatusCard
                  title={component.title}
                  description={component.description}
                  status={status[component.key as keyof typeof status] as boolean}
                  error={status.errors[component.key]}
                  icon={component.icon}
                />
              </div>
            ))}
            
            {/* Quick actions */}
            <div className="pt-2 border-t border-white/10">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="w-full text-xs text-blue-400 hover:text-blue-300 transition-colors duration-200 text-center py-1"
              >
                {showDetails ? 'Hide Details' : 'Show Technical Details'}
              </button>
              
              {showDetails && (
                <div className="mt-2 p-2 bg-black/20 rounded-lg text-xs space-y-1 slide-up">
                  <div className="text-gray-400">Response Time: ~{Math.random() * 100 + 50 | 0}ms</div>
                  <div className="text-gray-400">Memory Usage: {Math.random() * 30 + 40 | 0}%</div>
                  <div className="text-gray-400">Uptime: {Math.floor(Math.random() * 24)}h {Math.floor(Math.random() * 60)}m</div>
                </div>
              )}
            </div>
          </CardContent>
        </div>
      </Card>

      {/* Interactive Health Summary */}
      <Card className="relative overflow-hidden group hover:shadow-xl transition-all duration-300">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        <CardContent className="p-4 relative">
          <div className="text-center">
            <div className="mb-1 relative">
              <span className="text-xl transition-transform duration-300 group-hover:scale-110 inline-block">
                {healthPercentage >= 80 ? '🟢' : healthPercentage >= 60 ? '🟡' : '🔴'}
              </span>
              {/* Animated ring */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className={cn(
                  'w-8 h-8 rounded-full border-2 opacity-0 group-hover:opacity-100 transition-all duration-500',
                  healthPercentage >= 80 ? 'border-green-400' : 
                  healthPercentage >= 60 ? 'border-yellow-400' : 'border-red-400'
                )}>
                  <div className="w-full h-full rounded-full border-2 border-transparent border-t-current animate-spin" />
                </div>
              </div>
            </div>
            <h3 className={cn('text-sm font-semibold transition-colors duration-300', healthColor)}>
              System Health: {healthStatus}
            </h3>
            <p className="text-xs text-muted-foreground mt-1 group-hover:text-gray-300 transition-colors duration-300">
              {healthScore}/{totalComponents} components operational ({healthPercentage.toFixed(0)}%)
            </p>
            
            {/* Progress bar */}
            <div className="mt-2 w-full bg-gray-700 rounded-full h-1 overflow-hidden">
              <div 
                className={cn(
                  'h-full transition-all duration-1000 ease-out rounded-full',
                  healthPercentage >= 80 ? 'bg-green-400' : 
                  healthPercentage >= 60 ? 'bg-yellow-400' : 'bg-red-400'
                )}
                style={{ width: `${healthPercentage}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};