import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Utility HITL Portal',
  description: 'Demand Response Coordination System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}