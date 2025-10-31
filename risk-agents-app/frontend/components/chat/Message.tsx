/**
 * Message Component
 * Individual chat message with user/assistant styling
 */

'use client';

import { cn } from '@/lib/utils';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface MessageProps {
  role: MessageRole;
  content: string;
  timestamp?: Date;
  isStreaming?: boolean;
  className?: string;
}

/**
 * Message Component
 *
 * Displays a single chat message with role-based styling
 *
 * @example
 * ```tsx
 * <Message
 *   role="user"
 *   content="What is risk management?"
 *   timestamp={new Date()}
 * />
 *
 * <Message
 *   role="assistant"
 *   content="Risk management is..."
 *   isStreaming={true}
 * />
 * ```
 */
export function Message({
  role,
  content,
  timestamp,
  isStreaming = false,
  className,
}: MessageProps) {
  const isUser = role === 'user';
  const isAssistant = role === 'assistant';
  const isSystem = role === 'system';

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg',
        isUser && 'bg-blue-500/10 border border-blue-500/20',
        isAssistant && 'bg-slate-800/50 border border-slate-700',
        isSystem && 'bg-yellow-500/10 border border-yellow-500/20',
        className
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
          isUser && 'bg-blue-500 text-white',
          isAssistant && 'bg-gradient-to-br from-purple-500 to-blue-600 text-white',
          isSystem && 'bg-yellow-500 text-slate-900'
        )}
      >
        {isUser && 'U'}
        {isAssistant && 'AI'}
        {isSystem && 'S'}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          <span
            className={cn(
              'text-sm font-semibold',
              isUser && 'text-blue-400',
              isAssistant && 'text-purple-400',
              isSystem && 'text-yellow-400'
            )}
          >
            {isUser && 'You'}
            {isAssistant && 'Risk Agent'}
            {isSystem && 'System'}
          </span>

          {timestamp && (
            <span className="text-xs text-slate-500">
              {timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}

          {isStreaming && (
            <span className="flex items-center gap-1 text-xs text-slate-400">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              Streaming...
            </span>
          )}
        </div>

        {/* Message Content */}
        <div
          className={cn(
            'text-sm leading-relaxed',
            isUser && 'text-slate-200',
            isAssistant && 'text-slate-300',
            isSystem && 'text-yellow-300'
          )}
        >
          {content}

          {isStreaming && !content && (
            <span className="inline-flex items-center gap-1">
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
