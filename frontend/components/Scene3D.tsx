'use client'

export default function Scene3D() {
  return (
    <div className="fixed inset-0 w-full h-full">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 animate-pulse" />
      
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-float" />
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      
      {/* Grid pattern */}
      <div className="absolute inset-0 grid-pattern opacity-20" />
    </div>
  )
}
