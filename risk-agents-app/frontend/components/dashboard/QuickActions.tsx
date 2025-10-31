/**
 * QuickActions Component
 * Displays quick action buttons for common tasks
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import {
  ChatBubbleLeftRightIcon,
  RectangleStackIcon,
  BookOpenIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  color?: 'blue' | 'green' | 'purple' | 'yellow';
  external?: boolean;
}

export interface QuickActionsProps {
  actions?: QuickAction[];
  className?: string;
}

/**
 * Default quick actions
 */
const DEFAULT_ACTIONS: QuickAction[] = [
  {
    id: 'new-chat',
    label: 'New Chat',
    description: 'Start a conversation with Risk Agent',
    href: '/chat',
    icon: <ChatBubbleLeftRightIcon className="w-6 h-6" />,
    color: 'blue'
  },
  {
    id: 'browse-skills',
    label: 'Browse Skills',
    description: 'Explore available agent skills',
    href: '/skills',
    icon: <RectangleStackIcon className="w-6 h-6" />,
    color: 'purple'
  },
  {
    id: 'knowledge-base',
    label: 'Knowledge Base',
    description: 'Access project documentation',
    href: '/knowledge',
    icon: <BookOpenIcon className="w-6 h-6" />,
    color: 'green'
  },
  {
    id: 'api-test',
    label: 'API Test',
    description: 'Test WebSocket connection',
    href: '/websocket-test',
    icon: <ArrowPathIcon className="w-6 h-6" />,
    color: 'yellow'
  }
];

/**
 * Gets color classes for an action button
 */
function getActionColors(color?: string): {
  gradient: string;
  icon: string;
  hover: string;
} {
  switch (color) {
    case 'blue':
      return {
        gradient: 'from-blue-500 to-blue-600',
        icon: 'text-blue-400',
        hover: 'hover:border-blue-500/50'
      };
    case 'green':
      return {
        gradient: 'from-green-500 to-green-600',
        icon: 'text-green-400',
        hover: 'hover:border-green-500/50'
      };
    case 'purple':
      return {
        gradient: 'from-purple-500 to-purple-600',
        icon: 'text-purple-400',
        hover: 'hover:border-purple-500/50'
      };
    case 'yellow':
      return {
        gradient: 'from-yellow-500 to-yellow-600',
        icon: 'text-yellow-400',
        hover: 'hover:border-yellow-500/50'
      };
    default:
      return {
        gradient: 'from-slate-500 to-slate-600',
        icon: 'text-slate-400',
        hover: 'hover:border-slate-500/50'
      };
  }
}

/**
 * QuickActions Component
 *
 * Displays a grid of quick action buttons for common tasks:
 * - New Chat
 * - Browse Skills
 * - Knowledge Base
 * - API Test
 *
 * Each action button includes:
 * - Icon with color
 * - Label and description
 * - Hover effects
 * - Navigation link
 *
 * @example
 * ```tsx
 * <QuickActions />
 * ```
 */
export function QuickActions({ actions = DEFAULT_ACTIONS, className }: QuickActionsProps) {
  return (
    <Card variant="glass" className={className}>
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-heading font-semibold text-slate-200">
          Quick Actions
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Common tasks and shortcuts
        </p>
      </div>

      {/* Actions grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {actions.map((action) => {
          const colors = getActionColors(action.color);

          const content = (
            <div
              className={cn(
                'relative p-4 rounded-lg border border-slate-700/50 bg-slate-800/30',
                'transition-all duration-200 group cursor-pointer',
                'hover:bg-slate-800/50',
                colors.hover
              )}
            >
              {/* Gradient overlay */}
              <div
                className={cn(
                  'absolute top-0 right-0 w-24 h-24 opacity-0 group-hover:opacity-10',
                  'transition-opacity duration-300 blur-2xl',
                  `bg-gradient-to-br ${colors.gradient}`
                )}
              />

              <div className="relative flex items-start gap-3">
                {/* Icon */}
                <div
                  className={cn(
                    'p-2 rounded-lg bg-slate-800/50 group-hover:scale-110',
                    'transition-transform duration-200',
                    colors.icon
                  )}
                >
                  {action.icon}
                </div>

                {/* Text */}
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-slate-200 group-hover:text-slate-100">
                    {action.label}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1">
                    {action.description}
                  </p>
                </div>
              </div>
            </div>
          );

          // Wrap in Link if internal, otherwise use <a>
          if (action.external) {
            return (
              <a
                key={action.id}
                href={action.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                {content}
              </a>
            );
          }

          return (
            <Link key={action.id} href={action.href}>
              {content}
            </Link>
          );
        })}
      </div>
    </Card>
  );
}

/**
 * SystemStatus Component
 * Displays system health status indicators
 */
export interface SystemStatusProps {
  backendStatus: 'online' | 'offline' | 'degraded';
  websocketStatus: 'connected' | 'disconnected' | 'reconnecting';
  authStatus: 'authenticated' | 'unauthenticated';
  className?: string;
}

export function SystemStatus({
  backendStatus,
  websocketStatus,
  authStatus,
  className
}: SystemStatusProps) {
  const getStatusColor = (status: string): string => {
    if (status === 'online' || status === 'connected' || status === 'authenticated') {
      return 'bg-green-500';
    }
    if (status === 'degraded' || status === 'reconnecting') {
      return 'bg-yellow-500';
    }
    return 'bg-red-500';
  };

  const getStatusLabel = (status: string): string => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <Card variant="glass" className={className}>
      <h3 className="text-lg font-heading font-semibold text-slate-200 mb-4">
        System Status
      </h3>

      <div className="space-y-3">
        {/* Backend */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">Backend API</span>
          <div className="flex items-center gap-2">
            <div className={cn('w-2 h-2 rounded-full', getStatusColor(backendStatus))} />
            <span className="text-sm text-slate-300">
              {getStatusLabel(backendStatus)}
            </span>
          </div>
        </div>

        {/* WebSocket */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">WebSocket</span>
          <div className="flex items-center gap-2">
            <div className={cn('w-2 h-2 rounded-full', getStatusColor(websocketStatus))} />
            <span className="text-sm text-slate-300">
              {getStatusLabel(websocketStatus)}
            </span>
          </div>
        </div>

        {/* Authentication */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">Authentication</span>
          <div className="flex items-center gap-2">
            <div className={cn('w-2 h-2 rounded-full', getStatusColor(authStatus))} />
            <span className="text-sm text-slate-300">
              {getStatusLabel(authStatus)}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
