'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function APITestPage() {
  const [results, setResults] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const testAPI = async () => {
      const testResults: Record<string, any> = {}

      // Test System Health
      try {
        const health = await api.health()
        testResults.systemHealth = {
          status: 'SUCCESS',
          data: health,
        }
      } catch (error: any) {
        testResults.systemHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      // Test Auth Health
      try {
        const authHealth = await api.authHealth()
        testResults.authHealth = {
          status: 'SUCCESS',
          data: authHealth,
        }
      } catch (error: any) {
        testResults.authHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      // Test Query Health
      try {
        const queryHealth = await api.queryHealth()
        testResults.queryHealth = {
          status: 'SUCCESS',
          data: queryHealth,
        }
      } catch (error: any) {
        testResults.queryHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      // Test Skills Health
      try {
        const skillsHealth = await api.skillsHealth()
        testResults.skillsHealth = {
          status: 'SUCCESS',
          data: skillsHealth,
        }
      } catch (error: any) {
        testResults.skillsHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      // Test Knowledge Health
      try {
        const knowledgeHealth = await api.knowledgeHealth()
        testResults.knowledgeHealth = {
          status: 'SUCCESS',
          data: knowledgeHealth,
        }
      } catch (error: any) {
        testResults.knowledgeHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      // Test WebSocket Health
      try {
        const wsHealth = await api.websocketHealth()
        testResults.websocketHealth = {
          status: 'SUCCESS',
          data: wsHealth,
        }
      } catch (error: any) {
        testResults.websocketHealth = {
          status: 'ERROR',
          error: error.message,
        }
      }

      setResults(testResults)
      setLoading(false)
    }

    testAPI()
  }, [])

  return (
    <main className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">
          API Client Test Results
        </h1>

        {loading ? (
          <div className="text-white">Loading...</div>
        ) : (
          <div className="space-y-4">
            {Object.entries(results).map(([key, value]) => (
              <div
                key={key}
                className="bg-slate-800 rounded-lg p-6 border border-slate-700"
              >
                <h2 className="text-xl font-semibold text-white mb-2">
                  {key}
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-slate-400">Status:</span>
                    <span
                      className={`font-mono ${
                        value.status === 'SUCCESS'
                          ? 'text-green-400'
                          : 'text-red-400'
                      }`}
                    >
                      {value.status}
                    </span>
                  </div>
                  {value.data && (
                    <div>
                      <span className="text-sm text-slate-400">Data:</span>
                      <pre className="mt-2 bg-slate-900 rounded p-3 text-xs text-slate-300 overflow-x-auto">
                        {JSON.stringify(value.data, null, 2)}
                      </pre>
                    </div>
                  )}
                  {value.error && (
                    <div>
                      <span className="text-sm text-red-400">Error:</span>
                      <pre className="mt-2 bg-red-900/20 rounded p-3 text-xs text-red-300">
                        {value.error}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <a
            href="/"
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </main>
  )
}
