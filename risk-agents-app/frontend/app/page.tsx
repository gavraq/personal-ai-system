'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api, type HealthCheck } from '@/lib/api'
import { useAuth } from '@/lib/auth/middleware'

export default function Home() {
  const [backendHealth, setBackendHealth] = useState<HealthCheck | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { isAuthenticated, user } = useAuth()

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const data = await api.health()
        setBackendHealth(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to backend')
      } finally {
        setLoading(false)
      }
    }

    checkBackend()
  }, [])

  return (
    <main className="flex min-h-screen flex-col bg-gradient-to-b from-slate-900 to-slate-800 circuit-pattern">
      {/* Navigation Bar */}
      <nav className="glass border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">Risk Agents</h1>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-slate-300 text-sm">
                    Welcome, {user?.email || 'User'}
                  </span>
                  <Link
                    href="/dashboard"
                    className="btn-primary px-4 py-2 rounded-lg font-semibold"
                  >
                    Dashboard
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-slate-300 hover:text-white font-medium transition-colors"
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="btn-primary px-4 py-2 rounded-lg font-semibold"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            Risk Agents 🚀
          </h1>
          <p className="text-xl text-slate-300">
            AI-Powered Project Management - Hot Reload Working! 🔥
          </p>
        </div>

        {/* Backend Status Card */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-8 border border-slate-700">
          <h2 className="text-2xl font-semibold text-white mb-4">
            System Status
          </h2>

          {loading && (
            <div className="flex items-center space-x-2 text-slate-300">
              <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full"></div>
              <span>Checking backend connection...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
              <p className="text-red-400">
                <span className="font-semibold">Error:</span> {error}
              </p>
              <p className="text-sm text-red-300 mt-2">
                Make sure the backend is running on port 8050
              </p>
            </div>
          )}

          {backendHealth && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 font-semibold">
                  Backend is healthy
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="bg-slate-900/50 rounded p-3">
                  <p className="text-sm text-slate-400">Service</p>
                  <p className="text-white font-mono">{backendHealth.service}</p>
                </div>

                <div className="bg-slate-900/50 rounded p-3">
                  <p className="text-sm text-slate-400">Version</p>
                  <p className="text-white font-mono">{backendHealth.version}</p>
                </div>

                <div className="bg-slate-900/50 rounded p-3">
                  <p className="text-sm text-slate-400">Environment</p>
                  <p className="text-white font-mono">{backendHealth.environment}</p>
                </div>

                <div className="bg-slate-900/50 rounded p-3">
                  <p className="text-sm text-slate-400">Status</p>
                  <p className="text-white font-mono">{backendHealth.status}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="card-lift bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-2">
              Claude Agent SDK
            </h3>
            <p className="text-slate-300 text-sm">
              Powered by Anthropic's Claude with Skills Framework
            </p>
          </div>

          <div className="card-lift bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-2">
              FastAPI Backend
            </h3>
            <p className="text-slate-300 text-sm">
              High-performance Python API with hot-reload
            </p>
          </div>

          <div className="card-lift bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-2">
              Next.js 15 Frontend
            </h3>
            <p className="text-slate-300 text-sm">
              React 19 with App Router and TypeScript
            </p>
          </div>
        </div>

        {/* Documentation Links */}
        <div className="text-center space-y-4">
          <div className="space-x-4">
            <a
              href="http://localhost:8050/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              API Documentation
            </a>
            <Link
              href="/api-test"
              className="inline-block bg-slate-700 hover:bg-slate-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              API Test Page
            </Link>
          </div>

          {!isAuthenticated && (
            <div className="pt-4">
              <p className="text-slate-400 mb-4">Get started with Risk Agents</p>
              <Link
                href="/login"
                className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold px-8 py-4 rounded-lg transition-colors text-lg"
              >
                Login to Continue →
              </Link>
            </div>
          )}
        </div>
        </div>
      </div>
    </main>
  )
}
