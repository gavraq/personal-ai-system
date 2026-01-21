'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

interface HeaderProps {
  user: {
    email: string
    role: string
  }
  onLogout: () => void
  onSearch?: (query: string) => void
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  )
}

function BellIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
      />
    </svg>
  )
}

function MenuIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 6h16M4 12h16M4 18h16"
      />
    </svg>
  )
}

function UserAvatar({ email }: { email: string }) {
  return (
    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-medium text-sm">
      {email[0].toUpperCase()}
    </div>
  )
}

export function Header({ user, onLogout, onSearch }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch?.(searchQuery)
  }

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-background px-4 lg:px-6">
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        aria-label="Toggle menu"
      >
        <MenuIcon className="w-5 h-5" />
      </Button>

      {/* Mobile Logo */}
      <Link href="/dashboard" className="lg:hidden flex items-center gap-2">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
          FO
        </div>
      </Link>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex-1 max-w-md hidden md:flex">
        <div className="relative w-full">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search deals, files..."
            className="pl-9 bg-muted/50"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </form>

      {/* Mobile Search Button */}
      <Button variant="ghost" size="icon" className="md:hidden ml-auto" aria-label="Search">
        <SearchIcon className="w-5 h-5" />
      </Button>

      {/* Right Side Actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <BellIcon className="w-5 h-5" />
          {/* Notification badge - can be conditionally shown */}
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
        </Button>

        {/* User Menu */}
        <Dialog open={isUserMenuOpen} onOpenChange={setIsUserMenuOpen}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <UserAvatar email={user.email} />
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[300px]">
            <DialogHeader>
              <DialogTitle>Account</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <UserAvatar email={user.email} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user.email}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                </div>
              </div>
              <div className="space-y-1">
                <Button
                  variant="ghost"
                  className="w-full justify-start"
                  onClick={() => {
                    setIsUserMenuOpen(false)
                  }}
                >
                  Settings
                </Button>
                <Button
                  variant="ghost"
                  className="w-full justify-start text-destructive hover:text-destructive"
                  onClick={() => {
                    setIsUserMenuOpen(false)
                    onLogout()
                  }}
                >
                  Sign Out
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-50 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <div className="fixed inset-0 bg-black/50" />
          <div
            className="fixed inset-y-0 left-0 w-64 bg-background p-4 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <Link href="/dashboard" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
                  FO
                </div>
                <span className="font-semibold">Family Office</span>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <span className="text-xl">&times;</span>
              </Button>
            </div>

            <nav className="space-y-1">
              <Link
                href="/dashboard"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:bg-muted"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <span>🏠</span>
                <span>Dashboard</span>
              </Link>
              <Link
                href="/deals"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:bg-muted"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <span>📁</span>
                <span>Deals</span>
              </Link>
            </nav>

            {/* Mobile User Profile */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <UserAvatar email={user.email} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user.email}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

export default Header
