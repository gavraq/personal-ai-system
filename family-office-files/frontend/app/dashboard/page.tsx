'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore, clearTokens, getRefreshToken } from '@/lib/auth'
import { authApi } from '@/lib/api'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading, setUser, logout } = useAuthStore()

  useEffect(() => {
    // Load user data if not already loaded
    const loadUser = async () => {
      try {
        const userData = await authApi.getMe()
        setUser(userData)
      } catch (error) {
        // If unauthorized, redirect to login
        logout()
        router.push('/login')
      }
    }

    if (!user && !isLoading) {
      loadUser()
    }
  }, [user, isLoading, setUser, logout, router])

  const handleLogout = async () => {
    try {
      const refreshToken = getRefreshToken()
      await authApi.logout(refreshToken || undefined)
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API error:', error)
    }
    clearTokens()
    logout()
    router.push('/login')
  }

  if (isLoading || !user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
        <div className="text-gray-600">Loading...</div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Dashboard</CardTitle>
          <CardDescription>Welcome to Family Office Files</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-gray-100 rounded-lg">
            <p className="text-sm text-gray-600">Email</p>
            <p className="font-medium">{user.email}</p>
          </div>
          <div className="p-4 bg-gray-100 rounded-lg">
            <p className="text-sm text-gray-600">Role</p>
            <p className="font-medium capitalize">{user.role}</p>
          </div>
          <Button onClick={() => router.push('/deals')} className="w-full">
            View Deals
          </Button>
          <Button onClick={handleLogout} variant="outline" className="w-full">
            Sign Out
          </Button>
        </CardContent>
      </Card>
    </main>
  )
}
