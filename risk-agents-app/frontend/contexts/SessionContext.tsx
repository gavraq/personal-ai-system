/**
 * SessionContext
 * Global authentication state management using React Context
 */

'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { SessionStorage, TokenUtils } from '@/lib/auth/session';
import { User, LoginCredentials, RegisterCredentials } from '@/lib/auth/types';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface SessionContextType {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  clearError: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

/**
 * useSession Hook
 *
 * Access session state and authentication methods
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { user, isAuthenticated, login, logout } = useSession();
 *
 *   if (!isAuthenticated) {
 *     return <LoginButton onClick={() => login(credentials)} />;
 *   }
 *
 *   return <div>Welcome {user?.email}</div>;
 * }
 * ```
 */
export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}

/**
 * SessionProvider Component
 *
 * Wrap your app with this provider to enable global session state
 *
 * @example
 * ```tsx
 * // In app/layout.tsx
 * <SessionProvider>
 *   <App />
 * </SessionProvider>
 * ```
 */
export interface SessionProviderProps {
  children: ReactNode;
}

export function SessionProvider({ children }: SessionProviderProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = user !== null;

  /**
   * Initialize session on mount
   * Check for existing token and validate it
   */
  useEffect(() => {
    const initializeSession = async () => {
      setIsLoading(true);
      try {
        const token = SessionStorage.getToken();
        if (!token) {
          setIsLoading(false);
          return;
        }

        // Check if token is expired
        if (TokenUtils.isExpired(token)) {
          SessionStorage.clearSession();
          setIsLoading(false);
          return;
        }

        // Validate token with backend
        try {
          const response = await api.validateToken();
          if (response.valid) {
            // Get current user
            const userData = await api.getCurrentUser();
            setUser(userData.user);
          } else {
            SessionStorage.clearSession();
          }
        } catch (err) {
          // Token validation failed, clear session
          SessionStorage.clearSession();
        }
      } catch (err) {
        console.error('Session initialization error:', err);
        SessionStorage.clearSession();
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []);

  /**
   * Login
   * Authenticate user and store session
   */
  const login = useCallback(
    async (credentials: LoginCredentials) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.login(credentials);

        // Store token
        SessionStorage.setToken(response.access_token);

        // Get user data
        const userData = await api.getCurrentUser();
        setUser(userData.user);

        // Redirect to dashboard
        router.push('/dashboard');
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Login failed';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  /**
   * Register
   * Create new user account
   */
  const register = useCallback(
    async (credentials: RegisterCredentials) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.register(credentials);

        // Store token
        SessionStorage.setToken(response.access_token);

        // Get user data
        const userData = await api.getCurrentUser();
        setUser(userData.user);

        // Redirect to dashboard
        router.push('/dashboard');
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Registration failed';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  /**
   * Logout
   * Clear session and redirect to login
   */
  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      // Call logout endpoint
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
      // Continue with logout even if API call fails
    } finally {
      // Clear local session
      SessionStorage.clearSession();
      setUser(null);
      setIsLoading(false);

      // Redirect to login
      router.push('/login');
    }
  }, [router]);

  /**
   * Refresh Session
   * Refresh access token and user data
   */
  const refreshSession = useCallback(async () => {
    try {
      const token = SessionStorage.getToken();
      if (!token) {
        return;
      }

      // Refresh token
      const response = await api.refreshToken();
      SessionStorage.setToken(response.access_token);

      // Get updated user data
      const userData = await api.getCurrentUser();
      setUser(userData.user);
    } catch (err) {
      console.error('Session refresh error:', err);
      // If refresh fails, clear session
      SessionStorage.clearSession();
      setUser(null);
      router.push('/login');
    }
  }, [router]);

  /**
   * Clear Error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: SessionContextType = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshSession,
    clearError,
  };

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}

/**
 * withAuth HOC
 *
 * Higher-order component to protect routes
 *
 * @example
 * ```tsx
 * const ProtectedPage = withAuth(MyPage);
 * ```
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useSession();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login');
      }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-slate-300">Loading...</div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return null;
    }

    return <Component {...props} />;
  };
}

/**
 * withGuest HOC
 *
 * Higher-order component to redirect authenticated users
 *
 * @example
 * ```tsx
 * const LoginPage = withGuest(LoginForm);
 * ```
 */
export function withGuest<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> {
  return function GuestComponent(props: P) {
    const { isAuthenticated, isLoading } = useSession();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && isAuthenticated) {
        router.push('/dashboard');
      }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-slate-300">Loading...</div>
        </div>
      );
    }

    if (isAuthenticated) {
      return null;
    }

    return <Component {...props} />;
  };
}
