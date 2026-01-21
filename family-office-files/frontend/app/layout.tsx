import type { Metadata } from 'next'
import { ThemeProvider } from '@/components/theme/ThemeProvider'
import './globals.css'

export const metadata: Metadata = {
  title: 'Family Office Files',
  description: 'Collaboration platform for Family Office Partnership',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
