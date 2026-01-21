'use client'

import { useEffect, useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { activityApi, Activity, ActivityType } from '@/lib/api'

interface ActivityFeedProps {
  dealId?: string
  pageSize?: number
  autoRefresh?: boolean
  refreshInterval?: number
}

function formatRelativeTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffSeconds < 60) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
  })
}

function getActivityIcon(action: ActivityType): string {
  switch (action) {
    case 'file_upload':
      return '📤'
    case 'file_link':
      return '🔗'
    case 'file_delete':
      return '🗑️'
    case 'deal_create':
      return '✨'
    case 'deal_update':
      return '✏️'
    case 'deal_delete':
      return '❌'
    case 'member_add':
      return '👤'
    case 'member_remove':
      return '👋'
    case 'agent_run':
      return '🤖'
    default:
      return '📋'
  }
}

function getActivityDescription(activity: Activity): string {
  const actor = activity.actor_email || 'Someone'
  const details = activity.details || {}

  switch (activity.action) {
    case 'file_upload':
      return `${actor} uploaded "${details.file_name || 'a file'}"`
    case 'file_link':
      return `${actor} linked "${details.file_name || 'a file'}"`
    case 'file_delete':
      return `${actor} deleted "${details.file_name || 'a file'}"`
    case 'deal_create':
      return `${actor} created this deal`
    case 'deal_update':
      const changes = details.changes as Record<string, { old: string; new: string }> | undefined
      if (changes?.status) {
        return `${actor} changed status to ${changes.status.new}`
      }
      if (changes?.title) {
        return `${actor} renamed the deal`
      }
      return `${actor} updated the deal`
    case 'deal_delete':
      return `${actor} deleted the deal`
    case 'member_add':
      return `${actor} added ${details.user_email || 'a member'}`
    case 'member_remove':
      return `${actor} removed ${details.user_email || 'a member'}`
    case 'agent_run':
      return `${actor} ran an agent`
    default:
      return `${actor} performed an action`
  }
}

function ActivityAvatar({ email }: { email: string | null }) {
  const initial = email ? email[0].toUpperCase() : '?'
  const bgColors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-teal-500',
  ]
  const colorIndex = email ? email.charCodeAt(0) % bgColors.length : 0
  const bgColor = bgColors[colorIndex]

  return (
    <div
      className={`w-8 h-8 rounded-full ${bgColor} flex items-center justify-center text-white text-sm font-medium`}
      title={email || 'Unknown user'}
    >
      {initial}
    </div>
  )
}

export function ActivityFeed({
  dealId,
  pageSize = 10,
  autoRefresh = true,
  refreshInterval = 30000,
}: ActivityFeedProps) {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchActivities = useCallback(async () => {
    try {
      const response = dealId
        ? await activityApi.listForDeal(dealId, 1, pageSize)
        : await activityApi.list({ page: 1, pageSize })
      setActivities(response.activities)
      setError(null)
    } catch (err) {
      setError('Failed to load activities')
      console.error('Error fetching activities:', err)
    } finally {
      setLoading(false)
    }
  }, [dealId, pageSize])

  useEffect(() => {
    fetchActivities()

    // Auto-refresh
    if (autoRefresh) {
      const interval = setInterval(fetchActivities, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchActivities, autoRefresh, refreshInterval])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-3 animate-pulse">
                <div className="w-8 h-8 rounded-full bg-gray-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 rounded w-1/4" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No activity yet</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3">
              <ActivityAvatar email={activity.actor_email} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{getActivityIcon(activity.action)}</span>
                  <p className="text-sm truncate">
                    {getActivityDescription(activity)}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatRelativeTime(activity.created_at)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
