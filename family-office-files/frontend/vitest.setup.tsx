import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock scrollIntoView for jsdom
Element.prototype.scrollIntoView = vi.fn()

// Mock hasPointerCapture for Radix UI components
Element.prototype.hasPointerCapture = vi.fn().mockReturnValue(false)
Element.prototype.setPointerCapture = vi.fn()
Element.prototype.releasePointerCapture = vi.fn()

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))
