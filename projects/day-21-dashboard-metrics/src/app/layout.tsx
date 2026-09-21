import type { Metadata } from 'next'

import './globals.css'

export const metadata: Metadata = {
  title: 'Signal Desk | Dashboard de métricas',
  description: 'Dashboard local de métricas operativas.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}