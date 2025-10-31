/**
 * Loading Components
 * Spinner, Skeleton, and loading state components
 */

'use client';

import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerVariant = 'primary' | 'white' | 'slate';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  /** Spinner size */
  size?: SpinnerSize;
  /** Spinner color variant */
  variant?: SpinnerVariant;
  /** Center the spinner */
  center?: boolean;
}

/**
 * Spinner Component
 *
 * Animated loading spinner with multiple sizes and colors
 *
 * @example
 * ```tsx
 * <Spinner size="md" />
 * <Spinner size="lg" variant="white" center />
 * ```
 */
export function Spinner({
  size = 'md',
  variant = 'primary',
  center = false,
  className,
  ...props
}: SpinnerProps) {
  const sizeClasses = {
    xs: 'w-3 h-3 border-2',
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4',
  };

  const variantClasses = {
    primary: 'border-blue-500 border-t-transparent',
    white: 'border-white border-t-transparent',
    slate: 'border-slate-400 border-t-transparent',
  };

  return (
    <div
      className={cn(center && 'flex items-center justify-center')}
      {...props}
    >
      <div
        className={cn(
          'rounded-full animate-spin',
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        role="status"
        aria-label="Loading"
      />
    </div>
  );
}

/**
 * LoadingText Component
 *
 * Spinner with accompanying text
 */
export interface LoadingTextProps {
  text?: string;
  size?: SpinnerSize;
  variant?: SpinnerVariant;
  className?: string;
}

export function LoadingText({
  text = 'Loading...',
  size = 'md',
  variant = 'primary',
  className,
}: LoadingTextProps) {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <Spinner size={size} variant={variant} />
      <span className="text-slate-300">{text}</span>
    </div>
  );
}

/**
 * FullPageLoader Component
 *
 * Full-page loading overlay
 */
export interface FullPageLoaderProps {
  text?: string;
  variant?: SpinnerVariant;
}

export function FullPageLoader({
  text = 'Loading...',
  variant = 'primary',
}: FullPageLoaderProps) {
  return (
    <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="xl" variant={variant} />
        <p className="text-lg text-slate-200">{text}</p>
      </div>
    </div>
  );
}

/**
 * Skeleton Component
 *
 * Placeholder skeleton for loading content
 *
 * @example
 * ```tsx
 * <Skeleton className="h-4 w-32" />
 * <Skeleton variant="circular" className="w-12 h-12" />
 * <Skeleton variant="text" count={3} />
 * ```
 */
export type SkeletonVariant = 'rectangular' | 'circular' | 'text';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /** Skeleton variant */
  variant?: SkeletonVariant;
  /** Number of skeleton lines (for text variant) */
  count?: number;
  /** Animation enabled */
  animate?: boolean;
}

export function Skeleton({
  variant = 'rectangular',
  count = 1,
  animate = true,
  className,
  ...props
}: SkeletonProps) {
  const variantClasses = {
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
    text: 'rounded h-4',
  };

  // For text variant with multiple lines
  if (variant === 'text' && count > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className={cn(
              'bg-slate-800/50',
              variantClasses.text,
              animate && 'animate-pulse',
              // Last line is shorter
              i === count - 1 ? 'w-3/4' : 'w-full'
            )}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-slate-800/50',
        variantClasses[variant],
        animate && 'animate-pulse',
        className
      )}
      {...props}
    />
  );
}

/**
 * SkeletonCard Component
 *
 * Pre-configured skeleton for card layouts
 */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('glass-card p-4', className)}>
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <Skeleton variant="circular" className="w-12 h-12 flex-shrink-0" />

        {/* Content */}
        <div className="flex-1 space-y-2">
          {/* Title */}
          <Skeleton className="h-5 w-3/4" />
          {/* Description */}
          <Skeleton variant="text" count={2} />
        </div>
      </div>

      {/* Footer */}
      <div className="flex gap-2 mt-4">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
}

/**
 * SkeletonTable Component
 *
 * Pre-configured skeleton for table layouts
 */
export interface SkeletonTableProps {
  rows?: number;
  cols?: number;
  className?: string;
}

export function SkeletonTable({
  rows = 5,
  cols = 4,
  className,
}: SkeletonTableProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={`header-${i}`} className="h-8" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="grid gap-4"
          style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
        >
          {Array.from({ length: cols }).map((_, colIndex) => (
            <Skeleton key={`cell-${rowIndex}-${colIndex}`} className="h-10" />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * LoadingState Component
 *
 * Wrapper component that shows loading state or children
 */
export interface LoadingStateProps {
  /** Whether data is loading */
  isLoading: boolean;
  /** Loading component to show */
  loader?: React.ReactNode;
  /** Content to show when not loading */
  children: React.ReactNode;
}

export function LoadingState({
  isLoading,
  loader,
  children,
}: LoadingStateProps) {
  if (isLoading) {
    return <>{loader || <LoadingText />}</>;
  }

  return <>{children}</>;
}

/**
 * ProgressBar Component
 *
 * Linear progress indicator
 */
export interface ProgressBarProps {
  /** Progress value (0-100) */
  value: number;
  /** Show percentage text */
  showLabel?: boolean;
  /** Color variant */
  variant?: 'primary' | 'success' | 'warning' | 'error';
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ProgressBar({
  value,
  showLabel = false,
  variant = 'primary',
  size = 'md',
  className,
}: ProgressBarProps) {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const variantClasses = {
    primary: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  // Clamp value between 0 and 100
  const clampedValue = Math.min(Math.max(value, 0), 100);

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between mb-1 text-xs text-slate-400">
          <span>Progress</span>
          <span>{clampedValue}%</span>
        </div>
      )}
      <div
        className={cn(
          'w-full bg-slate-800 rounded-full overflow-hidden',
          sizeClasses[size]
        )}
      >
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out',
            variantClasses[variant]
          )}
          style={{ width: `${clampedValue}%` }}
          role="progressbar"
          aria-valuenow={clampedValue}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}

/**
 * Dots Loader Component
 *
 * Animated dots loading indicator
 */
export function DotsLoader({ className }: { className?: string }) {
  return (
    <div className={cn('flex gap-1', className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
          style={{
            animationDelay: `${i * 0.15}s`,
          }}
        />
      ))}
    </div>
  );
}
