'use client'

/**
 * Login Form Component
 * Handles user login with email and password
 */

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { sessionStorage } from '@/lib/auth/session'
import { LoginCredentials } from '@/lib/auth/types'

interface LoginFormProps {
  onSuccess?: () => void
  redirectTo?: string
}

export default function LoginForm({ onSuccess, redirectTo = '/dashboard' }: LoginFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Call login API
      const token = await api.login(formData)

      // Save tokens to localStorage
      sessionStorage.saveTokens(token)

      // Fetch and save user information
      try {
        const user = await api.getCurrentUser(token.access_token)
        sessionStorage.saveUser(user)
      } catch (userError) {
        console.error('Failed to fetch user info:', userError)
        // Continue even if user fetch fails
      }

      // Call success callback
      if (onSuccess) {
        onSuccess()
      }

      // Redirect to dashboard
      router.push(redirectTo)
    } catch (err) {
      console.error('Login error:', err)
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-200 mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          placeholder="you@example.com"
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-1">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          placeholder="••••••••"
          disabled={loading}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full py-3 px-4 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </button>

      <div className="text-sm text-slate-300 text-center">
        <p>
          Test credentials: <code className="bg-slate-800 px-2 py-1 rounded text-blue-400">test@example.com</code> /{' '}
          <code className="bg-slate-800 px-2 py-1 rounded text-blue-400">testpassword</code>
        </p>
      </div>
    </form>
  )
}
