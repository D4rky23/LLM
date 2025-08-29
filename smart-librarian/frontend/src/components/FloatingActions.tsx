import React, { useState } from 'react';
import { Plus, BookOpen, Mic, Sparkles, Heart, X } from 'lucide-react';
import { cn } from '../lib/utils';

export const FloatingActions: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    { 
      icon: BookOpen, 
      label: 'Browse Books', 
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => {
        const input = document.querySelector('input[placeholder*="books"]') as HTMLInputElement;
        if (input) {
          input.value = 'Show me popular books';
          input.focus();
        }
      }
    },
    { 
      icon: Heart, 
      label: 'Romance Books', 
      color: 'bg-pink-500 hover:bg-pink-600',
      action: () => {
        const input = document.querySelector('input[placeholder*="books"]') as HTMLInputElement;
        if (input) {
          input.value = 'Recommend romantic novels';
          input.focus();
        }
      }
    },
    { 
      icon: Sparkles, 
      label: 'Generate Cover', 
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => {
        const input = document.querySelector('input[placeholder*="books"]') as HTMLInputElement;
        if (input) {
          input.value = 'Generate a book cover for "My Adventure Story"';
          input.focus();
        }
      }
    },
    { 
      icon: Mic, 
      label: 'Quick Help', 
      color: 'bg-green-500 hover:bg-green-600',
      action: () => {
        const input = document.querySelector('input[placeholder*="books"]') as HTMLInputElement;
        if (input) {
          input.value = 'What can you help me with?';
          input.focus();
        }
      }
    }
  ];

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Action buttons */}
      {isOpen && (
        <div className="absolute bottom-16 right-0 space-y-3 fade-in-scale">
          {actions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <div
                key={index}
                className="flex items-center gap-3 slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="glass-card px-3 py-2 rounded-lg border border-white/20 hidden md:block">
                  <span className="text-sm text-white font-medium whitespace-nowrap">
                    {action.label}
                  </span>
                </div>
                <button
                  onClick={() => {
                    action.action();
                    setIsOpen(false);
                  }}
                  className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110',
                    action.color
                  )}
                >
                  <IconComponent className="w-5 h-5 text-white" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Main toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-14 h-14 rounded-full flex items-center justify-center shadow-xl transition-all duration-300 hover:scale-110 group',
          isOpen 
            ? 'bg-red-500 hover:bg-red-600 rotate-45' 
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
        )}
        title={isOpen ? 'Close quick actions' : 'Quick actions - Click for shortcuts!'}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <Plus className="w-6 h-6 text-white group-hover:rotate-90 transition-transform duration-300" />
        )}
      </button>

      {/* Tooltip when closed */}
      {!isOpen && (
        <div className="absolute bottom-16 right-0 glass-card px-3 py-2 rounded-lg border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap">
          <span className="text-sm text-white font-medium">
            🚀 Quick Actions
          </span>
        </div>
      )}

      {/* Ripple effect */}
      <div className="absolute inset-0 rounded-full bg-blue-400/20 animate-ping" 
           style={{ animationDuration: '3s' }} />
    </div>
  );
};