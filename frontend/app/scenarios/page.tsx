'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Target, TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle, Clock, BarChart3 } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function ScenariosPage() {
  const router = useRouter()
  const [scenarios, setScenarios] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchScenarios()
  }, [])

  const fetchScenarios = async () => {
    try {
      const data = await intelligenceApi.getMacroScenarios()
      setScenarios(data)
    } catch (error) {
      console.error('Error fetching scenarios:', error)
    } finally {
      setLoading(false)
    }
  }

  const getScenarioIcon = (scenario: any) => {
    const equityImplication = scenario.asset_implications?.equities || scenario.implications?.equities
    if (equityImplication?.toLowerCase().includes('bullish')) return TrendingUp
    if (equityImplication?.toLowerCase().includes('bearish')) return TrendingDown
    return Minus
  }

  const getScenarioColor = (scenario: any) => {
    const equityImplication = scenario.asset_implications?.equities || scenario.implications?.equities
    if (equityImplication?.toLowerCase().includes('bullish')) return 'text-green-400 bg-green-400/20'
    if (equityImplication?.toLowerCase().includes('bearish')) return 'text-red-400 bg-red-400/20'
    return 'text-yellow-400 bg-yellow-400/20'
  }

  const getScenarioBorderColor = (scenario: any) => {
    const equityImplication = scenario.asset_implications?.equities || scenario.implications?.equities
    if (equityImplication?.toLowerCase().includes('bullish')) return 'border-green-500/30'
    if (equityImplication?.toLowerCase().includes('bearish')) return 'border-red-500/30'
    return 'border-yellow-500/30'
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
            <h1 className="text-4xl font-bold gradient-text mb-2">Market Scenarios</h1>
            <p className="text-text-secondary">Forward-looking macro scenarios with probabilities and implications</p>
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center text-text-secondary py-20">Loading scenarios...</div>
        ) : (
          <>
            {/* Summary Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid md:grid-cols-3 gap-6 mb-8"
            >
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <BarChart3 className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Total Scenarios</span>
                </div>
                <div className="text-3xl font-bold">{scenarios.length}</div>
              </div>
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="w-6 h-6 text-green-400" />
                  <span className="text-text-secondary">Bullish Probability</span>
                </div>
                <div className="text-3xl font-bold text-green-400">
                  {scenarios.filter(s => {
                    const equityImplication = s.asset_implications?.equities || s.implications?.equities
                    return equityImplication?.toLowerCase().includes('bullish')
                  }).reduce((sum, s) => sum + (s.probability || 0), 0).toFixed(0)}%
                </div>
              </div>
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingDown className="w-6 h-6 text-red-400" />
                  <span className="text-text-secondary">Bearish Probability</span>
                </div>
                <div className="text-3xl font-bold text-red-400">
                  {scenarios.filter(s => {
                    const equityImplication = s.asset_implications?.equities || s.implications?.equities
                    return equityImplication?.toLowerCase().includes('bearish')
                  }).reduce((sum, s) => sum + (s.probability || 0), 0).toFixed(0)}%
                </div>
              </div>
            </motion.div>

            {/* Scenario Cards */}
            <div className="grid md:grid-cols-2 gap-6">
              {scenarios.map((scenario, index) => {
                const Icon = getScenarioIcon(scenario)
                const colorClass = getScenarioColor(scenario)
                const borderClass = getScenarioBorderColor(scenario)
                return (
                  <motion.div
                    key={scenario.name}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className={`glass rounded-2xl p-6 border-2 ${borderClass} hover:border-accent/50 transition-all cursor-pointer`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-lg ${colorClass}`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold">{scenario.name}</h3>
                          <div className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
                            {(scenario.probability * 100).toFixed(0)}% probability
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-text-secondary mb-4">{scenario.description}</p>
                    
                    {/* Timeline */}
                    <div className="flex items-center gap-2 mb-4 text-sm text-text-secondary">
                      <Clock className="w-4 h-4" />
                      <span>Expected timeframe: {scenario.timeframe || '6-12 months'}</span>
                    </div>

                    {/* Implications */}
                    <div className="space-y-2">
                      <div className="text-sm font-semibold text-text-primary flex items-center gap-2">
                        <Target className="w-4 h-4 text-accent" />
                        Key Implications
                      </div>
                      {scenario.implications && Object.entries(scenario.implications).slice(0, 4).map(([key, value]: [string, any]) => (
                        <div key={key} className="flex items-center justify-between p-2 bg-panel-bg rounded text-sm">
                          <span className="text-text-secondary capitalize">{key.replace('_', ' ')}</span>
                          <span className="font-semibold">
                            {typeof value === 'object' ? JSON.stringify(value) : value}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Action Items */}
                    {scenario.action_items && (
                      <div className="mt-4 pt-4 border-t border-border">
                        <div className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Recommended Actions
                        </div>
                        <ul className="space-y-1">
                          {scenario.action_items.slice(0, 3).map((action: string, i: number) => (
                            <li key={i} className="text-sm text-text-secondary flex items-start gap-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-accent mt-1.5"></span>
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>

            {/* Scenario Comparison Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-8 glass rounded-2xl p-6"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-accent" />
                Scenario Comparison
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Scenario</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Probability</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Market Impact</th>
                      <th className="text-left py-3 px-4 text-text-secondary font-semibold">Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scenarios.map((scenario) => {
                      const colorClass = getScenarioColor(scenario)
                      return (
                        <tr key={scenario.name} className="border-b border-border/50 hover:bg-panel-bg/50 transition-colors">
                          <td className="py-3 px-4 font-semibold">{scenario.name}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
                              {(scenario.probability * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="py-3 px-4 text-text-secondary">
                            {scenario.asset_implications?.equities || scenario.implications?.equities || 'Moderate'}
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-accent font-semibold">
                              {scenario.asset_implications?.strategy || scenario.implications?.recommended_action || 'Monitor'}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </>
        )}
      </div>
    </div>
  )
}
