'use client'

import { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface DashboardLayoutProps {
  children: ReactNode
  user: {
    email: string
    role: string
  }
  stats?: {
    totalDeals: number
    activeDeals?: number
    recentFiles?: number
  }
  onLogout: () => void
  onSearch?: (query: string) => void
}

export function DashboardLayout({
  children,
  user,
  stats,
  onLogout,
  onSearch,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar - hidden on mobile, fixed on desktop */}
      <Sidebar user={user} stats={stats} />

      {/* Main content area - adjusted for sidebar on desktop */}
      <div className="lg:pl-64">
        {/* Header */}
        <Header user={user} onLogout={onLogout} onSearch={onSearch} />

        {/* Main content */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
