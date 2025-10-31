/**
 * Login Page
 * User authentication with email and password
 */

import Link from 'next/link'
import LoginForm from '@/components/auth/LoginForm'

export const metadata = {
  title: 'Login | Risk Agents',
  description: 'Sign in to your Risk Agents account',
}

export default function LoginPage() {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-card text-white">Sign In</h2>
        <p className="text-slate-300 mt-1">Welcome back! Please sign in to continue.</p>
      </div>

      <LoginForm />

      <div className="mt-6 text-center">
        <p className="text-sm text-slate-300">
          Don't have an account?{' '}
          <Link href="/register" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
            Create account
          </Link>
        </p>
      </div>
    </div>
  )
}
