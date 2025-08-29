import React, { useState, useRef, useEffect } from 'react';
import { Search, Book, Sparkles, Clock, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickSearchProps {
  onSearch?: (query: string) => void;
  className?: string;
}

const popularSearches = [
  "Fantasy books",
  "Sci-fi recommendations", 
  "Romance novels",
  "Mystery thrillers",
  "Self-help books",
  "Historical fiction"
];

const recentSearches = [
  "1984 George Orwell",
  "Books like Harry Potter",
  "Best productivity books"
];

export const QuickSearch: React.FC<QuickSearchProps> = ({ onSearch, className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setIsFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (searchQuery: string) => {
    if (searchQuery.trim()) {
      onSearch?.(searchQuery.trim());
      setQuery('');
      setIsOpen(false);
      setIsFocused(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch(query);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setIsFocused(false);
      inputRef.current?.blur();
    }
  };

  return (
    <div ref={containerRef} className={cn("relative z-50", className)}>
      {/* Search Input */}
      <div 
        className={cn(
          "flex items-center gap-2 glass-card transition-all duration-300 group cursor-text",
          isFocused || query 
            ? "px-4 py-2 rounded-lg bg-white/10 border border-blue-400/50 shadow-lg shadow-blue-500/20" 
            : "px-3 py-1.5 rounded-full hover:bg-white/10",
          "search-enhanced"
        )}
        onClick={() => {
          setIsOpen(true);
          setIsFocused(true);
          inputRef.current?.focus();
        }}
      >
        <Search className={cn(
          "transition-all duration-300",
          isFocused || query ? "w-4 h-4 text-blue-400" : "w-4 h-4 text-gray-400 group-hover:text-blue-400"
        )} />
        
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            setIsFocused(true);
            setIsOpen(true);
          }}
          onKeyDown={handleKeyPress}
          placeholder="Search books, authors, genres..."
          className={cn(
            "bg-transparent border-none outline-none text-sm transition-all duration-300",
            isFocused || query 
              ? "w-64 text-white placeholder-gray-400" 
              : "w-32 text-gray-400 placeholder-gray-500"
          )}
        />
        
        {query && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setQuery('');
            }}
            className="text-gray-400 hover:text-white transition-colors duration-200 ml-1"
          >
            ×
          </button>
        )}
      </div>

      {/* Search Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900/95 backdrop-filter backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl z-[9999] overflow-hidden slide-up">
          {query ? (
            /* Search Results */
            <div className="p-4">
              <div className="text-xs text-gray-400 mb-3 flex items-center gap-2">
                <Sparkles className="w-3 h-3" />
                Search suggestions for "{query}"
              </div>
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <button
                    key={i}
                    onClick={() => handleSearch(`${query} suggestion ${i + 1}`)}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 transition-colors duration-200 group"
                  >
                    <div className="flex items-center gap-3">
                      <Book className="w-4 h-4 text-blue-400" />
                      <div>
                        <div className="text-sm text-white group-hover:text-blue-300 transition-colors">
                          {query} - suggestion {i + 1}
                        </div>
                        <div className="text-xs text-gray-400">
                          {Math.floor(Math.random() * 100) + 10} results found
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Default Dropdown Content */
            <div className="p-4 space-y-4">
              {/* Recent Searches */}
              {recentSearches.length > 0 && (
                <div>
                  <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                    <Clock className="w-3 h-3" />
                    Recent searches
                  </div>
                  <div className="space-y-1">
                    {recentSearches.map((search, i) => (
                      <button
                        key={i}
                        onClick={() => handleSearch(search)}
                        className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                      >
                        {search}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Popular Searches */}
              <div>
                <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                  <TrendingUp className="w-3 h-3" />
                  Popular searches
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {popularSearches.map((search, i) => (
                    <button
                      key={i}
                      onClick={() => handleSearch(search)}
                      className="text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200 group"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-blue-400 rounded-full group-hover:bg-blue-300 transition-colors" />
                        {search}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Quick tip */}
              <div className="pt-3 border-t border-white/10">
                <div className="text-xs text-gray-500 flex items-center gap-2">
                  <div className="w-1 h-1 bg-purple-400 rounded-full animate-pulse" />
                  Tip: Try "books like [book name]" or "best [genre] books"
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};