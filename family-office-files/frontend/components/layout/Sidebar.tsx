'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface SidebarProps {
  user: {
    email: string
    role: string
  }
  stats?: {
    totalDeals: number
    activeDeals?: number
    recentFiles?: number
  }
}

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { href: '/deals', label: 'Deals', icon: '📁' },
]

function NavItem({ href, label, icon, isActive }: { href: string; label: string; icon: string; isActive: boolean }) {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        isActive
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </Link>
  )
}

export function Sidebar({ user, stats }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-card border-r">
      {/* Logo */}
      <div className="flex items-center h-16 px-6 border-b">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
            FO
          </div>
          <span className="font-semibold text-lg">Family Office</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavItem
            key={item.href}
            href={item.href}
            label={item.label}
            icon={item.icon}
            isActive={pathname === item.href || (item.href === '/deals' && pathname.startsWith('/deals/'))}
          />
        ))}
      </nav>

      {/* Quick Stats */}
      {stats && (
        <div className="px-4 pb-4">
          <Card className="bg-muted/50">
            <CardHeader className="pb-2 pt-4 px-4">
              <CardDescription className="text-xs">Quick Stats</CardDescription>
            </CardHeader>
            <CardContent className="px-4 pb-4 pt-0">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Total Deals</span>
                  <span className="font-medium">{stats.totalDeals}</span>
                </div>
                {stats.activeDeals !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Active</span>
                    <span className="font-medium text-green-600">{stats.activeDeals}</span>
                  </div>
                )}
                {stats.recentFiles !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Files (7d)</span>
                    <span className="font-medium">{stats.recentFiles}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* User Profile */}
      <div className="px-4 py-4 border-t">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-medium">
            {user.email[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user.email}</p>
            <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
