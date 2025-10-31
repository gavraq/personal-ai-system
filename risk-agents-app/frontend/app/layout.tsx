import type { Metadata } from 'next'
import './globals.css'
import { SessionProvider } from '@/contexts/SessionContext'
import { WebSocketProvider } from '@/contexts/WebSocketContext'
import { ToastProvider } from '@/components/ui/Toast'
import { ErrorBoundary } from '@/components/ErrorBoundary'

export const metadata: Metadata = {
  title: 'Risk Agents - AI-Powered Project Management',
  description: 'Transform project complexity into clarity with AI-powered risk management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900">
        <ErrorBoundary>
          <SessionProvider>
            <WebSocketProvider autoConnect={true}>
              <ToastProvider position="top-right" maxToasts={5}>
                {children}
              </ToastProvider>
            </WebSocketProvider>
          </SessionProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
