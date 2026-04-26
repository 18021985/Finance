'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, Shield, Target, PieChart, AlertCircle, Clock, DollarSign, BarChart3, ChevronRight } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

interface Strategy {
  name: string
  type: string
  description: string
  riskLevel: 'Low' | 'Medium' | 'High'
  timeHorizon: string
  expectedReturn: string
  volatility: string
  maxDrawdown: string
  data: any
  icon: any
  assets: { name: string; allocation: number; color: string }[]
}

const STRATEGY_DATA: Omit<Strategy, 'data'>[] = [
  {
    name: '60/40 Portfolio',
    type: 'Balanced',
    description: 'Classic balanced portfolio with 60% equities and 40% fixed income. Provides steady growth with moderate risk.',
    riskLevel: 'Medium',
    timeHorizon: '5-10 years',
    expectedReturn: '7-9%',
    volatility: '10-12%',
    maxDrawdown: '-15 to -20%',
    icon: PieChart,
    assets: [
      { name: 'US Equities', allocation: 40, color: '#3B82F6' },
      { name: 'Intl Equities', allocation: 20, color: '#10B981' },
      { name: 'Bonds', allocation: 30, color: '#F59E0B' },
      { name: 'Cash', allocation: 10, color: '#6B7280' },
    ],
  },
  {
    name: 'Risk Parity',
    type: 'Risk-Adjusted',
    description: 'Balances risk contribution across asset classes. Uses leverage to achieve equal risk exposure from equities and bonds.',
    riskLevel: 'Medium',
    timeHorizon: '3-7 years',
    expectedReturn: '6-8%',
    volatility: '8-10%',
    maxDrawdown: '-12 to -18%',
    icon: Shield,
    assets: [
      { name: 'US Equities', allocation: 25, color: '#3B82F6' },
      { name: 'Intl Equities', allocation: 15, color: '#10B981' },
      { name: 'Bonds', allocation: 40, color: '#F59E0B' },
      { name: 'Commodities', allocation: 10, color: '#EF4444' },
      { name: 'Real Estate', allocation: 10, color: '#8B5CF6' },
    ],
  },
  {
    name: 'All Weather',
    type: 'Defensive',
    description: 'Ray Dalio\'s all-weather portfolio designed to perform well across economic environments. Highly diversified.',
    riskLevel: 'Low',
    timeHorizon: '10+ years',
    expectedReturn: '5-7%',
    volatility: '6-8%',
    maxDrawdown: '-8 to -12%',
    icon: Target,
    assets: [
      { name: 'US Stocks', allocation: 30, color: '#3B82F6' },
      { name: 'Long-term Bonds', allocation: 40, color: '#F59E0B' },
      { name: 'Intermediate Bonds', allocation: 15, color: '#10B981' },
      { name: 'Gold', allocation: 7.5, color: '#FCD34D' },
      { name: 'Commodities', allocation: 7.5, color: '#EF4444' },
    ],
  },
]

