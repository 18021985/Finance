'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, TrendingDown, Target, Lightbulb, PieChart, AlertCircle } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function RecommendationsPage() {
  const router = useRouter()
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [opportunities, setOpportunities] = useState<any[]>([])
  const [tips, setTips] = useState<string[]>([])
  const [allocation, setAllocation] = useState<any>(null)
  const [riskProfile, setRiskProfile] = useState('moderate')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [riskProfile])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      // Never fail-fast the whole page; render whatever succeeds.
      const results = await Promise.allSettled([
        intelligenceApi.getRecommendations(15),
        intelligenceApi.getOpportunities(),
        intelligenceApi.getTips(),
        intelligenceApi.getAllocation(riskProfile)
      ])

      const [recsR, oppsR, tipsR, allocR] = results

      if (recsR.status === 'fulfilled') setRecommendations(recsR.value || [])
      else console.error('Recommendations failed:', recsR.reason)

      if (oppsR.status === 'fulfilled') setOpportunities(oppsR.value || [])
      else console.error('Opportunities failed:', oppsR.reason)

      if (tipsR.status === 'fulfilled') setTips(tipsR.value || [])
      else console.error('Tips failed:', tipsR.reason)

      if (allocR.status === 'fulfilled') setAllocation(allocR.value || null)
      else console.error('Allocation failed:', allocR.reason)
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    } finally {
      setLoading(false)
    }
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
            <h1 className="text-4xl font-bold gradient-text mb-2">Investment Recommendations</h1>
            <p className="text-text-secondary">AI-powered investment strategies and opportunities</p>
          </div>
        </motion.div>

        {/* Risk Profile Selector */}
        <div className="mb-6 flex gap-2">
          {['conservative', 'moderate', 'aggressive'].map((profile) => (
            <button
              key={profile}
              onClick={() => setRiskProfile(profile)}
              className={`px-4 py-2 rounded-lg transition-colors cursor-pointer capitalize ${
                riskProfile === profile ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
              }`}
            >
              {profile}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center text-text-secondary">Loading recommendations...</div>
        ) : (
          <div className="space-y-6">
            {/* Investment Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Target className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Investment Recommendations</h3>
              </div>
              <div className="space-y-4">
                {recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-2 ${
                      rec.action === 'buy' ? 'border-green-500/30 bg-green-500/10' :
                      rec.action === 'sell' ? 'border-red-500/30 bg-red-500/10' :
                      'border-yellow-500/30 bg-yellow-500/10'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                          rec.action === 'buy' ? 'bg-green-500' :
                          rec.action === 'sell' ? 'bg-red-500' :
                          'bg-yellow-500'
                        } text-white`}>
                          {rec.action === 'buy' ? 'B' : rec.action === 'sell' ? 'S' : 'H'}
                        </div>
                        <div>
                          <div className="font-bold text-lg">{rec.symbol}</div>
                          <div className="text-sm text-text-secondary capitalize">{rec.time_horizon}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">${rec.entry_price?.toFixed(2)}</div>
                        <div className={`text-sm ${rec.action === 'buy' ? 'text-bullish' : 'text-bearish'}`}>
                          {(rec.confidence * 100).toFixed(0)}% confidence
                        </div>
                      </div>
                    </div>
                    <div className="grid md:grid-cols-3 gap-2 text-sm mb-2">
                      <div>
                        <span className="text-text-secondary">Target:</span> ${rec.target_price?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-text-secondary">Stop Loss:</span> ${rec.stop_loss?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-text-secondary">Expected Return:</span> {(rec.expected_return * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="text-sm text-text-secondary">
                      <ul className="list-disc list-inside space-y-1">
                        {rec.reasoning?.map((reason: string, i: number) => (
                          <li key={i}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Market Opportunities */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Lightbulb className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Market Opportunities</h3>
              </div>
              <div className="space-y-3">
                {opportunities.map((opp, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg ${
                      opp.priority === 'high' ? 'bg-green-500/10 border border-green-500/30' :
                      'bg-panel-bg'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-semibold">{opp.description}</div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        opp.priority === 'high' ? 'bg-green-500 text-white' :
                        'bg-yellow-500 text-white'
                      }`}>
                        {opp.priority}
                      </span>
                    </div>
                    <div className="text-sm text-text-secondary">{opp.action}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Portfolio Allocation */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <PieChart className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Recommended Portfolio Allocation</h3>
              </div>
              {allocation && (
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(allocation).map(([key, value]: [string, any]) => (
                    <div key={key} className="p-4 bg-panel-bg rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-text-secondary capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-bold">{(value * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-panel-bg rounded-full h-2">
                        <div
                          className="bg-accent h-2 rounded-full transition-all"
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            {/* Investment Tips */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Investment Tips & Best Practices</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-3">
                {tips.map((tip, index) => (
                  <div key={index} className="p-3 bg-panel-bg rounded-lg text-sm">
                    {tip}
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  )
}
