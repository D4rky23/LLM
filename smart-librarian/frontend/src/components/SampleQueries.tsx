import React, { useState } from 'react';
import { Sparkles, Zap, BookOpen, Heart, Brain, Sword } from 'lucide-react';
import { cn } from '@/lib/utils';

const sampleQueries = [
  {
    query: 'I want a book about friendship and magic.',
    category: 'fantasy-friendship',
    emoji: '🧩',
    icon: Heart,
    gradient: 'from-pink-500 to-rose-500',
    description: 'Magical bonds and friendship adventures',
    tags: ['Fantasy', 'Friendship', 'Magic']
  },
  {
    query: 'What do you recommend for someone who loves war stories?',
    category: 'war-historical',
    emoji: '⚔️',
    icon: Sword,
    gradient: 'from-red-500 to-orange-500',
    description: 'Epic battles and historical conflicts',
    tags: ['War', 'History', 'Action']
  },
  {
    query: 'I want a book about freedom and social control.',
    category: 'dystopian-political',
    emoji: '🔒',
    icon: Brain,
    gradient: 'from-purple-500 to-indigo-500',
    description: 'Dystopian societies and political themes',
    tags: ['Dystopian', 'Politics', 'Freedom']
  },
  {
    query: 'What is 1984 about?',
    category: 'specific-book',
    emoji: '📚',
    icon: BookOpen,
    gradient: 'from-blue-500 to-cyan-500',
    description: 'Classic literature and book analysis',
    tags: ['Classic', 'Analysis', 'Literature']
  },
  {
    query: 'Recommend me a psychological thriller.',
    category: 'psychological-thriller',
    emoji: '🧠',
    icon: Zap,
    gradient: 'from-green-500 to-teal-500',
    description: 'Mind-bending psychological adventures',
    tags: ['Thriller', 'Psychology', 'Mystery']
  },
  {
    query: 'I love epic adventures with heroes.',
    category: 'epic-adventure',
    emoji: '🗡️',
    icon: Sword,
    gradient: 'from-yellow-500 to-amber-500',
    description: 'Heroic journeys and epic quests',
    tags: ['Adventure', 'Heroes', 'Epic']
  },
];

interface SampleQueriesProps {
  onQuerySelect: (query: string) => void;
}

export const SampleQueries: React.FC<SampleQueriesProps> = ({ onQuerySelect }) => {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleQueryClick = async (query: string) => {
    setIsAnimating(true);
    await onQuerySelect(query);
    setTimeout(() => setIsAnimating(false), 1000);
  };

  return (
    <div className="relative">
      {/* Floating particles background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-blue-400/30 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>

            <div className="glass-card border border-white/20 rounded-lg p-2 backdrop-blur-lg">
        {/* Animated header background */}
        <div className="absolute top-0 left-0 right-0 h-20 bg-gradient-to-r from-orange-500/20 via-yellow-500/20 to-orange-500/20 opacity-0 group-hover:opacity-100 transition-all duration-500" />
        
        <div className="p-2 border-b border-white/10 relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Sparkles className="w-4 h-4 text-white animate-pulse" />
                </div>
                {/* Orbit effect */}
                <div className="absolute inset-0 w-8 h-8 border border-yellow-400/50 rounded-full animate-spin opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{animationDuration: '3s'}} />
              </div>
              <h3 className="text-lg font-semibold gradient-text group-hover:scale-105 transition-transform duration-300">
                Try These Sample Questions
              </h3>
            </div>
            
            {/* Live counter */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-green-400 font-medium">{sampleQueries.length} ready</span>
            </div>
          </div>
        </div>
        
        <div className="p-2 relative z-10">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2">
            {sampleQueries.map((sample, index) => {
              const IconComponent = sample.icon;
              const isHovered = hoveredCard === sample.category;
              
              return (
                <button
                  key={index}
                  className={cn(
                    "relative h-auto p-3 text-left rounded-2xl group overflow-hidden transition-all duration-500 transform",
                    "bg-gradient-to-br from-white/5 to-white/10 border border-white/20",
                    "hover:scale-[1.02] hover:shadow-2xl",
                    isHovered ? "shadow-2xl scale-[1.02]" : "",
                    isAnimating ? "animate-pulse" : ""
                  )}
                  onClick={() => handleQueryClick(sample.query)}
                  onMouseEnter={() => setHoveredCard(sample.category)}
                  onMouseLeave={() => setHoveredCard(null)}
                  style={{
                    animationDelay: `${index * 100}ms`
                  }}
                >
                  {/* Animated background gradient */}
                  <div className={cn(
                    "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-20 transition-all duration-500",
                    sample.gradient
                  )} />
                  
                  {/* Shimmer effect */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 animate-shimmer" />
                  </div>
                  
                  <div className="relative z-10">
                    {/* Header with icons */}
                    <div className="flex items-center gap-3 mb-2">
                      <div className="relative">
                        <div className={cn(
                          "text-3xl group-hover:scale-125 transition-all duration-300 floating-element",
                          isHovered ? "animate-bounce" : ""
                        )}>
                          {sample.emoji}
                        </div>
                        {/* Icon overlay */}
                        <div className={cn(
                          "absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-500",
                          "bg-gradient-to-r", sample.gradient, "rounded-full w-8 h-8 -top-1 -left-1"
                        )}>
                          <IconComponent className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors duration-300">
                          {sample.description}
                        </div>
                      </div>
                    </div>
                    
                    {/* Main query text */}
                    <div className="text-sm leading-relaxed text-gray-300 group-hover:text-white transition-colors duration-300 mb-2">
                      {sample.query}
                    </div>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      {sample.tags.map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className={cn(
                            "px-2 py-1 text-xs rounded-full border transition-all duration-300",
                            "bg-white/5 border-white/20 text-gray-400",
                            "group-hover:bg-white/10 group-hover:border-white/30 group-hover:text-white"
                          )}
                          style={{
                            animationDelay: `${tagIndex * 50}ms`
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    
                    {/* Action indicator */}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                        <Zap className="w-3 h-3 text-white" />
                      </div>
                    </div>
                  </div>
                  
                  {/* Pulse effect on click */}
                  <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-active:opacity-100 transition-opacity duration-150" />
                </button>
              );
            })}
          </div>
          
          {/* Footer with tips */}
          <div className="mt-2 p-2 bg-black/20 rounded-lg border border-white/10">
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Sparkles className="w-3 h-3 animate-pulse" />
              <span>
                💡 <strong>Pro tip:</strong> Click any card to start exploring, or type your own question below!
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};