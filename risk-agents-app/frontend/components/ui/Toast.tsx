/**
 * Toast Notification System
 * Toast notifications with multiple variants and positions
 */

'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type ToastVariant = 'info' | 'success' | 'warning' | 'error';
export type ToastPosition =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right';

export interface Toast {
  id: string;
  title?: string;
  message: string;
  variant?: ToastVariant;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

/**
 * useToast Hook
 *
 * Access toast notification functions
 *
 * @example
 * ```tsx
 * const { addToast } = useToast();
 *
 * addToast({
 *   message: 'Success!',
 *   variant: 'success',
 *   duration: 3000
 * });
 * ```
 */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * ToastProvider Component
 *
 * Wrap your app with this provider to enable toasts
 */
export interface ToastProviderProps {
  children: ReactNode;
  position?: ToastPosition;
  maxToasts?: number;
}

export function ToastProvider({
  children,
  position = 'top-right',
  maxToasts = 5,
}: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const newToast: Toast = {
        id,
        variant: 'info',
        duration: 5000,
        ...toast,
      };

      setToasts((prev) => {
        const updated = [...prev, newToast];
        // Limit to maxToasts
        if (updated.length > maxToasts) {
          return updated.slice(-maxToasts);
        }
        return updated;
      });

      // Auto-remove after duration
      if (newToast.duration && newToast.duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, newToast.duration);
      }
    },
    [maxToasts]
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearToasts }}>
      {children}
      <ToastContainer position={position} toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

/**
 * ToastContainer Component
 *
 * Container for displaying toasts
 */
interface ToastContainerProps {
  position: ToastPosition;
  toasts: Toast[];
  onRemove: (id: string) => void;
}

function ToastContainer({ position, toasts, onRemove }: ToastContainerProps) {
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    'bottom-right': 'bottom-4 right-4',
  };

  if (toasts.length === 0) return null;

  return (
    <div
      className={cn(
        'fixed z-50 flex flex-col gap-2',
        'max-w-sm w-full',
        positionClasses[position]
      )}
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

/**
 * ToastItem Component
 *
 * Individual toast notification
 */
interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const variantConfig = {
    info: {
      icon: 'ℹ️',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      iconColor: 'text-blue-400',
    },
    success: {
      icon: '✅',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
      iconColor: 'text-green-400',
    },
    warning: {
      icon: '⚠️',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30',
      iconColor: 'text-yellow-400',
    },
    error: {
      icon: '❌',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      iconColor: 'text-red-400',
    },
  };

  const config = variantConfig[toast.variant || 'info'];

  return (
    <div
      className={cn(
        'glass-card p-4 border',
        'animate-in slide-in-from-top-2 fade-in duration-200',
        config.bgColor,
        config.borderColor
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <span className={cn('text-lg flex-shrink-0', config.iconColor)}>
          {config.icon}
        </span>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {toast.title && (
            <h4 className="font-semibold text-slate-200 mb-1">
              {toast.title}
            </h4>
          )}
          <p className="text-sm text-slate-300">{toast.message}</p>

          {/* Action Button */}
          {toast.action && (
            <button
              onClick={() => {
                toast.action!.onClick();
                onRemove(toast.id);
              }}
              className="mt-2 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors"
            >
              {toast.action.label}
            </button>
          )}
        </div>

        {/* Close Button */}
        <button
          onClick={() => onRemove(toast.id)}
          className="flex-shrink-0 text-slate-400 hover:text-slate-200 transition-colors"
          aria-label="Close"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Convenience hook for common toast operations
 */
export function useToastHelpers() {
  const { addToast } = useToast();

  return {
    info: (message: string, title?: string) =>
      addToast({ message, title, variant: 'info' }),
    success: (message: string, title?: string) =>
      addToast({ message, title, variant: 'success' }),
    warning: (message: string, title?: string) =>
      addToast({ message, title, variant: 'warning' }),
    error: (message: string, title?: string) =>
      addToast({ message, title, variant: 'error' }),
  };
}
