import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ThemeToggle } from '@/components/theme/ThemeToggle'
import { ThemeProvider } from '@/components/theme/ThemeProvider'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock matchMedia
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

function renderWithTheme(ui: React.ReactElement) {
  return render(<ThemeProvider>{ui}</ThemeProvider>)
}

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorageMock.clear()
    mockMatchMedia(false) // Default to light system preference
    document.documentElement.classList.remove('light', 'dark')
  })

  it('renders theme toggle button', async () => {
    renderWithTheme(<ThemeToggle />)

    // Wait for mounting to complete
    await waitFor(() => {
      const button = screen.getByRole('button', { name: /toggle theme/i })
      expect(button).toBeInTheDocument()
    })
  })

  it('displays sun icon in light mode', async () => {
    localStorageMock.setItem('family-office-theme', 'light')
    renderWithTheme(<ThemeToggle />)

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /toggle theme/i })
      // Sun icon should be present (we can check the SVG path exists)
      const svg = button.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })
  })

  it('displays moon icon in dark mode', async () => {
    localStorageMock.setItem('family-office-theme', 'dark')
    renderWithTheme(<ThemeToggle />)

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /toggle theme/i })
      const svg = button.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })
  })

  it('cycles through themes on click: light -> dark -> system -> light', async () => {
    localStorageMock.setItem('family-office-theme', 'light')
    renderWithTheme(<ThemeToggle />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /toggle theme/i })).toBeInTheDocument()
    })

    const button = screen.getByRole('button', { name: /toggle theme/i })

    // Click to go to dark
    fireEvent.click(button)
    expect(localStorageMock.getItem('family-office-theme')).toBe('dark')

    // Click to go to system
    fireEvent.click(button)
    expect(localStorageMock.getItem('family-office-theme')).toBe('system')

    // Click to go back to light
    fireEvent.click(button)
    expect(localStorageMock.getItem('family-office-theme')).toBe('light')
  })

  it('persists theme preference to localStorage', async () => {
    renderWithTheme(<ThemeToggle />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /toggle theme/i })).toBeInTheDocument()
    })

    const button = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(button)

    // Should have saved to localStorage
    const stored = localStorageMock.getItem('family-office-theme')
    expect(stored).toBeTruthy()
  })

  it('has accessible label', async () => {
    renderWithTheme(<ThemeToggle />)

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /toggle theme/i })
      expect(button).toHaveAttribute('aria-label')
    })
  })
})

describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorageMock.clear()
    mockMatchMedia(false)
    document.documentElement.classList.remove('light', 'dark')
  })

  it('applies light class by default', async () => {
    renderWithTheme(<div>Test</div>)

    // After mounting, should apply light class
    await waitFor(() => {
      expect(document.documentElement.classList.contains('light')).toBe(true)
    })
  })

  it('applies dark class when dark theme is set', async () => {
    localStorageMock.setItem('family-office-theme', 'dark')
    renderWithTheme(<div>Test</div>)

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })

  it('respects system preference when set to system', async () => {
    mockMatchMedia(true) // System prefers dark
    localStorageMock.setItem('family-office-theme', 'system')
    renderWithTheme(<div>Test</div>)

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })

  it('restores theme from localStorage on mount', async () => {
    localStorageMock.setItem('family-office-theme', 'dark')
    renderWithTheme(<ThemeToggle />)

    // Should display the dark mode state
    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })
})
