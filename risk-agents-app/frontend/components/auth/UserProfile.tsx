'use client'

/**
 * User Profile Component
 * Displays current user information and logout button
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { sessionStorage } from '@/lib/auth/session'
import { User } from '@/lib/auth/types'

export default function UserProfile() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load user from session storage
    const storedUser = sessionStorage.getUser()
    setUser(storedUser)
    setLoading(false)

    // Redirect to login if not authenticated
    if (!storedUser) {
      router.push('/login')
    }
  }, [router])

  const handleLogout = () => {
    // Clear session storage
    sessionStorage.clear()

    // Redirect to login
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="animate-pulse bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-slate-700 rounded w-1/2"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-elegant border border-slate-700 p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-card text-white">Profile</h2>
          <p className="text-slate-300 mt-1">Your account information</p>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all"
        >
          Logout
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">User ID</label>
          <p className="text-white font-mono text-sm bg-slate-900/50 px-3 py-2 rounded border border-slate-600">
            {user.user_id}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
          <p className="text-white">{user.email}</p>
        </div>

        {user.full_name && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
            <p className="text-white">{user.full_name}</p>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Account Status</label>
          <div className="flex items-center gap-2">
            <span className={`led-indicator ${user.disabled ? 'led-off' : 'led-on'}`}></span>
            <span className={`text-sm font-semibold ${user.disabled ? 'text-red-400' : 'text-green-400'}`}>
              {user.disabled ? 'Disabled' : 'Active'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
