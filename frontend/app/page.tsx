'use client'

import { useState, useEffect, Suspense } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import { TrendingUp, TrendingDown, Activity, Zap, Globe, BarChart3, Brain, Sparkles, ArrowRight, Shield, Target, Layers, ChevronRight } from 'lucide-react'

// Dynamic import for 3D components to avoid SSR issues
const Scene3D = dynamic(() => import('../components/Scene3D'), {
  ssr: false,
  loading: () => <div className="fixed inset-0 bg-background" />
})

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLaunchDashboard = () => {
    router.push('/dashboard')
  }

  const handleViewDocs = () => {
    router.push('/docs')
  }

  const handleGetStarted = () => {
    router.push('/dashboard')
  }

  const quickActions = [
    { label: 'Dashboard', icon: BarChart3, path: '/dashboard', color: 'from-blue-500 to-cyan-500' },
    { label: 'Strategies', icon: Target, path: '/strategies', color: 'from-purple-500 to-pink-500' },
    { label: 'Intelligence', icon: Brain, path: '/intelligence', color: 'from-orange-500 to-red-500' },
    { label: 'Recommendations', icon: TrendingUp, path: '/recommendations', color: 'from-green-500 to-emerald-500' },
  ]

  if (!mounted) return null

  return (
    <main className="min-h-screen bg-background relative overflow-hidden">
      {/* 3D Background */}
      <div className="fixed inset-0 z-0">
        <Suspense fallback={<div className="fixed inset-0 bg-background" />}>
          <Scene3D />
        </Suspense>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="fixed inset-0 grid-pattern opacity-30 z-0 pointer-events-none" />

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex items-center justify-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-6xl"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="inline-block mb-6"
            >
              <div className="w-24 h-24 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center neon-glow">
                <Brain className="w-12 h-12 text-white" />
              </div>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-6xl md:text-8xl font-bold mb-6 gradient-text"
            >
              Financial Intelligence
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-xl md:text-2xl text-text-secondary mb-8 max-w-3xl mx-auto leading-relaxed"
            >
              Institutional-grade market intelligence with AI-powered insights, 
              multi-asset analysis, and forward-looking scenarios
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="flex flex-wrap gap-4 justify-center mb-12"
            >
              <button 
                onClick={handleLaunchDashboard}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-white hover:scale-105 transition-transform neon-glow cursor-pointer flex items-center gap-2"
              >
                Launch Dashboard
                <ArrowRight className="w-5 h-5" />
              </button>
              <button 
                onClick={handleViewDocs}
                className="px-8 py-4 border border-accent rounded-lg font-semibold text-accent hover:bg-accent/10 transition-colors cursor-pointer"
              >
                View Documentation
              </button>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto"
            >
              {quickActions.map((action, index) => (
                <motion.button
                  key={action.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1 + index * 0.1 }}
                  onClick={() => router.push(action.path)}
                  className="glass rounded-xl p-4 hover:border-accent/50 transition-all cursor-pointer group"
                >
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${action.color} flex items-center justify-center mb-2 mx-auto group-hover:scale-110 transition-transform`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-sm font-semibold text-text-primary">{action.label}</div>
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.h2
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold text-center mb-4 gradient-text"
            >
              Intelligence Layers
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-text-secondary text-center mb-16 max-w-2xl mx-auto"
            >
              A comprehensive suite of AI-powered tools for institutional-grade market analysis
            </motion.p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="card-3d"
                >
                  <div className="card-3d-inner glass rounded-2xl p-6 h-full hover:border-accent/50 transition-colors">
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center mb-4"
                    >
                      <feature.icon className="w-8 h-8 text-accent" />
                    </motion.div>
                    <h3 className="text-2xl font-bold mb-3 text-text-primary">{feature.title}</h3>
                    <p className="text-text-secondary leading-relaxed">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.h2
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold text-center mb-16 gradient-text"
            >
              Platform Capabilities
            </motion.h2>

            <div className="grid md:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.5 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center"
                >
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="glass rounded-2xl p-8"
                  >
                    <div className="text-5xl font-bold gradient-text mb-2">{stat.value}</div>
                    <div className="text-text-secondary">{stat.label}</div>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Key Benefits Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.h2
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold text-center mb-16 gradient-text"
            >
              Why Choose Us
            </motion.h2>

            <div className="grid md:grid-cols-2 gap-6">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="glass rounded-2xl p-6 flex gap-4 hover:border-accent/30 transition-colors"
                >
                  <div className="p-3 bg-accent/20 rounded-lg flex-shrink-0">
                    <benefit.icon className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-text-primary">{benefit.title}</h3>
                    <p className="text-text-secondary">{benefit.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto text-center"
          >
            <div className="glass rounded-3xl p-12 neon-glow">
              <Sparkles className="w-16 h-16 text-accent mx-auto mb-6" />
              <h2 className="text-4xl font-bold mb-4 gradient-text">Ready to Transform Your Analysis?</h2>
              <p className="text-text-secondary mb-8 text-lg">
                Experience institutional-grade financial intelligence with real-time insights, 
                AI-powered predictions, and advanced analytics.
              </p>
              <button 
                onClick={handleGetStarted}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-white hover:scale-105 transition-transform cursor-pointer flex items-center gap-2 mx-auto"
              >
                Get Started
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="py-8 px-4 border-t border-white/10">
          <div className="max-w-7xl mx-auto text-center text-text-secondary text-sm">
            <p>© 2026 Financial Intelligence System. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </main>
  )
}

const features = [
  {
    icon: Brain,
    title: 'ML Ensemble',
    description: 'XGBoost, LightGBM, CatBoost ensemble with 15 technical features for probabilistic predictions'
  },
  {
    icon: Globe,
    title: 'Multi-Asset',
    description: 'Equities, bonds, commodities, crypto, and forex analysis with asset-class-specific insights'
  },
  {
    icon: BarChart3,
    title: 'Macro Intelligence',
    description: 'Bank-level macro analysis covering rates, inflation, central banks, and economic cycles'
  },
  {
    icon: Activity,
    title: 'Real-Time Data',
    description: '30-second polling during market hours with instant updates and alerts'
  },
  {
    icon: TrendingUp,
    title: 'Scenario Analysis',
    description: 'IF-THEN forward-looking scenarios with probability-based asset implications'
  },
  {
    icon: Zap,
    title: 'Auto-Learning',
    description: 'Continuous validation, hyperparameter optimization, and automatic retraining'
  }
]

const stats = [
  { value: '40+', label: 'Signal Types' },
  { value: '5', label: 'Asset Classes' },
  { value: '12', label: 'ML Models' },
  { value: '0-100', label: 'Composite Score' }
]

const benefits = [
  {
    icon: Shield,
    title: 'Production-Grade Reliability',
    description: 'Timeout enforcement, data quality safeguards, and graceful fallback mechanisms ensure system stability.'
  },
  {
    icon: Target,
    title: 'Actionable Insights',
    description: 'Get clear buy/sell/hold recommendations with position sizing, stop losses, and take profit targets.'
  },
  {
    icon: Layers,
    title: 'Multi-Layer Analysis',
    description: 'Combine technical, fundamental, and macro signals for a comprehensive market view.'
  },
  {
    icon: Activity,
    title: 'Real-Time Updates',
    description: 'Stay informed with live intelligence feed and instant alerts on market-moving events.'
  }
]
