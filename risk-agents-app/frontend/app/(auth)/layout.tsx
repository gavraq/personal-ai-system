/**
 * Authentication Layout
 * Shared layout for login and register pages
 */

import { ReactNode } from 'react'

interface AuthLayoutProps {
  children: ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 circuit-pattern flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo/Branding */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Risk Agents</h1>
          <p className="text-slate-300">AI-Powered Risk Management Platform</p>
        </div>

        {/* Auth Card */}
        <div className="glass rounded-lg shadow-glow-blue p-8">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-slate-400">
          <p>&copy; 2025 Risk Agents. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
