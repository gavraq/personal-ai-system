/**
 * MetricsWidget Component
 * Displays a single metric with value, trend, and icon
 */

'use client';

import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

export interface MetricData {
  label: string;
  value: string | number;
  change?: number; // Percentage change
  changeLabel?: string; // e.g., "vs last week"
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'purple' | 'yellow' | 'red';
  format?: 'number' | 'percentage' | 'duration' | 'currency';
}

export interface MetricsWidgetProps {
  metric: MetricData;
  className?: string;
}

/**
 * Formats the metric value based on the format type
 */
function formatValue(value: string | number, format?: string): string {
  if (typeof value === 'string') return value;

  switch (format) {
    case 'percentage':
      return `${value}%`;
    case 'duration':
      return `${value}ms`;
    case 'currency':
      return `$${value.toLocaleString()}`;
    case 'number':
    default:
      return value.toLocaleString();
  }
}

/**
 * Gets the color classes for the metric
 */
function getColorClasses(color?: string): { gradient: string; icon: string; border: string } {
  switch (color) {
    case 'blue':
      return {
        gradient: 'from-blue-500 to-blue-600',
        icon: 'text-blue-400',
        border: 'border-blue-500/20'
      };
    case 'green':
      return {
        gradient: 'from-green-500 to-green-600',
        icon: 'text-green-400',
        border: 'border-green-500/20'
      };
    case 'purple':
      return {
        gradient: 'from-purple-500 to-purple-600',
        icon: 'text-purple-400',
        border: 'border-purple-500/20'
      };
    case 'yellow':
      return {
        gradient: 'from-yellow-500 to-yellow-600',
        icon: 'text-yellow-400',
        border: 'border-yellow-500/20'
      };
    case 'red':
      return {
        gradient: 'from-red-500 to-red-600',
        icon: 'text-red-400',
        border: 'border-red-500/20'
      };
    default:
      return {
        gradient: 'from-slate-500 to-slate-600',
        icon: 'text-slate-400',
        border: 'border-slate-500/20'
      };
  }
}

/**
 * MetricsWidget Component
 *
 * Displays a single metric card with:
 * - Icon and label
 * - Large value display
 * - Optional trend indicator (up/down arrow)
 * - Optional change percentage
 *
 * @example
 * ```tsx
 * <MetricsWidget
 *   metric={{
 *     label: "Total Queries",
 *     value: 1234,
 *     change: 12.5,
 *     changeLabel: "vs last week",
 *     icon: <ChartBarIcon className="w-6 h-6" />,
 *     color: "blue",
 *     format: "number"
 *   }}
 * />
 * ```
 */
export function MetricsWidget({ metric, className }: MetricsWidgetProps) {
  const { label, value, change, changeLabel, icon, color, format } = metric;
  const colors = getColorClasses(color);
  const formattedValue = formatValue(value, format);
  const isPositive = change !== undefined && change >= 0;

  return (
    <Card
      variant="glass"
      className={cn(
        'relative overflow-hidden transition-all duration-300 hover:scale-105',
        colors.border,
        className
      )}
    >
      {/* Gradient overlay */}
      <div
        className={cn(
          'absolute top-0 right-0 w-32 h-32 opacity-10 blur-2xl',
          `bg-gradient-to-br ${colors.gradient}`
        )}
      />

      <div className="relative">
        {/* Icon and label */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">
              {label}
            </p>
          </div>
          {icon && (
            <div className={cn('p-2 rounded-lg bg-slate-800/50', colors.icon)}>
              {icon}
            </div>
          )}
        </div>

        {/* Value */}
        <div className="mb-3">
          <p className="text-4xl font-heading font-bold text-slate-100">
            {formattedValue}
          </p>
        </div>

        {/* Trend indicator */}
        {change !== undefined && (
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded-md text-xs font-semibold',
                isPositive
                  ? 'bg-green-500/10 text-green-400'
                  : 'bg-red-500/10 text-red-400'
              )}
            >
              {isPositive ? (
                <ArrowUpIcon className="w-3 h-3" />
              ) : (
                <ArrowDownIcon className="w-3 h-3" />
              )}
              <span>{Math.abs(change)}%</span>
            </div>
            {changeLabel && (
              <span className="text-xs text-slate-500">{changeLabel}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

/**
 * MetricsGrid Component
 * Grid layout for multiple metrics widgets
 */
export interface MetricsGridProps {
  metrics: MetricData[];
  className?: string;
}

export function MetricsGrid({ metrics, className }: MetricsGridProps) {
  return (
    <div
      className={cn(
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4',
        className
      )}
    >
      {metrics.map((metric, index) => (
        <MetricsWidget key={index} metric={metric} />
      ))}
    </div>
  );
}
