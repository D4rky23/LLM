import React from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Try These Sample Questions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sampleQueries.map((sample, index) => (
            <Button
              key={index}
              variant="outline"
              className="h-auto p-4 text-left justify-start hover:shadow-md transition-all duration-200 group"
              onClick={() => onQuerySelect(sample.query)}
            >
              <div className="flex items-center gap-3 w-full">
                <span className="text-lg group-hover:scale-110 transition-transform">
                  {sample.emoji}
                </span>
                <span className="text-sm flex-1 leading-relaxed">
                  {sample.query}
                </span>
              </div>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};