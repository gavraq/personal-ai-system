/**
 * QueryInput Component
 * Text input for chat queries with submit button
 */

'use client';

import { useState, KeyboardEvent, FormEvent } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Input';
import { cn } from '@/lib/utils';

export interface QueryInputProps {
  onSubmit: (query: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

/**
 * QueryInput Component
 *
 * Multi-line text input with submit button and keyboard shortcuts
 *
 * Features:
 * - Enter to submit (Shift+Enter for new line)
 * - Auto-resize textarea
 * - Character count
 * - Disabled state during streaming
 *
 * @example
 * ```tsx
 * <QueryInput
 *   onSubmit={(query) => console.log(query)}
 *   disabled={isStreaming}
 *   placeholder="Ask a question..."
 * />
 * ```
 */
export function QueryInput({
  onSubmit,
  disabled = false,
  placeholder = 'Ask a question or describe a risk management task...',
  className,
}: QueryInputProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();

    const trimmedQuery = query.trim();
    if (!trimmedQuery || disabled) return;

    onSubmit(trimmedQuery);
    setQuery('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const characterCount = query.length;
  const maxCharacters = 4000;
  const isNearLimit = characterCount > maxCharacters * 0.9;
  const isOverLimit = characterCount > maxCharacters;

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('border-t border-slate-800 bg-slate-900/50 p-4', className)}
    >
      <div className="max-w-4xl mx-auto">
        {/* Input Area */}
        <div className="relative">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={3}
            className={cn(
              'resize-none pr-24',
              isOverLimit && 'border-red-500 focus:border-red-500'
            )}
          />

          {/* Submit Button (overlaid on textarea) */}
          <div className="absolute right-2 bottom-2">
            <Button
              type="submit"
              variant="gradient"
              size="sm"
              disabled={disabled || !query.trim() || isOverLimit}
              className="shadow-lg"
            >
              {disabled ? 'Sending...' : 'Send'}
            </Button>
          </div>
        </div>

        {/* Footer Info */}
        <div className="flex items-center justify-between mt-2 text-xs text-slate-500">
          <span>
            Press <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-400">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-400">Shift + Enter</kbd> for new line
          </span>

          <span
            className={cn(
              isOverLimit && 'text-red-400 font-semibold',
              isNearLimit && !isOverLimit && 'text-yellow-400'
            )}
          >
            {characterCount.toLocaleString()} / {maxCharacters.toLocaleString()}
          </span>
        </div>
      </div>
    </form>
  );
}
