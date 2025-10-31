/**
 * WebSocketContext
 * Global WebSocket connection management using React Context
 */

'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  ReactNode,
} from 'react';
import { WebSocketClient } from '@/lib/websocket/client';
import {
  ConnectionStatus,
  WebSocketConfig,
  ServerMessage,
  QueryOptions,
} from '@/lib/websocket/types';

interface WebSocketContextType {
  // State
  status: ConnectionStatus;
  isConnected: boolean;
  queueSize: number;
  lastPing: Date | null;
  sessionId: string;

  // Connection management
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;

  // Messaging
  sendQuery: (query: string, options?: QueryOptions) => void;

  // Event listeners
  onMessage: (handler: (message: ServerMessage) => void) => () => void;
  onStatusChange: (handler: (status: ConnectionStatus) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

/**
 * useWebSocketContext Hook
 *
 * Access WebSocket connection state and methods
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { isConnected, sendQuery, status } = useWebSocketContext();
 *
 *   const handleQuery = () => {
 *     if (isConnected) {
 *       sendQuery('What is risk management?');
 *     }
 *   };
 *
 *   return (
 *     <div>
 *       Status: {status}
 *       <button onClick={handleQuery}>Send Query</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error(
      'useWebSocketContext must be used within a WebSocketProvider'
    );
  }
  return context;
}

/**
 * WebSocketProvider Component
 *
 * Wrap your app with this provider to enable global WebSocket connection
 *
 * @example
 * ```tsx
 * // In app/layout.tsx
 * <WebSocketProvider autoConnect={false}>
 *   <App />
 * </WebSocketProvider>
 * ```
 */
export interface WebSocketProviderProps {
  children: ReactNode;
  /** Automatically connect on mount */
  autoConnect?: boolean;
  /** Custom WebSocket URL (defaults to env variable) */
  url?: string;
  /** Custom session ID (auto-generated if not provided) */
  sessionId?: string;
  /** User ID for connection */
  userId?: string;
}

export function WebSocketProvider({
  children,
  autoConnect = false,
  url,
  sessionId: customSessionId,
  userId,
}: WebSocketProviderProps) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [queueSize, setQueueSize] = useState(0);
  const [lastPing, setLastPing] = useState<Date | null>(null);
  const [sessionId, setSessionId] = useState('');

  const clientRef = useRef<WebSocketClient | null>(null);
  const messageHandlersRef = useRef<Set<(message: ServerMessage) => void>>(
    new Set()
  );
  const statusHandlersRef = useRef<Set<(status: ConnectionStatus) => void>>(
    new Set()
  );

  const isConnected = status === 'connected';

  /**
   * Debug: Log status changes
   */
  useEffect(() => {
    console.log(`[WebSocketContext] Status state changed to: ${status}, isConnected: ${isConnected}`);
  }, [status, isConnected]);

  /**
   * Initialize session ID on mount (client-side only)
   */
  useEffect(() => {
    if (customSessionId) {
      setSessionId(customSessionId);
    } else {
      setSessionId(
        `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      );
    }
  }, [customSessionId]);

  /**
   * Initialize WebSocket client when session ID is available
   */
  useEffect(() => {
    if (!sessionId) return;

    const wsUrl = url || process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8050';

    const config: WebSocketConfig = {
      url: wsUrl,
      sessionId,
      userId,
      autoReconnect: true,
      maxReconnectAttempts: 10,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      pingInterval: 30000,
      connectionTimeout: 10000,
    };

    const client = new WebSocketClient(config);

    // Set up event handlers
    client.on('onConnected', (message) => {
      console.log('[WebSocketContext] Connected event received, calling setStatus');
      setStatus('connected');
      messageHandlersRef.current.forEach((handler) => handler(message));
      statusHandlersRef.current.forEach((handler) => handler('connected'));
    });

    client.on('onDisconnected', (message) => {
      setStatus('disconnected');
      messageHandlersRef.current.forEach((handler) => handler(message));
      statusHandlersRef.current.forEach((handler) => handler('disconnected'));
    });

    client.on('onChunk', (message) => {
      console.log('[WebSocketContext] Chunk received, calling', messageHandlersRef.current.size, 'handlers');
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('onComplete', (message) => {
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('onError', (message) => {
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('onQueryStart', (message) => {
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('pong', (message) => {
      setLastPing(new Date());
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('keepalive', (message) => {
      messageHandlersRef.current.forEach((handler) => handler(message));
    });

    client.on('statusChange', (newStatus) => {
      setStatus(newStatus);
      statusHandlersRef.current.forEach((handler) => handler(newStatus));
    });

    client.on('queueSizeChange', (size) => {
      setQueueSize(size);
    });

    clientRef.current = client;

    // Auto-connect if enabled
    if (autoConnect) {
      client.connect();
    }

    // Cleanup on unmount
    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
        clientRef.current = null;
      }
    };
  }, [sessionId, url, userId, autoConnect]);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.connect();
    }
  }, []);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
    }
  }, []);

  /**
   * Reconnect WebSocket
   */
  const reconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
      setTimeout(() => {
        clientRef.current?.connect();
      }, 500);
    }
  }, []);

  /**
   * Send query through WebSocket
   */
  const sendQuery = useCallback((query: string, options?: QueryOptions) => {
    if (clientRef.current) {
      clientRef.current.sendQuery(query, options);
    }
  }, []);

  /**
   * Subscribe to WebSocket messages
   */
  const onMessage = useCallback(
    (handler: (message: ServerMessage) => void) => {
      console.log('[WebSocketContext] onMessage: Adding handler, total handlers:', messageHandlersRef.current.size + 1);
      messageHandlersRef.current.add(handler);
      return () => {
        messageHandlersRef.current.delete(handler);
      };
    },
    []
  );

  /**
   * Subscribe to status changes
   */
  const onStatusChange = useCallback(
    (handler: (status: ConnectionStatus) => void) => {
      statusHandlersRef.current.add(handler);
      return () => {
        statusHandlersRef.current.delete(handler);
      };
    },
    []
  );

  const value: WebSocketContextType = {
    status,
    isConnected,
    queueSize,
    lastPing,
    sessionId,
    connect,
    disconnect,
    reconnect,
    sendQuery,
    onMessage,
    onStatusChange,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * useWebSocketQuery Hook
 *
 * Simplified hook for sending queries and receiving responses
 *
 * @example
 * ```tsx
 * function QueryComponent() {
 *   const { sendQuery, response, isStreaming, error } = useWebSocketQuery();
 *
 *   const handleSubmit = () => {
 *     sendQuery('What is machine learning?');
 *   };
 *
 *   return (
 *     <div>
 *       <button onClick={handleSubmit}>Ask Question</button>
 *       {isStreaming && <LoadingText text="Streaming..." />}
 *       {response && <div>{response}</div>}
 *       {error && <div>Error: {error}</div>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useWebSocketQuery() {
  const { sendQuery: contextSendQuery, onMessage, isConnected } = useWebSocketContext();
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debug: Log when response changes
  useEffect(() => {
    console.log('[useWebSocketQuery] Response state changed, length:', response.length, 'isStreaming:', isStreaming);
  }, [response, isStreaming]);

  useEffect(() => {
    console.log('[useWebSocketQuery] Setting up message handler');
    const unsubscribe = onMessage((message) => {
      console.log('[useWebSocketQuery] Received message:', message.type);
      switch (message.type) {
        case 'query_start':
          console.log('[useWebSocketQuery] Query start - resetting response');
          setResponse('');
          setIsStreaming(true);
          setError(null);
          break;

        case 'chunk':
          // Server sends chunks with 'content' field
          if ('content' in message) {
            const content = (message as any).content;
            console.log('[useWebSocketQuery] Chunk with content:', content);
            setResponse((prev) => {
              const newResponse = prev + content;
              console.log('[useWebSocketQuery] Updated response length:', newResponse.length);
              return newResponse;
            });
          } else if ('text' in message) {
            setResponse((prev) => prev + (message as any).text);
          } else {
            console.warn('[useWebSocketQuery] Chunk has no content or text field:', message);
          }
          break;

        case 'complete':
          setIsStreaming(false);
          if ('full_response' in message) {
            setResponse(message.full_response);
          }
          break;

        case 'error':
          setIsStreaming(false);
          if ('error' in message) {
            setError(message.error);
          }
          break;
      }
    });

    return unsubscribe;
  }, [onMessage]);

  const sendQuery = useCallback(
    (query: string, options?: QueryOptions) => {
      if (!isConnected) {
        setError('Not connected to WebSocket');
        return;
      }
      setResponse('');
      setError(null);
      contextSendQuery(query, options);
    },
    [contextSendQuery, isConnected]
  );

  const clear = useCallback(() => {
    setResponse('');
    setError(null);
    setIsStreaming(false);
  }, []);

  return {
    sendQuery,
    response,
    isStreaming,
    error,
    isConnected,
    clear,
  };
}
