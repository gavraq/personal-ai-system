/**
 * WebSocket Connection Status Indicator
 * Visual indicator for WebSocket connection status
 */

'use client';

import { ConnectionStatus } from '@/lib/websocket/types';

export interface ConnectionStatusProps {
  /** Current connection status */
  status: ConnectionStatus;
  /** Show status text (default: true) */
  showText?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Custom className */
  className?: string;
}

/**
 * ConnectionStatus Component
 *
 * Displays the current WebSocket connection status with an LED indicator
 *
 * @example
 * ```tsx
 * <ConnectionStatus status="connected" />
 * <ConnectionStatus status="reconnecting" size="lg" />
 * <ConnectionStatus status="error" showText={false} />
 * ```
 */
export function ConnectionStatus({
  status,
  showText = true,
  size = 'md',
  className = '',
}: ConnectionStatusProps) {
  // LED indicator size classes
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  // Text size classes
  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  // Status configuration
  const statusConfig = {
    disconnected: {
      color: 'gray',
      bgColor: 'bg-gray-500',
      text: 'Disconnected',
      blink: false,
    },
    connecting: {
      color: 'yellow',
      bgColor: 'bg-yellow-500',
      text: 'Connecting...',
      blink: true,
    },
    connected: {
      color: 'green',
      bgColor: 'bg-green-500',
      text: 'Connected',
      blink: false,
    },
    reconnecting: {
      color: 'orange',
      bgColor: 'bg-orange-500',
      text: 'Reconnecting...',
      blink: true,
    },
    error: {
      color: 'red',
      bgColor: 'bg-red-500',
      text: 'Connection Error',
      blink: true,
    },
  };

  const config = statusConfig[status];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* LED Indicator */}
      <div
        className={`
          ${sizeClasses[size]}
          ${config.bgColor}
          rounded-full
          ${config.blink ? 'led-blink' : ''}
          shadow-elegant-sm
        `}
        title={config.text}
      />

      {/* Status Text */}
      {showText && (
        <span
          className={`
            ${textSizeClasses[size]}
            text-slate-300
            font-medium
          `}
        >
          {config.text}
        </span>
      )}
    </div>
  );
}

/**
 * Mini Connection Status Indicator
 * Compact version for headers/nav bars
 */
export function MiniConnectionStatus({
  status,
  className = '',
}: {
  status: ConnectionStatus;
  className?: string;
}) {
  return (
    <ConnectionStatus
      status={status}
      size="sm"
      showText={false}
      className={className}
    />
  );
}

/**
 * Detailed Connection Status Card
 * Full status card with additional information
 */
export function ConnectionStatusCard({
  status,
  queueSize = 0,
  lastPing,
  className = '',
}: {
  status: ConnectionStatus;
  queueSize?: number;
  lastPing?: Date;
  className?: string;
}) {
  const statusConfig = {
    disconnected: {
      title: 'Disconnected',
      description: 'WebSocket is not connected',
      icon: '⭕',
    },
    connecting: {
      title: 'Connecting',
      description: 'Establishing WebSocket connection...',
      icon: '🔄',
    },
    connected: {
      title: 'Connected',
      description: 'WebSocket is connected and ready',
      icon: '✅',
    },
    reconnecting: {
      title: 'Reconnecting',
      description: 'Attempting to reconnect...',
      icon: '🔄',
    },
    error: {
      title: 'Connection Error',
      description: 'Failed to connect to WebSocket server',
      icon: '❌',
    },
  };

  const config = statusConfig[status];

  return (
    <div className={`glass-card p-4 ${className}`}>
      <div className="flex items-start gap-3">
        {/* Status Indicator */}
        <ConnectionStatus status={status} size="md" showText={false} />

        {/* Status Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{config.icon}</span>
            <h3 className="font-heading font-semibold text-slate-200">
              {config.title}
            </h3>
          </div>

          <p className="text-sm text-slate-400 mb-3">{config.description}</p>

          {/* Additional Details */}
          <div className="flex gap-4 text-xs text-slate-500">
            {queueSize > 0 && (
              <div className="flex items-center gap-1">
                <span className="badge-ai">Queue</span>
                <span>{queueSize} messages</span>
              </div>
            )}

            {lastPing && status === 'connected' && (
              <div className="flex items-center gap-1">
                <span className="badge-retro">Ping</span>
                <span>{formatTimeSince(lastPing)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Format time since a date
 */
function formatTimeSince(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}
