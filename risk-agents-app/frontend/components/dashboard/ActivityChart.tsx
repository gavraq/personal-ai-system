/**
 * ActivityChart Component
 * Displays activity visualization with simple bar chart
 */

'use client';

import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

export interface ActivityData {
  label: string;
  value: number;
  color?: 'blue' | 'green' | 'purple' | 'yellow';
}

export interface ActivityChartProps {
  data: ActivityData[];
  title?: string;
  description?: string;
  className?: string;
}

/**
 * Gets color classes for bars
 */
function getBarColor(color?: string): string {
  switch (color) {
    case 'blue':
      return 'bg-gradient-to-t from-blue-500 to-blue-400';
    case 'green':
      return 'bg-gradient-to-t from-green-500 to-green-400';
    case 'purple':
      return 'bg-gradient-to-t from-purple-500 to-purple-400';
    case 'yellow':
      return 'bg-gradient-to-t from-yellow-500 to-yellow-400';
    default:
      return 'bg-gradient-to-t from-slate-500 to-slate-400';
  }
}

/**
 * ActivityChart Component
 *
 * Simple bar chart visualization for activity data:
 * - Responsive bar heights
 * - Color-coded bars
 * - Labels and values
 * - Hover effects
 *
 * @example
 * ```tsx
 * <ActivityChart
 *   data={[
 *     { label: 'Mon', value: 12, color: 'blue' },
 *     { label: 'Tue', value: 19, color: 'blue' },
 *     { label: 'Wed', value: 15, color: 'blue' }
 *   ]}
 *   title="Weekly Activity"
 *   description="Queries per day"
 * />
 * ```
 */
export function ActivityChart({
  data,
  title = 'Activity',
  description,
  className
}: ActivityChartProps) {
  // Find max value for scaling
  const maxValue = Math.max(...data.map(d => d.value), 1);

  return (
    <Card variant="glass" className={className}>
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-heading font-semibold text-slate-200">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-slate-400 mt-1">{description}</p>
        )}
      </div>

      {/* Chart */}
      <div className="space-y-4">
        {data.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400">No activity data available</p>
          </div>
        ) : (
          <div className="flex items-end justify-between gap-2 h-48">
            {data.map((item, index) => {
              const heightPercent = (item.value / maxValue) * 100;

              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2">
                  {/* Value label (on hover) */}
                  <div className="h-6 flex items-center">
                    <span className="text-xs font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                      {item.value}
                    </span>
                  </div>

                  {/* Bar */}
                  <div className="w-full flex-1 flex items-end group">
                    <div
                      className={cn(
                        'w-full rounded-t-lg transition-all duration-300',
                        'hover:opacity-80 cursor-pointer relative',
                        getBarColor(item.color)
                      )}
                      style={{ height: `${heightPercent}%` }}
                      title={`${item.label}: ${item.value}`}
                    >
                      {/* Glow effect on hover */}
                      <div
                        className={cn(
                          'absolute inset-0 rounded-t-lg opacity-0 group-hover:opacity-50',
                          'transition-opacity duration-300 blur-sm',
                          getBarColor(item.color)
                        )}
                      />

                      {/* Value display on hover */}
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="px-2 py-1 bg-slate-800 rounded text-xs font-semibold text-slate-200 whitespace-nowrap shadow-lg">
                          {item.value}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Label */}
                  <div className="text-xs text-slate-500 font-medium mt-2">
                    {item.label}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Legend/Summary */}
      {data.length > 0 && (
        <div className="mt-6 pt-4 border-t border-slate-700/50 flex items-center justify-between text-xs">
          <div className="text-slate-500">
            Total: <span className="text-slate-300 font-semibold">
              {data.reduce((sum, item) => sum + item.value, 0)}
            </span>
          </div>
          <div className="text-slate-500">
            Average: <span className="text-slate-300 font-semibold">
              {(data.reduce((sum, item) => sum + item.value, 0) / data.length).toFixed(1)}
            </span>
          </div>
        </div>
      )}
    </Card>
  );
}

/**
 * DomainActivity Component
 * Shows activity breakdown by domain
 */
export interface DomainActivityProps {
  domains: {
    name: string;
    count: number;
    percentage: number;
    color?: 'blue' | 'green' | 'purple' | 'yellow';
  }[];
  className?: string;
}

export function DomainActivity({ domains, className }: DomainActivityProps) {
  const total = domains.reduce((sum, d) => sum + d.count, 0);

  return (
    <Card variant="glass" className={className}>
      <div className="mb-6">
        <h3 className="text-lg font-heading font-semibold text-slate-200">
          Domain Activity
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Skill usage by domain
        </p>
      </div>

      {domains.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-slate-400">No domain activity yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {domains.map((domain, index) => {
            const barColor = getBarColor(domain.color);

            return (
              <div key={index}>
                {/* Domain name and count */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-300 font-medium">
                    {domain.name}
                  </span>
                  <span className="text-sm text-slate-400">
                    {domain.count} ({domain.percentage.toFixed(0)}%)
                  </span>
                </div>

                {/* Progress bar */}
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={cn('h-full transition-all duration-500', barColor)}
                    style={{ width: `${domain.percentage}%` }}
                  />
                </div>
              </div>
            );
          })}

          {/* Total */}
          <div className="pt-4 border-t border-slate-700/50">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Total Skills Used</span>
              <span className="text-slate-200 font-semibold">{total}</span>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