export default function StrategiesPage() {
  const router = useRouter()
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      // Fetch allocation strategies to get real data
      const strategies_60_40 = await intelligenceApi.getAllocationByStrategy('60_40')
      const strategies_risk_parity = await intelligenceApi.getAllocationByStrategy('risk_parity')
      const strategies_all_weather = await intelligenceApi.getAllocationByStrategy('all_weather')
      
      const dataMap = {
        '60/40 Portfolio': strategies_60_40,
        'Risk Parity': strategies_risk_parity,
        'All Weather': strategies_all_weather,
      }
      
      setStrategies(STRATEGY_DATA.map(s => ({ ...s, data: dataMap[s.name as keyof typeof dataMap] || {} })))
    } catch (error) {
      console.error('Error fetching strategies:', error)
      // Use default data if API fails
      setStrategies(STRATEGY_DATA.map(s => ({ ...s, data: {} })))
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Low': return 'text-green-400 bg-green-400/20'
      case 'Medium': return 'text-yellow-400 bg-yellow-400/20'
      case 'High': return 'text-red-400 bg-red-400/20'
      default: return 'text-gray-400 bg-gray-400/20'
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
            <h1 className="text-4xl font-bold gradient-text mb-2">Investment Strategies</h1>
            <p className="text-text-secondary">Portfolio allocation strategies for different risk profiles and goals</p>
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center text-text-secondary py-20">Loading strategies...</div>
        ) : (
          <>
            {/* Strategy Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {strategies.map((strategy, index) => (
                <motion.div
                  key={strategy.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass rounded-2xl p-6 hover:border-accent/50 transition-all cursor-pointer group"
                  onClick={() => setSelectedStrategy(strategy)}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-3 bg-accent/20 rounded-lg group-hover:bg-accent/30 transition-colors">
                      <strategy.icon className="w-6 h-6 text-accent" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold">{strategy.name}</h3>
                      <p className="text-sm text-text-secondary">{strategy.type}</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-text-secondary group-hover:text-accent transition-colors" />
                  </div>
                  
                  <p className="text-sm text-text-secondary mb-4 line-clamp-2">{strategy.description}</p>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRiskColor(strategy.riskLevel)}`}>
                      {strategy.riskLevel} Risk
                    </span>
                    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-blue-400/20 text-blue-400">
                      {strategy.timeHorizon}
                    </span>
                  </div>

                  {/* Mini Allocation Chart */}
                  <div className="flex items-end gap-1 h-8 mb-4">
                    {strategy.assets.slice(0, 4).map((asset, i) => (
                      <div
                        key={asset.name}
                        className="flex-1 rounded-t-sm transition-all group-hover:opacity-80"
                        style={{
                          height: `${asset.allocation}%`,
                          backgroundColor: asset.color,
                        }}
                        title={`${asset.name}: ${asset.allocation}%`}
                      />
                    ))}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center gap-1 text-text-secondary">
                      <TrendingUp className="w-3 h-3" />
                      <span>Exp: {strategy.expectedReturn}</span>
                    </div>
                    <div className="flex items-center gap-1 text-text-secondary">
                      <AlertCircle className="w-3 h-3" />
                      <span>Vol: {strategy.volatility}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Strategy Comparison Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-2xl p-6"
            >
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-accent" />
                Strategy Comparison
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Strategy</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Risk Level</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Time Horizon</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Expected Return</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Volatility</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Max Drawdown</th>
                    </tr>
                  </thead>
                  <tbody>
                    {strategies.map((strategy) => (
                      <tr key={strategy.name} className="border-b border-border/50 hover:bg-panel-bg/50 transition-colors">
                        <td className="py-3 px-4 font-semibold">{strategy.name}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRiskColor(strategy.riskLevel)}`}>
                            {strategy.riskLevel}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-text-secondary">{strategy.timeHorizon}</td>
                        <td className="py-3 px-4 text-green-400">{strategy.expectedReturn}</td>
                        <td className="py-3 px-4 text-text-secondary">{strategy.volatility}</td>
                        <td className="py-3 px-4 text-red-400">{strategy.maxDrawdown}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>

            {/* Strategy Detail Modal */}
            {selectedStrategy && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                onClick={() => setSelectedStrategy(null)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="glass rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-accent/20 rounded-lg">
                        <selectedStrategy.icon className="w-6 h-6 text-accent" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold">{selectedStrategy.name}</h2>
                        <p className="text-text-secondary">{selectedStrategy.type}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedStrategy(null)}
                      className="p-2 hover:bg-panel-bg rounded-lg transition-colors"
                    >
                      <ArrowLeft className="w-6 h-6" />
                    </button>
                  </div>

                  <p className="text-text-secondary mb-6">{selectedStrategy.description}</p>

                  {/* Key Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="glass rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className="w-4 h-4 text-accent" />
                        <span className="text-sm text-text-secondary">Risk Level</span>
                      </div>
                      <span className={`text-lg font-bold ${getRiskColor(selectedStrategy.riskLevel).split(' ')[0]}`}>
                        {selectedStrategy.riskLevel}
                      </span>
                    </div>
                    <div className="glass rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-accent" />
                        <span className="text-sm text-text-secondary">Time Horizon</span>
                      </div>
                      <span className="text-lg font-bold">{selectedStrategy.timeHorizon}</span>
                    </div>
                    <div className="glass rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-accent" />
                        <span className="text-sm text-text-secondary">Expected Return</span>
                      </div>
                      <span className="text-lg font-bold text-green-400">{selectedStrategy.expectedReturn}</span>
                    </div>
                    <div className="glass rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-accent" />
                        <span className="text-sm text-text-secondary">Volatility</span>
                      </div>
                      <span className="text-lg font-bold">{selectedStrategy.volatility}</span>
                    </div>
                  </div>

                  {/* Asset Allocation */}
                  <div className="mb-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-accent" />
                      Asset Allocation
                    </h3>
                    <div className="space-y-3">
                      {selectedStrategy.assets.map((asset) => (
                        <div key={asset.name}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="font-semibold">{asset.name}</span>
                            <span className="text-text-secondary">{asset.allocation}%</span>
                          </div>
                          <div className="h-2 bg-panel-bg rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${asset.allocation}%`,
                                backgroundColor: asset.color,
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Button */}
                  <button
                    className="w-full py-3 bg-accent hover:bg-accent/80 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2"
                    onClick={() => {
                      router.push('/recommendations')
                      setSelectedStrategy(null)
                    }}
                  >
                    <DollarSign className="w-5 h-5" />
                    Get Recommendations for This Strategy
                  </button>
                </motion.div>
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
