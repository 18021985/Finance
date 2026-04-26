'use client'

import { Suspense } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import for Dashboard component
const Dashboard = dynamic(() => import('../../components/Dashboard'), {
  ssr: false,
  loading: () => <div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>
})

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>}>
      <Dashboard />
    </Suspense>
  )
}
