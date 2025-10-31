/**
 * Register Page
 * User registration with email, password, and optional full name
 */

import Link from 'next/link'
import RegisterForm from '@/components/auth/RegisterForm'

export const metadata = {
  title: 'Register | Risk Agents',
  description: 'Create your Risk Agents account',
}

export default function RegisterPage() {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-card text-white">Create Account</h2>
        <p className="text-slate-300 mt-1">Join Risk Agents to get started.</p>
      </div>

      <RegisterForm />

      <div className="mt-6 text-center">
        <p className="text-sm text-slate-300">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
