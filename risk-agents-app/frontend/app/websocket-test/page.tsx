/**
 * WebSocket Test Page
 * Test and demonstrate WebSocket functionality
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket, useStreamingQuery } from '@/lib/websocket/hooks';
import {
  ConnectionStatus,
  ConnectionStatusCard,
  MiniConnectionStatus,
} from '@/components/websocket/ConnectionStatus';
import type {
  ChunkMessage,
  CompleteMessage,
  ErrorMessage,
  QueryStartMessage,
  ConnectedMessage,
} from '@/lib/websocket/types';

export default function WebSocketTestPage() {
  const [sessionId, setSessionId] = useState('');
  const [query, setQuery] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [isQueryActive, setIsQueryActive] = useState(false);
  const [chunkCount, setChunkCount] = useState(0);
  const [fullResponse, setFullResponse] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [lastPing, setLastPing] = useState<Date | null>(null);
  const [autoConnect, setAutoConnect] = useState(false);

  // Generate session ID on client side only (fixes hydration error)
  useEffect(() => {
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  // Example queries
  const exampleQueries = [
    'What is risk management?',
    'Explain the three lines of defense model',
    'What are the key principles of operational risk management?',
    'How do you calculate Value at Risk (VaR)?',
  ];

  // WebSocket connection (only initialize after sessionId is set to avoid hydration errors)
  const { status, sendQuery, connect, disconnect, queueSize, isConnected } =
    useWebSocket(
      {
        url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8050',
        sessionId: sessionId || 'loading',
        userId: 'test-user-1',
        autoReconnect: true,
        maxReconnectAttempts: 5,
      },
      {
        onConnected: (message: ConnectedMessage) => {
          console.log('✅ Connected:', message);
          setErrorMessage('');
        },
        onQueryStart: (message: QueryStartMessage) => {
          console.log('🚀 Query started:', message.query);
          setIsQueryActive(true);
          setStreamingText('');
          setChunkCount(0);
          setFullResponse('');
          setErrorMessage('');
        },
        onChunk: (message: ChunkMessage) => {
          setStreamingText((prev) => prev + message.content);
          setChunkCount(message.chunk_number);
        },
        onComplete: (message: CompleteMessage) => {
          console.log(
            '✅ Query complete:',
            message.total_chunks,
            'chunks'
          );
          setIsQueryActive(false);
          setFullResponse(message.full_response);
        },
        onError: (message: ErrorMessage) => {
          console.error('❌ Error:', message.error);
          setIsQueryActive(false);
          setErrorMessage(message.error);
        },
        onPong: () => {
          setLastPing(new Date());
        },
        onDisconnected: () => {
          console.log('Disconnected from WebSocket');
        },
      }
    );

  // Auto-connect on mount if enabled (wait for sessionId to be ready)
  useEffect(() => {
    if (autoConnect && status === 'disconnected' && sessionId) {
      connect();
    }
  }, [autoConnect, connect, status, sessionId]);

  const handleSendQuery = () => {
    if (!query.trim()) return;

    sendQuery(query, {
      systemPrompt:
        'You are a helpful AI assistant specialized in risk management.',
      includeContext: true,
    });
  };

  const handleExampleQuery = (exampleQuery: string) => {
    setQuery(exampleQuery);
    if (isConnected) {
      sendQuery(exampleQuery, {
        systemPrompt:
          'You are a helpful AI assistant specialized in risk management.',
        includeContext: true,
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h1 className="font-heading text-hero font-bold text-slate-200">
              WebSocket Test
            </h1>
            <MiniConnectionStatus status={status} />
          </div>
          <p className="text-slate-400">
            Test real-time streaming queries with WebSocket
          </p>
          <div className="flex gap-2 mt-2 text-xs text-slate-500">
            <span className="badge-circuit">Session: {sessionId}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Controls */}
          <div className="space-y-6">
            {/* Connection Status */}
            <ConnectionStatusCard
              status={status}
              queueSize={queueSize}
              lastPing={lastPing || undefined}
            />

            {/* Connection Controls */}
            <div className="glass-card p-4">
              <h3 className="font-heading font-semibold text-slate-200 mb-4">
                Connection Controls
              </h3>

              <div className="flex gap-2 mb-4">
                <button
                  onClick={connect}
                  disabled={status === 'connected' || status === 'connecting'}
                  className="flex-1 gradient-button px-4 py-2 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {status === 'connecting' ? 'Connecting...' : 'Connect'}
                </button>
                <button
                  onClick={disconnect}
                  disabled={status === 'disconnected'}
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Disconnect
                </button>
              </div>

              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoConnect}
                  onChange={(e) => setAutoConnect(e.target.checked)}
                  className="w-4 h-4"
                />
                Auto-connect on page load
              </label>
            </div>

            {/* Query Input */}
            <div className="glass-card p-4">
              <h3 className="font-heading font-semibold text-slate-200 mb-4">
                Send Query
              </h3>

              <div className="space-y-3">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                      handleSendQuery();
                    }
                  }}
                  placeholder="Enter your query... (Ctrl+Enter to send)"
                  className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none"
                  rows={4}
                  disabled={!isConnected}
                />

                <button
                  onClick={handleSendQuery}
                  disabled={!isConnected || !query.trim() || isQueryActive}
                  className="w-full gradient-button px-4 py-3 rounded-lg font-semibold text-base disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isQueryActive ? '⚡ Streaming...' : '🚀 Send Query'}
                </button>

                {!isConnected && (
                  <p className="text-sm text-yellow-500">
                    ⚠️ Connect to WebSocket first
                  </p>
                )}

                {/* API Key Warning */}
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-300">
                  <p className="font-semibold mb-1">ℹ️ Note: Backend API Key Required</p>
                  <p className="text-xs text-blue-400">
                    Query execution requires an Anthropic API key in the backend. The WebSocket connection will work, but queries may fail with a 401 authentication error if the backend doesn't have <code className="bg-slate-800 px-1 rounded">ANTHROPIC_API_KEY</code> configured.
                  </p>
                </div>
              </div>
            </div>

            {/* Example Queries */}
            <div className="glass-card p-4">
              <h3 className="font-heading font-semibold text-slate-200 mb-4">
                Example Queries
              </h3>

              <div className="space-y-2">
                {exampleQueries.map((exampleQuery, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleQuery(exampleQuery)}
                    disabled={!isConnected || isQueryActive}
                    className="w-full text-left px-3 py-2 bg-slate-800/30 hover:bg-slate-800/50 border border-slate-700/50 rounded-lg text-sm text-slate-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {exampleQuery}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Response */}
          <div className="space-y-6">
            {/* Streaming Response */}
            <div className="glass-card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-heading font-semibold text-slate-200">
                  Response
                </h3>
                {isQueryActive && (
                  <span className="flex items-center gap-2 text-sm text-blue-400">
                    <div className="w-2 h-2 bg-blue-500 rounded-full led-blink" />
                    Streaming... ({chunkCount} chunks)
                  </span>
                )}
              </div>

              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
                {streamingText ? (
                  <div className="text-slate-200 whitespace-pre-wrap">
                    {streamingText}
                    {isQueryActive && (
                      <span className="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse" />
                    )}
                  </div>
                ) : (
                  <div className="text-center text-slate-500 py-12">
                    {isConnected
                      ? 'Send a query to see streaming response'
                      : 'Connect to WebSocket to start'}
                  </div>
                )}
              </div>

              {errorMessage && (
                <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                  ❌ Error: {errorMessage}
                </div>
              )}

              {fullResponse && !isQueryActive && (
                <div className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">
                  ✅ Complete ({chunkCount} chunks,{' '}
                  {fullResponse.length} characters)
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="glass-card p-4">
              <h3 className="font-heading font-semibold text-slate-200 mb-4">
                Statistics
              </h3>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-slate-500 mb-1">Status</div>
                  <div className="text-slate-200 font-medium">
                    <ConnectionStatus status={status} size="sm" />
                  </div>
                </div>

                <div>
                  <div className="text-slate-500 mb-1">Queued Messages</div>
                  <div className="text-slate-200 font-medium">{queueSize}</div>
                </div>

                <div>
                  <div className="text-slate-500 mb-1">Chunks Received</div>
                  <div className="text-slate-200 font-medium">{chunkCount}</div>
                </div>

                <div>
                  <div className="text-slate-500 mb-1">Characters</div>
                  <div className="text-slate-200 font-medium">
                    {streamingText.length}
                  </div>
                </div>
              </div>
            </div>

            {/* Help */}
            <div className="glass-card p-4 text-xs text-slate-400">
              <h4 className="font-semibold text-slate-300 mb-2">💡 Tips</h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>Connect to WebSocket before sending queries</li>
                <li>Use Ctrl+Enter to quickly send queries</li>
                <li>Try example queries for quick testing</li>
                <li>Connection auto-reconnects on disconnect</li>
                <li>Messages are queued if sent while offline</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
