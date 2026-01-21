'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useAuthStore, clearTokens, getRefreshToken } from '@/lib/auth'
import { authApi, dealsApi, Deal, AgentType } from '@/lib/api'
import { DealCard } from '@/components/deals'
import { DashboardLayout } from '@/components/layout'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { AgentSummaryCard } from '@/components/dashboard/AgentSummaryCard'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { UploadedFile } from '@/components/files/FileUploader'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading: authLoading, setUser, logout } = useAuthStore()
  const [deals, setDeals] = useState<Deal[]>([])
  const [isLoadingDeals, setIsLoadingDeals] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [activeDeals, setActiveDeals] = useState(0)

  const canCreateDeal = user?.role === 'admin' || user?.role === 'partner'

  const loadDeals = useCallback(async () => {
    setIsLoadingDeals(true)
    setError(null)
    try {
      // Load first page of deals sorted by last activity (backend default)
      const response = await dealsApi.list(1, 12)
      setDeals(response.deals)
      setTotal(response.total)
      // Count active deals
      const active = response.deals.filter(d => d.status === 'active').length
      setActiveDeals(active)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to load deals')
    } finally {
      setIsLoadingDeals(false)
    }
  }, [])

  useEffect(() => {
    // Load user data if not already loaded
    const loadUser = async () => {
      try {
        const userData = await authApi.getMe()
        setUser(userData)
      } catch {
        // If unauthorized, redirect to login
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
      loadDeals()
    }
  }, [user, loadDeals])

  const handleLogout = async () => {
    try {
      const refreshToken = getRefreshToken()
      await authApi.logout(refreshToken || undefined)
    } catch {
      // Continue with logout even if API call fails
    }
    clearTokens()
    logout()
    router.push('/login')
  }

  const handleDealCreated = (deal: Deal) => {
    // Add the new deal to the beginning of the list
    setDeals((prev) => [deal, ...prev.slice(0, 11)])
    setTotal((prev) => prev + 1)
    if (deal.status === 'active') {
      setActiveDeals((prev) => prev + 1)
    }
  }

  const handleFileUploaded = (file: UploadedFile, dealId: string) => {
    console.log('File uploaded:', file.name, 'to deal:', dealId)
    // Could trigger a refresh of the activity feed here
  }

  const handleRunAgent = (agentType: AgentType, dealId: string) => {
    console.log('Run agent:', agentType, 'on deal:', dealId)
    // Implement agent run logic
  }

  const handleSearch = (query: string) => {
    if (query.trim()) {
      router.push(`/deals?search=${encodeURIComponent(query)}`)
    }
  }

  if (authLoading || !user) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <DashboardLayout
      user={user}
      stats={{
        totalDeals: total,
        activeDeals: activeDeals,
      }}
      onLogout={handleLogout}
      onSearch={handleSearch}
    >
      <div className="space-y-6">
        {/* Page Header with Quick Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back, {user.email.split('@')[0]}
            </p>
          </div>
          <QuickActions
            userRole={user.role as 'admin' | 'partner' | 'viewer'}
            onDealCreated={handleDealCreated}
            onFileUploaded={handleFileUploaded}
            onRunAgent={handleRunAgent}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column - Deal Cards (takes 2 cols on xl) */}
          <div className="xl:col-span-2 space-y-6">
            {/* Deal Cards Section */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Recent Deals</h2>
                <Button variant="link" className="text-sm" onClick={() => router.push('/deals')}>
                  View All ({total}) →
                </Button>
              </div>

              {/* Error message */}
              {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-lg mb-4">
                  {error}
                </div>
              )}

              {/* Deal cards grid */}
              {isLoadingDeals ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-36 bg-muted rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : deals.length === 0 ? (
                <Card className="p-8 text-center">
                  <div className="text-4xl mb-4">📁</div>
                  <p className="text-muted-foreground mb-2">No deals found</p>
                  {canCreateDeal && (
                    <p className="text-sm text-muted-foreground">
                      Create your first deal to get started
                    </p>
                  )}
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {deals.slice(0, 6).map((deal) => (
                    <DealCard key={deal.id} deal={deal} />
                  ))}
                </div>
              )}
            </div>

            {/* Agent Summaries - below deals on larger screens */}
            <div className="hidden lg:block">
              <AgentSummaryCard
                limit={3}
                autoRefresh
                refreshInterval={60000}
                onRerun={(runId, agentType, dealId) => {
                  console.log('Re-run agent:', runId, agentType, dealId)
                }}
              />
            </div>
          </div>

          {/* Right Column - Activity Feed */}
          <div className="space-y-6">
            {/* Activity Feed */}
            <ActivityFeed
              pageSize={10}
              autoRefresh
              refreshInterval={30000}
            />

            {/* Agent Summaries - shown on mobile/tablet, hidden on lg+ */}
            <div className="lg:hidden">
              <AgentSummaryCard
                limit={3}
                autoRefresh
                refreshInterval={60000}
                onRerun={(runId, agentType, dealId) => {
                  console.log('Re-run agent:', runId, agentType, dealId)
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
