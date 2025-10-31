/**
 * MessageList Component
 * Scrollable list of chat messages with auto-scroll
 */

'use client';

import { useEffect, useRef } from 'react';
import { Message, MessageRole } from './Message';
import { cn } from '@/lib/utils';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface MessageListProps {
  messages: ChatMessage[];
  className?: string;
}

/**
 * MessageList Component
 *
 * Displays a scrollable list of chat messages with auto-scroll to latest
 *
 * @example
 * ```tsx
 * const messages = [
 *   { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
 *   { id: '2', role: 'assistant', content: 'Hi there!', timestamp: new Date() }
 * ];
 *
 * <MessageList messages={messages} />
 * ```
 */
export function MessageList({ messages, className }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className={cn('flex-1 flex items-center justify-center p-8', className)}>
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">💬</div>
          <h3 className="text-xl font-semibold text-slate-300 mb-2">
            Start a conversation
          </h3>
          <p className="text-slate-400 text-sm">
            Ask me anything about risk management, project management, or use any of the available skills.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        'flex-1 overflow-y-auto scroll-smooth p-4 space-y-4',
        className
      )}
    >
      {messages.map((message) => (
        <Message
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
          isStreaming={message.isStreaming}
        />
      ))}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
