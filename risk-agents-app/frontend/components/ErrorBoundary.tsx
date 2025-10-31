/**
 * ErrorBoundary Component
 * Catch React errors and display fallback UI
 */

'use client';

import React, { Component, ReactNode, ErrorInfo } from 'react';
import { Button } from './ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/Card';

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Custom fallback UI */
  fallback?: (error: Error, resetError: () => void) => ReactNode;
  /** Callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Show detailed error in development */
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary Class Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 *
 * @example
 * ```tsx
 * <ErrorBoundary>
 *   <MyApp />
 * </ErrorBoundary>
 * ```
 *
 * @example
 * ```tsx
 * <ErrorBoundary
 *   fallback={(error, reset) => (
 *     <div>
 *       <h1>Custom Error UI</h1>
 *       <p>{error.message}</p>
 *       <button onClick={reset}>Try Again</button>
 *     </div>
 *   )}
 *   onError={(error, errorInfo) => {
 *     logErrorToService(error, errorInfo);
 *   }}
 * >
 *   <MyApp />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call custom error handler
    this.props.onError?.(error, errorInfo);
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback, showDetails = process.env.NODE_ENV === 'development' } = this.props;

    if (hasError && error) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback(error, this.resetError);
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <Card variant="bordered" className="max-w-2xl w-full border-red-500/30 bg-red-500/5">
            <CardHeader>
              <CardTitle className="text-red-400 flex items-center gap-2">
                <span className="text-2xl">⚠️</span>
                Something went wrong
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-4">
                <p className="text-slate-300">
                  An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
                </p>

                {showDetails && (
                  <>
                    {/* Error Message */}
                    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                      <h3 className="text-sm font-semibold text-red-400 mb-2">Error Message:</h3>
                      <pre className="text-xs text-slate-300 overflow-x-auto">
                        {error.message}
                      </pre>
                    </div>

                    {/* Stack Trace */}
                    {error.stack && (
                      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <h3 className="text-sm font-semibold text-red-400 mb-2">Stack Trace:</h3>
                        <pre className="text-xs text-slate-400 overflow-x-auto max-h-48 overflow-y-auto">
                          {error.stack}
                        </pre>
                      </div>
                    )}

                    {/* Component Stack */}
                    {errorInfo?.componentStack && (
                      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <h3 className="text-sm font-semibold text-red-400 mb-2">Component Stack:</h3>
                        <pre className="text-xs text-slate-400 overflow-x-auto max-h-48 overflow-y-auto">
                          {errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </>
                )}
              </div>
            </CardContent>

            <CardFooter>
              <div className="flex gap-2">
                <Button variant="gradient" onClick={this.resetError}>
                  Try Again
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.location.reload()}
                >
                  Reload Page
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => window.history.back()}
                >
                  Go Back
                </Button>
              </div>
            </CardFooter>
          </Card>
        </div>
      );
    }

    return children;
  }
}

/**
 * useErrorHandler Hook
 *
 * Functional way to throw errors to the nearest error boundary
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const throwError = useErrorHandler();
 *
 *   const handleClick = async () => {
 *     try {
 *       await riskyOperation();
 *     } catch (err) {
 *       throwError(err);
 *     }
 *   };
 *
 *   return <button onClick={handleClick}>Do Something</button>;
 * }
 * ```
 */
export function useErrorHandler() {
  const [, setError] = React.useState();

  return React.useCallback((error: unknown) => {
    setError(() => {
      throw error;
    });
  }, []);
}
