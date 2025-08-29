import React from 'react';
import { Sparkles } from 'lucide-react';

const sampleQueries = [
  {
    query: 'I want a book about friendship and magic.',
    category: 'fantasy-friendship',
    emoji: '🧩',
  },
  {
    query: 'What do you recommend for someone who loves war stories?',
    category: 'war-historical',
    emoji: '⚔️',
  },
  {
    query: 'I want a book about freedom and social control.',
    category: 'dystopian-political',
    emoji: '🔒',
  },
  {
    query: 'What is 1984 about?',
    category: 'specific-book',
    emoji: '📚',
  },
  {
    query: 'Recommend me a psychological thriller.',
    category: 'psychological-thriller',
    emoji: '🧠',
  },
  {
    query: 'I love epic adventures with heroes.',
    category: 'epic-adventure',
    emoji: '🗡️',
  },
];

interface SampleQueriesProps {
  onQuerySelect: (query: string) => void;
}

export const SampleQueries: React.FC<SampleQueriesProps> = ({ onQuerySelect }) => {
  return (
    <div className="glass-card mb-4 rounded-2xl border border-white/10">
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center">
            <Sparkles className="w-3 h-3 text-white" />
          </div>
          <h3 className="text-lg font-semibold gradient-text">Try These Sample Questions</h3>
        </div>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sampleQueries.map((sample, index) => (
            <button
              key={index}
              className="sample-query-card h-auto p-3 text-left rounded-xl group"
              onClick={() => onQuerySelect(sample.query)}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="text-xl group-hover:scale-125 transition-transform duration-300 floating-element">
                  {sample.emoji}
                </div>
                <span className="text-xs flex-1 leading-relaxed text-gray-300 group-hover:text-white transition-colors">
                  {sample.query}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};