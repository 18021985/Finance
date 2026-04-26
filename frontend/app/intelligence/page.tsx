'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Brain, TrendingUp, AlertTriangle, Sparkles, BarChart3, Target, Zap, ChevronRight } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function IntelligencePage() {
  const router = useRouter()
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [intelligenceData, setIntelligenceData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchIntelligenceData(selectedSymbol)
  }, [selectedSymbol])

  const fetchIntelligenceData = async (symbol: string) => {
    try {
      setLoading(true)
      const data = await intelligenceApi.getCompositeScore(symbol)
      setIntelligenceData(data)
    } catch (error) {
      console.error('Error fetching intelligence data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-400'
    if (score >= 60) return 'text-blue-400'
    if (score >= 45) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBg = (score: number) => {
    if (score >= 75) return 'bg-green-400/20'
    if (score >= 60) return 'bg-blue-400/20'
    if (score >= 45) return 'bg-yellow-400/20'
    return 'bg-red-400/20'
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center gap-4"
        >
          <button
            onClick={() => router.push('/dashboard')}
            className="p-2 hover:bg-panel-bg rounded-lg transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">AI Intelligence</h1>
            <p className="text-text-secondary">Machine learning-powered market analysis with composite scoring</p>
          </div>
        </motion.div>

        {/* Symbol Selector */}
        <div className="mb-6 flex gap-2 flex-wrap">
          {['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'].map((symbol) => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-4 py-2 rounded-lg transition-colors cursor-pointer ${
                selectedSymbol === symbol ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center text-text-secondary py-20">Loading intelligence data...</div>
        ) : intelligenceData ? (
          <div className="space-y-6">
            {/* Composite Score Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Brain className="w-6 h-6 text-accent" />
                  <h3 className="text-xl font-bold gradient-text">Composite Intelligence Score</h3>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreBg(intelligenceData.composite_score?.total_score || 0)} ${getScoreColor(intelligenceData.composite_score?.total_score || 0)}`}>
                  {intelligenceData.composite_score?.total_score || 0}/100
                </span>
              </div>

              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <div className="w-40 h-40 rounded-full border-8 border-accent/20 flex items-center justify-center">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getScoreColor(intelligenceData.composite_score?.total_score || 0)}`}>
                        {intelligenceData.composite_score?.total_score || 0}
                      </div>
                      <div className="text-sm text-text-secondary">/ 100</div>
                    </div>
                  </div>
                  <div
                    className="absolute inset-0 rounded-full border-8 border-accent/40"
                    style={{
                      clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
                      transform: `rotate(${((intelligenceData.composite_score?.total_score || 0) / 100) * 360 - 90}deg)`,
                      transition: 'transform 1.5s ease-out'
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: 'Technical', value: intelligenceData.composite_score?.technical_score || 0, icon: BarChart3 },
                  { label: 'Momentum', value: intelligenceData.composite_score?.momentum_score || 0, icon: TrendingUp },
                  { label: 'Macro', value: intelligenceData.composite_score?.macro_score || 0, icon: Target },
                  { label: 'ML Probability', value: (intelligenceData.composite_score?.ml_probability || 0).toFixed(2), icon: Zap },
                ].map((item, index) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 bg-panel-bg rounded-lg"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <item.icon className="w-4 h-4 text-accent" />
                      <span className="text-sm text-text-secondary">{item.label}</span>
                    </div>
                    <div className="text-2xl font-bold">{item.value}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* ML Prediction */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">ML Prediction</h3>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-sm text-text-secondary mb-1">Direction</div>
                  <div className={`text-2xl font-bold capitalize ${
                    intelligenceData.ml_prediction?.direction === 'bullish' ? 'text-bullish' :
                    intelligenceData.ml_prediction?.direction === 'bearish' ? 'text-bearish' :
                    'text-yellow-500'
                  }`}>
                    {intelligenceData.ml_prediction?.direction || 'N/A'}
                  </div>
                </div>
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-sm text-text-secondary mb-1">Probability</div>
                  <div className="text-2xl font-bold">{(intelligenceData.composite_score?.ml_probability || 0).toFixed(2)}</div>
                </div>
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-sm text-text-secondary mb-1">Confidence</div>
                  <div className="text-2xl font-bold">{(intelligenceData.ml_prediction?.confidence || 0).toFixed(2)}</div>
                </div>
              </div>
            </motion.div>

            {/* Insight */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Strategic Insight</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Assessment</div>
                    <div className="text-lg">{intelligenceData.insight?.assessment || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Strategic Consideration</div>
                    <div className="text-lg">{intelligenceData.insight?.strategic_consideration || 'N/A'}</div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Key Drivers</div>
                    <ul className="list-disc list-inside space-y-1">
                      {intelligenceData.insight?.key_drivers?.map((driver: string, i: number) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-bullish"></span>
                          {driver}
                        </li>
                      )) || <li>N/A</li>}
                    </ul>
                  </div>
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Key Risks</div>
                    <ul className="list-disc list-inside space-y-1">
                      {intelligenceData.insight?.key_risks?.map((risk: string, i: number) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-bearish"></span>
                          {risk}
                        </li>
                      )) || <li>N/A</li>}
                    </ul>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
