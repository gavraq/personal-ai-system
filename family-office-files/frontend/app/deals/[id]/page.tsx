'use client'

import { useEffect, useState, use } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge, EditDealModal, MemberManager } from '@/components/deals'
import { dealsApi, Deal } from '@/lib/api'
import { useAuthStore } from '@/lib/auth'
import { authApi } from '@/lib/api'

interface DealDetailPageProps {
  params: Promise<{ id: string }>
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function DealDetailPage({ params }: DealDetailPageProps) {
  const { id } = use(params)
  const router = useRouter()
  const { user, isLoading: authLoading, setUser, logout } = useAuthStore()
  const [deal, setDeal] = useState<Deal | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [memberModalOpen, setMemberModalOpen] = useState(false)

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

  // Load deal when user is available
  useEffect(() => {
    const loadDeal = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const dealData = await dealsApi.get(id)
        setDeal(dealData)
      } catch (err: unknown) {
        const error = err as { response?: { status?: number; data?: { detail?: string } } }
        if (error.response?.status === 404) {
          setError('Deal not found')
        } else if (error.response?.status === 403) {
          setError('You do not have access to this deal')
        } else {
          setError(error.response?.data?.detail || 'Failed to load deal')
        }
      } finally {
        setIsLoading(false)
      }
    }

    if (user && id) {
      loadDeal()
    }
  }, [user, id])

  const handleDealUpdated = (updatedDeal: Deal) => {
    setDeal(updatedDeal)
  }

  const handleDelete = async () => {
    if (!deal) return
    if (!confirm('Are you sure you want to delete this deal? This action cannot be undone.')) {
      return
    }

    try {
      await dealsApi.delete(deal.id)
      router.push('/deals')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to delete deal')
    }
  }

  const isAdmin = user?.role === 'admin'
  const canEdit = deal && deal.status !== 'closed'

  if (authLoading || !user) {
    return (
      <main className="min-h-screen p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </main>
    )
  }

  if (isLoading) {
    return (
      <main className="min-h-screen p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="h-48 bg-gray-200 rounded-xl animate-pulse" />
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-4">
          <Button variant="outline" onClick={() => router.push('/deals')}>
            Back to Deals
          </Button>
          <div className="p-6 bg-destructive/10 text-destructive rounded-lg">
            {error}
          </div>
        </div>
      </main>
    )
  }

  if (!deal) {
    return null
  }

  return (
    <main className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Back button */}
        <Button variant="outline" onClick={() => router.push('/deals')}>
          Back to Deals
        </Button>

        {/* Deal header */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-2xl">{deal.title}</CardTitle>
                  <StatusBadge status={deal.status} />
                </div>
                <CardDescription>
                  Created {formatDate(deal.created_at)}
                  {deal.updated_at && deal.updated_at !== deal.created_at && (
                    <> • Updated {formatDate(deal.updated_at)}</>
                  )}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setMemberModalOpen(true)}>
                  Members
                </Button>
                {canEdit && (
                  <Button variant="outline" onClick={() => setEditModalOpen(true)}>
                    Edit
                  </Button>
                )}
                {isAdmin && (
                  <Button variant="destructive" onClick={handleDelete}>
                    Delete
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {deal.description ? (
              <p className="text-muted-foreground whitespace-pre-wrap">{deal.description}</p>
            ) : (
              <p className="text-muted-foreground italic">No description provided</p>
            )}
          </CardContent>
        </Card>

        {/* Deal info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <StatusBadge status={deal.status} className="text-sm" />
              {deal.status === 'closed' && (
                <p className="text-sm text-muted-foreground mt-2">
                  This deal is closed and read-only.
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Files</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                File management coming soon...
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Edit modal */}
        {deal && (
          <EditDealModal
            deal={deal}
            open={editModalOpen}
            onOpenChange={setEditModalOpen}
            onDealUpdated={handleDealUpdated}
          />
        )}

        {/* Member manager modal */}
        {deal && (
          <MemberManager
            deal={deal}
            open={memberModalOpen}
            onOpenChange={setMemberModalOpen}
          />
        )}
      </div>
    </main>
  )
}
