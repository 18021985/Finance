'use client'

import { useState, useEffect, Suspense, useRef } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import { TrendingUp, TrendingDown, Activity, Brain, Globe, Zap, BarChart3, Sparkles, AlertTriangle, Target, Layers, Newspaper, ArrowRight, Home, Settings, RefreshCw, ChevronRight } from 'lucide-react'
import { API_BASE_URL, intelligenceApi } from '../lib/api'

// Dynamic import for 3D components to avoid SSR issues
const Scene3D = dynamic(() => import('./Scene3D'), {
  ssr: false,
  loading: () => <div className="fixed inset-0 bg-background" />
})

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState('AAPL')
  const [compositeScore, setCompositeScore] = useState(0)
  const [riskSentiment, setRiskSentiment] = useState('bullish')
  const [activeTab, setActiveTab] = useState('Markets')
  const [loading, setLoading] = useState(true)
  const [intelligenceData, setIntelligenceData] = useState<any>(null)
  const [marketOverview, setMarketOverview] = useState<any>(null)
  const [intelligenceFeed, setIntelligenceFeed] = useState<any[]>([])
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected')
  const [errors, setErrors] = useState<{market?: string; feed?: string; intelligence?: string}>({})
  const router = useRouter()
  const didInit = useRef(false)

  useEffect(() => {
    if (didInit.current) return
    didInit.current = true
    fetchInitialData()
  }, [])

  useEffect(() => {
    if (selectedAsset) {
      fetchIntelligenceData(selectedAsset)
    }
  }, [selectedAsset])

  const fetchInitialData = async () => {
    setLoading(true)
    setApiStatus('connected')
    setErrors({})

    const results = await Promise.allSettled([
      intelligenceApi.getMacroIntelligence(),
      intelligenceApi.getIntelligenceFeed()
    ])

    const newErrors: {market?: string; feed?: string} = {}

    if (results[0].status === 'fulfilled') {
      setMarketOverview(results[0].value)
    } else {
      newErrors.market = results[0].reason?.message || 'Failed to load market data'
      setApiStatus('error')
    }

    if (results[1].status === 'fulfilled') {
      setIntelligenceFeed(results[1].value)
    } else {
      newErrors.feed = results[1].reason?.message || 'Failed to load intelligence feed'
    }

    setErrors(newErrors)
    setLoading(false)
  }

  const fetchIntelligenceData = async (symbol: string) => {
    try {
      setLoading(true)
      const data = await intelligenceApi.getCompositeScore(symbol)
      setIntelligenceData(data)
      setCompositeScore(data.composite_score?.total_score || 0)
      setErrors(prev => ({ ...prev, intelligence: undefined }))
    } catch (error: any) {
      console.error('Error fetching intelligence data:', error)
      setErrors(prev => ({ ...prev, intelligence: error.message || 'Failed to load intelligence data' }))
      setApiStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (tab: string) => {
    if (tab === 'Markets') {
      router.push('/dashboard')
    } else if (tab === 'Strategies') {
      router.push('/strategies')
    } else if (tab === 'Portfolio') {
      router.push('/portfolio')
    } else if (tab === 'Intelligence') {
      router.push('/intelligence')
    } else if (tab === 'Scenarios') {
      router.push('/scenarios')
    } else if (tab === 'Auto-Learning') {
      router.push('/auto-learning')
    } else if (tab === 'Indian Market') {
      router.push('/indian-market')
    } else if (tab === 'Market Intelligence') {
      router.push('/market-intelligence')
    } else if (tab === 'Recommendations') {
      router.push('/recommendations')
    }
  }

  const handleAssetChange = (asset: string) => {
    setSelectedAsset(asset)
  }

  const handleBackToHome = () => {
    router.push('/')
  }

  const handleRefresh = () => {
    fetchInitialData()
    if (selectedAsset) {
      fetchIntelligenceData(selectedAsset)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-500'
    if (score >= 60) return 'text-blue-400'
    if (score >= 45) return 'text-yellow-500'
    if (score >= 30) return 'text-orange-500'
    return 'text-red-500'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 75) return 'Strong Buy'
    if (score >= 60) return 'Buy'
    if (score >= 45) return 'Hold'
    if (score >= 30) return 'Sell'
    return 'Strong Sell'
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      {/* 3D Background */}
      <div className="fixed inset-0 z-0 opacity-20">
        <Suspense fallback={<div className="fixed inset-0 bg-background" />}>
          <Scene3D />
        </Suspense>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center justify-between"
        >
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold gradient-text">Financial Intelligence Dashboard</h1>
                <p className="text-text-secondary text-sm">Real-time market intelligence with AI-powered insights</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs mt-3">
              <span className="text-text-secondary">Status:</span>
              <span className={`font-semibold ${
                apiStatus === 'connected' ? 'text-green-500' :
                apiStatus === 'error' ? 'text-red-500' :
                'text-yellow-500'
              }`}>
                {apiStatus === 'connected' ? '● Connected' :
                 apiStatus === 'error' ? '● Error' :
                 '● Connecting...'}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              className="p-2 glass rounded-lg hover:bg-accent/20 transition-colors cursor-pointer"
              title="Refresh Data"
            >
              <RefreshCw className="w-5 h-5 text-accent" />
            </button>
            <button
              onClick={handleBackToHome}
              className="px-4 py-2 glass rounded-lg text-accent hover:bg-accent/10 transition-colors cursor-pointer flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Home
            </button>
          </div>
        </motion.div>

        {/* Top Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {errors.market ? (
            <div className="col-span-4 glass rounded-xl p-4 border border-red-500/30">
              <div className="flex items-center gap-2 text-red-500">
                <AlertTriangle className="w-5 h-5" />
                <span className="text-sm font-semibold">Market Data Error</span>
              </div>
              <div className="text-xs text-text-secondary mt-1">{errors.market}</div>
            </div>
          ) : marketOverview ? [
            {
              label: 'Fed Funds Rate',
              value: marketOverview.interest_rates?.fed ? '5.25%' : 'Loading',
              change: '+0.25%',
              icon: TrendingUp,
              color: 'bullish'
            },
            {
              label: 'CPI Inflation',
              value: marketOverview.inflation?.cpi ? `${marketOverview.inflation.cpi}%` : 'Loading',
              change: '-0.1%',
              icon: Activity,
              color: 'bearish'
            },
            {
              label: '10Y Treasury',
              value: marketOverview.yield_curve?.ten_year ? `${marketOverview.yield_curve.ten_year}%` : 'Loading',
              change: '+0.05%',
              icon: TrendingUp,
              color: 'bullish'
            },
            {
              label: 'Risk Sentiment',
              value: marketOverview.risk_sentiment?.interpretation || 'Loading',
              change: marketOverview.risk_sentiment?.interpretation || 'Loading',
              icon: Brain,
              color: marketOverview.risk_sentiment?.interpretation?.toLowerCase().includes('bullish') ? 'bullish' : 'bearish'
            },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-xl p-4 hover:border-accent/50 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="p-2 bg-accent/20 rounded-lg group-hover:scale-110 transition-transform">
                  <stat.icon className={`w-4 h-4 text-${stat.color}`} />
                </div>
                <span className={`text-sm font-semibold ${stat.change?.startsWith('+') ? 'text-bullish' : 'text-bearish'}`}>
                  {stat.change}
                </span>
              </div>
              <div className="text-2xl font-bold text-text-primary">{stat.value}</div>
              <div className="text-sm text-text-secondary">{stat.label}</div>
            </motion.div>
          )) : (
            <div className="col-span-4 text-center text-text-secondary">Loading market data...</div>
          )}
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Left Panel - Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-lg font-bold mb-4 gradient-text flex items-center gap-2">
              <Layers className="w-5 h-5" />
              Navigation
            </h3>
            <div className="space-y-2">
              {[
                { icon: Globe, label: 'Markets', active: true },
                { icon: BarChart3, label: 'Strategies', active: false },
                { icon: Layers, label: 'Portfolio', active: false },
                { icon: Brain, label: 'Intelligence', active: false },
                { icon: Target, label: 'Scenarios', active: false },
                { icon: Zap, label: 'Auto-Learning', active: false },
                { icon: Globe, label: 'Indian Market', active: false },
                { icon: Activity, label: 'Market Intelligence', active: false },
                { icon: TrendingUp, label: 'Recommendations', active: false },
              ].map((item, index) => (
                <motion.button
                  key={item.label}
                  onClick={() => handleTabChange(item.label)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full flex items-center justify-between gap-3 p-3 rounded-lg transition-all cursor-pointer ${
                    item.active ? 'bg-accent/20 text-accent border border-accent/30' : 'hover:bg-panel-bg text-text-secondary'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </div>
                  {item.active && <ChevronRight className="w-4 h-4" />}
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Center Panel - Main Analysis */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-3 space-y-6"
          >
            {/* Composite Score Card */}
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold gradient-text flex items-center gap-2">
                  <Brain className="w-6 h-6" />
                  Composite Intelligence Score
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {['AAPL', 'GOOGL', 'BTC', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'ITC.NS'].map((asset) => (
                    <button
                      key={asset}
                      onClick={() => handleAssetChange(asset)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                        selectedAsset === asset ? 'bg-accent/20 text-accent border border-accent/30' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                      }`}
                    >
                      {asset}
                    </button>
                  ))}
                </div>
              </div>

              {loading ? (
                <div className="text-center py-12 text-text-secondary">Loading intelligence data...</div>
              ) : (
                <>
                  <div className="flex items-center justify-center mb-6">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 200 }}
                      className="relative"
                    >
                      <div className="w-56 h-56 rounded-full border-8 border-accent/20 flex items-center justify-center neon-glow">
                        <div className="text-center">
                          <div className={`text-6xl font-bold ${getScoreColor(compositeScore)}`}>{compositeScore}</div>
                          <div className="text-sm text-text-secondary">/ 100</div>
                          <div className={`text-xs font-semibold mt-1 ${getScoreColor(compositeScore)}`}>
                            {getScoreLabel(compositeScore)}
                          </div>
                        </div>
                      </div>
                      <motion.div
                        className="absolute inset-0 rounded-full border-8 border-accent/40"
                        initial={{ rotate: -90 }}
                        animate={{ rotate: (compositeScore / 100) * 360 - 90 }}
                        transition={{ duration: 1.5, ease: 'easeOut' }}
                        style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}
                      />
                    </motion.div>
                  </div>

                  <div className="grid grid-cols-5 gap-4">
                    {intelligenceData?.composite_score ? [
                      { label: 'Technical', value: Math.round(intelligenceData.composite_score.technical_score || 0), color: 'text-blue-400' },
                      { label: 'Momentum', value: Math.round(intelligenceData.composite_score.momentum_score || 0), color: 'text-purple-400' },
                      { label: 'Macro', value: Math.round(intelligenceData.composite_score.macro_score || 0), color: 'text-green-400' },
                      { label: 'Fundamental', value: Math.round(intelligenceData.composite_score.fundamental_score || 0), color: 'text-yellow-400' },
                      { label: 'ML', value: Math.round(intelligenceData.composite_score.ml_probability || 0), color: 'text-pink-400' },
                    ].map((item, index) => (
                      <motion.div
                        key={item.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="text-center p-3 bg-panel-bg/50 rounded-lg"
                      >
                        <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
                        <div className="text-xs text-text-secondary">{item.label}</div>
                      </motion.div>
                    )) : (
                      <div className="col-span-5 text-center text-text-secondary">No component data available</div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Insight Cards */}
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass rounded-2xl p-6 border-l-4 border-l-bullish"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-bullish/20 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-bullish" />
                  </div>
                  <h3 className="font-bold text-text-primary">Key Drivers</h3>
                </div>
                <ul className="space-y-2 text-sm text-text-secondary">
                  {intelligenceData?.insight?.key_drivers?.map((driver: string, index: number) => (
                    <li key={index} className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-bullish"></span>
                      {driver}
                    </li>
                  )) || (
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-bullish"></span>
                      Loading drivers...
                    </li>
                  )}
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass rounded-2xl p-6 border-l-4 border-l-bearish"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-bearish/20 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-bearish" />
                  </div>
                  <h3 className="font-bold text-text-primary">Key Risks</h3>
                </div>
                <ul className="space-y-2 text-sm text-text-secondary">
                  {intelligenceData?.insight?.key_risks?.map((risk: string, index: number) => (
                    <li key={index} className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-bearish"></span>
                      {risk}
                    </li>
                  )) || (
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-bearish"></span>
                      Loading risks...
                    </li>
                  )}
                </ul>
              </motion.div>
            </div>

            {/* Strategic Consideration */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6 neon-glow"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-accent/20 rounded-lg">
                  <Sparkles className="w-5 h-5 text-accent" />
                </div>
                <h3 className="font-bold gradient-text">Strategic Consideration</h3>
              </div>
              <p className="text-text-secondary mb-4 leading-relaxed">
                {intelligenceData?.insight?.strategic_consideration || 'Loading strategic consideration...'}
              </p>

              {/* Score Legend */}
              <div className="border-t border-white/10 pt-4 mt-4">
                <h4 className="text-sm font-semibold text-text-primary mb-3">Score Legend</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-text-secondary">75-100: Strong Buy - Increase exposure</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                    <span className="text-text-secondary">60-75: Buy - Selective exposure</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-text-secondary">45-60: Hold - Neutral stance</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                    <span className="text-text-secondary">30-45: Sell - Reduce exposure</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="text-text-secondary">0-30: Strong Sell - Avoid</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Bottom Panel - Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 glass rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold gradient-text flex items-center gap-2">
              <Newspaper className="w-6 h-6" />
              Live Intelligence Feed
            </h3>
            <div className="flex items-center gap-2 text-xs text-text-secondary">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              Live
            </div>
          </div>
          <div className="space-y-3">
            {intelligenceFeed.length > 0 ? (
              intelligenceFeed.map((alert, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4 p-3 rounded-lg bg-panel-bg/50 hover:bg-panel-bg transition-colors cursor-pointer group"
                >
                  <span className="text-sm text-text-secondary w-16 font-mono">{alert.time}</span>
                  <span className={`w-2 h-2 rounded-full ${
                    alert.type === 'bullish' ? 'bg-green-500' :
                    alert.type === 'bearish' ? 'bg-red-500' :
                    'bg-yellow-500'
                  }`}></span>
                  <span className="text-text-primary flex-1 group-hover:text-accent transition-colors">{alert.message}</span>
                  <ChevronRight className="w-4 h-4 text-text-secondary group-hover:text-accent transition-colors" />
                </motion.div>
              ))
            ) : (
              <div className="text-text-secondary text-sm p-3 text-center">
                No active intelligence alerts at this time
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
