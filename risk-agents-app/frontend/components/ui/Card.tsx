/**
 * Card Component
 * Reusable card component with different layouts and styles
 */

'use client';

import { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type CardVariant = 'default' | 'glass' | 'elevated' | 'bordered' | 'gradient';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Card variant (affects styling) */
  variant?: CardVariant;
  /** Padding size */
  padding?: CardPadding;
  /** Hover effect */
  hoverable?: boolean;
  /** Clickable card */
  clickable?: boolean;
  children?: ReactNode;
}

/**
 * Card Component
 *
 * A flexible card container with:
 * - Multiple style variants (default, glass, elevated, bordered, gradient)
 * - Padding options (none, sm, md, lg)
 * - Hover effects
 * - Clickable support
 *
 * @example
 * ```tsx
 * <Card>
 *   <CardHeader>
 *     <CardTitle>Card Title</CardTitle>
 *     <CardDescription>Card description</CardDescription>
 *   </CardHeader>
 *   <CardContent>
 *     Card content goes here
 *   </CardContent>
 *   <CardFooter>
 *     <Button>Action</Button>
 *   </CardFooter>
 * </Card>
 * ```
 */
export function Card({
  variant = 'default',
  padding = 'md',
  hoverable = false,
  clickable = false,
  className,
  children,
  ...props
}: CardProps) {
  // Variant styles
  const variantClasses = {
    default: 'bg-slate-800/50 border border-slate-700',
    glass: 'glass-card',
    elevated: 'bg-slate-800 card-lift shadow-elegant-lg',
    bordered: 'bg-slate-900 border-2 border-slate-700',
    gradient: 'bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50',
  };

  // Padding classes
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(
        // Base styles
        'rounded-lg transition-all duration-200',

        // Variant
        variantClasses[variant],

        // Padding
        paddingClasses[padding],

        // Hoverable
        hoverable &&
          'hover:shadow-elegant-xl hover:-translate-y-0.5',

        // Clickable
        clickable && 'cursor-pointer hover:border-blue-500/50',

        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * CardHeader Component
 *
 * Card header section with title and description
 */
export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
}

export function CardHeader({ className, children, ...props }: CardHeaderProps) {
  return (
    <div
      className={cn('flex flex-col gap-1.5 pb-4', className)}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * CardTitle Component
 *
 * Card title with heading styles
 */
export interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children?: ReactNode;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export function CardTitle({
  as: Component = 'h3',
  className,
  children,
  ...props
}: CardTitleProps) {
  return (
    <Component
      className={cn(
        'font-heading font-semibold text-slate-200 text-lg',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

/**
 * CardDescription Component
 *
 * Card description with muted text
 */
export interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children?: ReactNode;
}

export function CardDescription({
  className,
  children,
  ...props
}: CardDescriptionProps) {
  return (
    <p
      className={cn('text-sm text-slate-400', className)}
      {...props}
    >
      {children}
    </p>
  );
}

/**
 * CardContent Component
 *
 * Card content area
 */
export interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
}

export function CardContent({ className, children, ...props }: CardContentProps) {
  return (
    <div className={cn('text-slate-300', className)} {...props}>
      {children}
    </div>
  );
}

/**
 * CardFooter Component
 *
 * Card footer section for actions
 */
export interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
}

export function CardFooter({ className, children, ...props }: CardFooterProps) {
  return (
    <div
      className={cn('flex items-center gap-2 pt-4', className)}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * StatCard Component
 *
 * Specialized card for displaying statistics
 */
export interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function StatCard({
  title,
  value,
  description,
  icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card variant="glass" className={className}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-slate-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-slate-200">{value}</p>
          {description && (
            <p className="text-xs text-slate-500 mt-1">{description}</p>
          )}
        </div>

        {icon && (
          <div className="text-slate-400 opacity-50 w-8 h-8">
            {icon}
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          <span
            className={cn(
              'font-semibold',
              trend.isPositive ? 'text-green-400' : 'text-red-400'
            )}
          >
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="text-slate-500">vs last period</span>
        </div>
      )}
    </Card>
  );
}

/**
 * InfoCard Component
 *
 * Specialized card for displaying information with icons
 */
export interface InfoCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  variant?: 'info' | 'success' | 'warning' | 'error';
  className?: string;
}

export function InfoCard({
  icon,
  title,
  description,
  variant = 'info',
  className,
}: InfoCardProps) {
  const variantClasses = {
    info: 'border-blue-500/30 bg-blue-500/5',
    success: 'border-green-500/30 bg-green-500/5',
    warning: 'border-yellow-500/30 bg-yellow-500/5',
    error: 'border-red-500/30 bg-red-500/5',
  };

  const iconColorClasses = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  };

  return (
    <Card
      variant="bordered"
      className={cn(variantClasses[variant], className)}
    >
      <div className="flex gap-3">
        <div className={cn('flex-shrink-0 w-5 h-5', iconColorClasses[variant])}>
          {icon}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-slate-200 mb-1">{title}</h4>
          <p className="text-sm text-slate-400">{description}</p>
        </div>
      </div>
    </Card>
  );
}

/**
 * CardGrid Component
 *
 * Grid layout for cards
 */
export interface CardGridProps extends HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4;
  children?: ReactNode;
}

export function CardGrid({
  cols = 3,
  className,
  children,
  ...props
}: CardGridProps) {
  const colClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div
      className={cn('grid gap-4', colClasses[cols], className)}
      {...props}
    >
      {children}
    </div>
  );
}
