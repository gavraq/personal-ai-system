/**
 * RecentQueries Component
 * Displays a list of recent queries with status and timestamps
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export interface QueryHistoryItem {
  id: string;
  query: string;
  status: 'success' | 'error' | 'pending';
  timestamp: Date;
  responseTime?: number; // in milliseconds
  skillsUsed?: string[];
}

export interface RecentQueriesProps {
  queries: QueryHistoryItem[];
  maxItems?: number;
  className?: string;
  onQueryClick?: (query: QueryHistoryItem) => void;
}

/**
 * Formats a timestamp to a relative time string
 */
function formatTimestamp(date: Date): string {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMins = Math.floor(diffInMs / 60000);
  const diffInHours = Math.floor(diffInMs / 3600000);
  const diffInDays = Math.floor(diffInMs / 86400000);

  if (diffInMins < 1) return 'Just now';
  if (diffInMins < 60) return `${diffInMins}m ago`;
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays}d ago`;
  return date.toLocaleDateString();
}

/**
 * Gets status icon and color
 */
function getStatusDisplay(status: string): { icon: React.ReactNode; color: string } {
  switch (status) {
    case 'success':
      return {
        icon: <CheckCircleIcon className="w-5 h-5" />,
        color: 'text-green-400'
      };
    case 'error':
      return {
        icon: <XCircleIcon className="w-5 h-5" />,
        color: 'text-red-400'
      };
    case 'pending':
    default:
      return {
        icon: <ClockIcon className="w-5 h-5" />,
        color: 'text-yellow-400'
      };
  }
}

/**
 * Truncates query text to a specified length
 */
function truncateQuery(query: string, maxLength: number = 60): string {
  if (query.length <= maxLength) return query;
  return query.substring(0, maxLength) + '...';
}

/**
 * RecentQueries Component
 *
 * Displays a list of recent query executions with:
 * - Query text (truncated)
 * - Status indicator (success/error/pending)
 * - Timestamp (relative)
 * - Response time
 * - Click to view details
 *
 * @example
 * ```tsx
 * <RecentQueries
 *   queries={queryHistory}
 *   maxItems={10}
 *   onQueryClick={(query) => console.log(query)}
 * />
 * ```
 */
export function RecentQueries({
  queries,
  maxItems = 10,
  className,
  onQueryClick
}: RecentQueriesProps) {
  const displayQueries = queries.slice(0, maxItems);

  return (
    <Card variant="glass" className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-heading font-semibold text-slate-200">
            Recent Queries
          </h3>
          <p className="text-sm text-slate-400 mt-1">
            Your latest interactions with Risk Agent
          </p>
        </div>
        <Link href="/chat">
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </Link>
      </div>

      {/* Queries list */}
      {displayQueries.length === 0 ? (
        <div className="text-center py-12">
          <ClockIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No queries yet</p>
          <p className="text-sm text-slate-500 mt-2">
            Start a conversation in the chat to see your query history
          </p>
          <Link href="/chat" className="mt-4 inline-block">
            <Button variant="gradient" size="sm">
              Start Chatting
            </Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {displayQueries.map((query) => {
            const statusDisplay = getStatusDisplay(query.status);

            return (
              <div
                key={query.id}
                onClick={() => onQueryClick?.(query)}
                className={cn(
                  'p-4 rounded-lg border border-slate-700/50 bg-slate-800/30',
                  'hover:bg-slate-800/50 hover:border-slate-600/50',
                  'transition-all duration-200 cursor-pointer group'
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  {/* Query text and metadata */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-200 mb-2 line-clamp-2 group-hover:text-slate-100">
                      {truncateQuery(query.query, 80)}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <ClockIcon className="w-3 h-3" />
                        {formatTimestamp(query.timestamp)}
                      </span>
                      {query.responseTime && (
                        <span>
                          {query.responseTime < 1000
                            ? `${query.responseTime}ms`
                            : `${(query.responseTime / 1000).toFixed(1)}s`}
                        </span>
                      )}
                      {query.skillsUsed && query.skillsUsed.length > 0 && (
                        <span className="text-purple-400">
                          {query.skillsUsed.length} skill{query.skillsUsed.length > 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Status indicator */}
                  <div className={cn('flex-shrink-0', statusDisplay.color)}>
                    {statusDisplay.icon}
                  </div>
                </div>

                {/* Skills used (if any) */}
                {query.skillsUsed && query.skillsUsed.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {query.skillsUsed.slice(0, 3).map((skill, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 text-xs rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20"
                      >
                        {skill}
                      </span>
                    ))}
                    {query.skillsUsed.length > 3 && (
                      <span className="px-2 py-1 text-xs rounded-md bg-slate-700/50 text-slate-400">
                        +{query.skillsUsed.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
