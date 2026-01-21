import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary, withErrorBoundary } from '@/components/error/ErrorBoundary'

// Component that throws an error
function ThrowError({ shouldThrow = true }: { shouldThrow?: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error message')
  }
  return <div>No error</div>
}

// Suppress console.error during tests
const originalError = console.error
beforeEach(() => {
  console.error = vi.fn()
})
afterEach(() => {
  console.error = originalError
})

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Child content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Child content')).toBeInTheDocument()
  })

  it('renders error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Test error message')).toBeInTheDocument()
  })

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error fallback</div>}>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Custom error fallback')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn()

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(onError).toHaveBeenCalledTimes(1)
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error)
    expect(onError.mock.calls[0][0].message).toBe('Test error message')
  })

  it('shows Try Again button that resets error state', () => {
    // For this test, we use a stateful wrapper to control whether the child throws
    let shouldThrow = true

    function ConditionalThrow() {
      if (shouldThrow) {
        throw new Error('Test error message')
      }
      return <div>No error</div>
    }

    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalThrow />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Change the condition before clicking retry
    shouldThrow = false

    // Click "Try Again" - this resets internal state and re-renders children
    fireEvent.click(screen.getByText('Try Again'))

    // Force re-render to pick up the new component behavior
    rerender(
      <ErrorBoundary>
        <ConditionalThrow />
      </ErrorBoundary>
    )

    expect(screen.getByText('No error')).toBeInTheDocument()
  })

  it('shows Go Home button', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Go Home')).toBeInTheDocument()
  })
})

describe('withErrorBoundary HOC', () => {
  it('wraps component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(ThrowError)

    render(<WrappedComponent shouldThrow={true} />)

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders wrapped component when no error', () => {
    function SafeComponent() {
      return <div>Safe content</div>
    }

    const WrappedComponent = withErrorBoundary(SafeComponent)

    render(<WrappedComponent />)

    expect(screen.getByText('Safe content')).toBeInTheDocument()
  })

  it('uses custom fallback when provided', () => {
    const WrappedComponent = withErrorBoundary(
      ThrowError,
      <div>HOC fallback</div>
    )

    render(<WrappedComponent shouldThrow={true} />)

    expect(screen.getByText('HOC fallback')).toBeInTheDocument()
  })
})
