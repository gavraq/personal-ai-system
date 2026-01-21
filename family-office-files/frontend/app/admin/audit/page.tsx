'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAuthStore } from '@/lib/auth'
import { authApi, auditApi, AuditLogEntry, AuditLogFilters } from '@/lib/api'
import { DashboardLayout } from '@/components/layout'
import { formatDistanceToNow } from 'date-fns'
import { ArrowLeft, ChevronLeft, ChevronRight, Shield, User, FileText, Users, FolderOpen } from 'lucide-react'

const ACTION_LABELS: Record<string, string> = {
  role_change: 'Role Change',
  user_create: 'User Created',
  deal_create: 'Deal Created',
  deal_update: 'Deal Updated',
  deal_delete: 'Deal Deleted',
  member_add: 'Member Added',
  member_remove: 'Member Removed',
  member_role_override: 'Role Override',
  file_upload: 'File Uploaded',
  file_delete: 'File Deleted',
  file_share: 'File Shared',
  file_unshare: 'File Unshared',
  permission_change: 'Permission Change',
}

const ENTITY_ICONS: Record<string, typeof Shield> = {
  user: User,
  deal: FolderOpen,
  deal_member: Users,
  file: FileText,
  file_share: Shield,
}

function getActionBadgeColor(action: string): string {
  if (action.includes('delete') || action.includes('remove') || action.includes('unshare')) {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  if (action.includes('create') || action.includes('add') || action.includes('share')) {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  }
  if (action.includes('change') || action.includes('update') || action.includes('override')) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  }
  return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

function formatValue(value: Record<string, unknown> | null): string {
  if (!value) return '-'
  return Object.entries(value)
    .map(([key, val]) => `${key}: ${val}`)
    .join(', ')
}

export default function AuditLogPage() {
  const router = useRouter()
  const { user, isLoading: authLoading, setUser, logout } = useAuthStore()
  const [entries, setEntries] = useState<AuditLogEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [filters, setFilters] = useState<AuditLogFilters>({})

  const loadAuditEntries = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await auditApi.list(page, pageSize, filters)
      setEntries(response.entries)
      setTotal(response.total)
    } catch (err: unknown) {
      const error = err as { response?: { status?: number; data?: { detail?: string } } }
      if (error.response?.status === 403) {
        setError('Access denied. Admin role required.')
      } else {
        setError(error.response?.data?.detail || 'Failed to load audit log')
      }
    } finally {
      setIsLoading(false)
    }
  }, [page, pageSize, filters])

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await authApi.getMe()
        setUser(userData)
      } catch {
        logout()
        router.push('/login')
      }
    }

    if (!user && !authLoading) {
      loadUser()
    }
  }, [user, authLoading, setUser, logout, router])

  useEffect(() => {
    if (user) {
      if (user.role !== 'admin') {
        router.push('/dashboard')
        return
      }
      loadAuditEntries()
    }
  }, [user, loadAuditEntries, router])

  const totalPages = Math.ceil(total / pageSize)

  const handleFilterChange = (key: keyof AuditLogFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === 'all' ? undefined : value,
    }))
    setPage(1)
  }

  const clearFilters = () => {
    setFilters({})
    setPage(1)
  }

  if (authLoading || !user) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/dashboard')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-semibold">Audit Log</h1>
              <p className="text-muted-foreground">
                View permission changes and security events
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Admin Only</span>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <div className="w-48">
                <label className="text-sm font-medium mb-1 block">Action Type</label>
                <Select
                  value={filters.action || 'all'}
                  onValueChange={(value) => handleFilterChange('action', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All actions" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All actions</SelectItem>
                    {Object.entries(ACTION_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <label className="text-sm font-medium mb-1 block">Entity Type</label>
                <Select
                  value={filters.entity_type || 'all'}
                  onValueChange={(value) => handleFilterChange('entity_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All entities" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All entities</SelectItem>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="deal">Deal</SelectItem>
                    <SelectItem value="deal_member">Deal Member</SelectItem>
                    <SelectItem value="file">File</SelectItem>
                    <SelectItem value="file_share">File Share</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <label className="text-sm font-medium mb-1 block">From Date</label>
                <Input
                  type="date"
                  value={filters.from_date?.split('T')[0] || ''}
                  onChange={(e) => handleFilterChange('from_date', e.target.value ? `${e.target.value}T00:00:00` : '')}
                />
              </div>

              <div className="w-48">
                <label className="text-sm font-medium mb-1 block">To Date</label>
                <Input
                  type="date"
                  value={filters.to_date?.split('T')[0] || ''}
                  onChange={(e) => handleFilterChange('to_date', e.target.value ? `${e.target.value}T23:59:59` : '')}
                />
              </div>

              <div className="flex items-end">
                <Button variant="outline" onClick={clearFilters}>
                  Clear Filters
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error state */}
        {error && (
          <Card className="border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800">
            <CardContent className="p-4">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Audit entries */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-muted-foreground">Loading audit entries...</p>
              </div>
            ) : entries.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-muted-foreground">No audit entries found</p>
              </div>
            ) : (
              <div className="divide-y">
                {entries.map((entry) => {
                  const EntityIcon = ENTITY_ICONS[entry.entity_type] || Shield
                  return (
                    <div
                      key={entry.id}
                      className="p-4 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3">
                          <div className="mt-1 p-2 bg-muted rounded-lg">
                            <EntityIcon className="h-4 w-4 text-muted-foreground" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionBadgeColor(entry.action)}`}>
                                {ACTION_LABELS[entry.action] || entry.action}
                              </span>
                              <span className="text-sm text-muted-foreground">
                                on {entry.entity_type}
                              </span>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              by {entry.actor_email || 'Unknown'}
                            </p>
                            {(entry.old_value || entry.new_value) && (
                              <div className="mt-2 text-sm">
                                {entry.old_value && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Old:</span> {formatValue(entry.old_value)}
                                  </p>
                                )}
                                {entry.new_value && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">New:</span> {formatValue(entry.new_value)}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground whitespace-nowrap">
                          {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} entries
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
