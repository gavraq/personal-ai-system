import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { ToastProvider, useToast } from '@/components/ui/toast'

// Test component that uses toast
function ToastTestComponent() {
  const { success, error, warning, info, toasts } = useToast()

  return (
    <div>
      <button onClick={() => success('Success message', 'Description')}>
        Show Success
      </button>
      <button onClick={() => error('Error message')}>Show Error</button>
      <button onClick={() => warning('Warning message')}>Show Warning</button>
      <button onClick={() => info('Info message')}>Show Info</button>
      <div data-testid="toast-count">{toasts.length}</div>
    </div>
  )
}

function renderWithToastProvider(children: React.ReactNode) {
  return render(<ToastProvider>{children}</ToastProvider>)
}

describe('ToastProvider', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders children correctly', () => {
    renderWithToastProvider(<div>Child content</div>)

    expect(screen.getByText('Child content')).toBeInTheDocument()
  })

  it('shows success toast when success is called', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Success'))
    })

    expect(screen.getByText('Success message')).toBeInTheDocument()
    expect(screen.getByText('Description')).toBeInTheDocument()
  })

  it('shows error toast when error is called', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Error'))
    })

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('shows warning toast when warning is called', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Warning'))
    })

    expect(screen.getByText('Warning message')).toBeInTheDocument()
  })

  it('shows info toast when info is called', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Info'))
    })

    expect(screen.getByText('Info message')).toBeInTheDocument()
  })

  it('increments toast count when toast is added', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    expect(screen.getByTestId('toast-count')).toHaveTextContent('0')

    await act(async () => {
      fireEvent.click(screen.getByText('Show Success'))
    })

    expect(screen.getByTestId('toast-count')).toHaveTextContent('1')
  })

  it('can show multiple toasts', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Success'))
      fireEvent.click(screen.getByText('Show Error'))
    })

    expect(screen.getByTestId('toast-count')).toHaveTextContent('2')
    expect(screen.getByText('Success message')).toBeInTheDocument()
    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('auto-dismisses toast after duration', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Success'))
    })

    expect(screen.getByText('Success message')).toBeInTheDocument()

    // Fast forward past the default 5000ms duration
    await act(async () => {
      vi.advanceTimersByTime(6000)
    })

    expect(screen.queryByText('Success message')).not.toBeInTheDocument()
  })

  it('dismisses toast when X button is clicked', async () => {
    renderWithToastProvider(<ToastTestComponent />)

    await act(async () => {
      fireEvent.click(screen.getByText('Show Success'))
    })

    expect(screen.getByText('Success message')).toBeInTheDocument()

    // Click dismiss button
    const dismissButton = screen.getByRole('button', { name: /dismiss/i })
    await act(async () => {
      fireEvent.click(dismissButton)
    })

    expect(screen.queryByText('Success message')).not.toBeInTheDocument()
  })
})

describe('useToast', () => {
  it('throws error when used outside ToastProvider', () => {
    function BadComponent() {
      useToast()
      return null
    }

    expect(() => render(<BadComponent />)).toThrow(
      'useToast must be used within a ToastProvider'
    )
  })
})
