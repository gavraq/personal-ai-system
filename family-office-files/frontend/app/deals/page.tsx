'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DealCard, CreateDealModal } from '@/components/deals'
import { dealsApi, Deal, DealStatus } from '@/lib/api'
import { useAuthStore } from '@/lib/auth'
import { authApi } from '@/lib/api'

export default function DealsPage() {
  const router = useRouter()
  const { user, isLoading: authLoading, setUser, logout } = useAuthStore()
  const [deals, setDeals] = useState<Deal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<DealStatus | 'all'>('all')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 12

  const canCreateDeal = user?.role === 'admin' || user?.role === 'partner'

  const loadDeals = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await dealsApi.list(
        page,
        pageSize,
        statusFilter === 'all' ? undefined : statusFilter
      )
      setDeals(response.deals)
      setTotal(response.total)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to load deals')
    } finally {
      setIsLoading(false)
    }
  }, [page, statusFilter])

  // Load user data if not already loaded
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

  // Load deals when user is available
  useEffect(() => {
    if (user) {
      loadDeals()
    }
  }, [user, loadDeals])

  const handleDealCreated = (deal: Deal) => {
    // Add the new deal to the list and refresh
    setDeals((prev) => [deal, ...prev])
    setTotal((prev) => prev + 1)
  }

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value as DealStatus | 'all')
    setPage(1)
  }

  const totalPages = Math.ceil(total / pageSize)

  if (authLoading || !user) {
    return (
      <main className="min-h-screen p-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Deals</h1>
            <p className="text-muted-foreground">
              Manage your deals and transactions
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => router.push('/dashboard')}>
              Back to Dashboard
            </Button>
            {canCreateDeal && (
              <CreateDealModal onDealCreated={handleDealCreated} />
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Status:</span>
            <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <span className="text-sm text-muted-foreground">
            {total} deal{total !== 1 ? 's' : ''} found
          </span>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
            {error}
          </div>
        )}

        {/* Deals grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No deals found</p>
            {canCreateDeal && (
              <p className="text-sm text-muted-foreground mt-2">
                Create your first deal to get started
              </p>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deals.map((deal) => (
              <DealCard key={deal.id} deal={deal} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
