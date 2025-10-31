/**
 * ChatInterface Component
 * Main chat interface integrating WebSocket, messages, and input
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWebSocketQuery } from '@/contexts/WebSocketContext';
import { MessageList, ChatMessage } from './MessageList';
import { QueryInput } from './QueryInput';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { generateId } from '@/lib/utils';

export interface ChatInterfaceProps {
  className?: string;
}

/**
 * ChatInterface Component
 *
 * Complete chat interface with:
 * - WebSocket integration for streaming responses
 * - Message history management
 * - Query input with submit
 * - Clear chat functionality
 * - Auto-scroll to latest message
 *
 * @example
 * ```tsx
 * <ChatInterface />
 * ```
 */
export function ChatInterface({ className }: ChatInterfaceProps) {
  const { sendQuery, response, isStreaming, error, isConnected, clear } =
    useWebSocketQuery();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentAssistantMessageId, setCurrentAssistantMessageId] = useState<
    string | null
  >(null);

  /**
   * Handle query submission
   */
  const handleSubmit = useCallback(
    (query: string) => {
      if (!isConnected) {
        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: 'system',
            content: 'Not connected to WebSocket. Please wait for connection...',
            timestamp: new Date(),
          },
        ]);
        return;
      }

      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Create assistant message placeholder
      const assistantMessageId = generateId();
      setCurrentAssistantMessageId(assistantMessageId);

      const assistantMessage: ChatMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Send query to WebSocket
      sendQuery(query);
    },
    [isConnected, sendQuery]
  );

  /**
   * Update assistant message with streaming response
   */
  useEffect(() => {
    console.log('[ChatInterface] useEffect triggered - currentAssistantMessageId:', currentAssistantMessageId, 'response length:', response.length, 'isStreaming:', isStreaming);
    if (currentAssistantMessageId && response) {
      console.log('[ChatInterface] Updating message with response:', response.substring(0, 50) + '...');
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === currentAssistantMessageId
            ? { ...msg, content: response, isStreaming }
            : msg
        )
      );
    } else {
      console.log('[ChatInterface] Skipping update - currentAssistantMessageId:', currentAssistantMessageId, 'response:', response.length);
    }
  }, [response, isStreaming, currentAssistantMessageId]);

  /**
   * Handle errors
   */
  useEffect(() => {
    if (error && currentAssistantMessageId) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === currentAssistantMessageId
            ? {
                ...msg,
                content: `Error: ${error}`,
                isStreaming: false,
              }
            : msg
        )
      );
      setCurrentAssistantMessageId(null);
    }
  }, [error, currentAssistantMessageId]);

  /**
   * NOTE: We intentionally do NOT clear currentAssistantMessageId when streaming completes.
   * This was causing a race condition where the ID would be cleared before final response
   * updates could propagate. The ID will be reset naturally when the next query is sent.
   */

  /**
   * Clear all messages
   */
  const handleClearChat = useCallback(() => {
    setMessages([]);
    setCurrentAssistantMessageId(null);
    clear();
  }, [clear]);

  return (
    <Card
      variant="glass"
      padding="none"
      className={cn('flex flex-col h-full', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white font-semibold">
            AI
          </div>
          <div>
            <h2 className="font-heading font-semibold text-slate-200">
              Risk Agent
            </h2>
            <p className="text-xs text-slate-400">
              {isConnected ? (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  Connected
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-red-500"></span>
                  Disconnected
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearChat}
            disabled={messages.length === 0}
          >
            Clear Chat
          </Button>
        </div>
      </div>

      {/* Messages */}
      <MessageList messages={messages} className="flex-1" />

      {/* Input */}
      <QueryInput onSubmit={handleSubmit} disabled={isStreaming || !isConnected} />
    </Card>
  );
}
