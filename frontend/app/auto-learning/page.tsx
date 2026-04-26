'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Zap, Brain, Activity, TrendingUp } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function AutoLearningPage() {
  const router = useRouter()
  const [learningData, setLearningData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLearningData()
  }, [])

  const fetchLearningData = async () => {
    try {
      const report = await intelligenceApi.getAutoLearningReport(200)
      const overall = report?.overall_metrics || report?.last_metrics || {}
      const models = report?.model_performance || {}
      const counts = report?.counts || {}
      const predictionsLogged = Number(counts?.predictions_logged ?? 0)
      const outcomesLogged = Number(counts?.outcomes_logged ?? 0)
      const metrics = Object.entries(models).map(([name, v]: any) => ({
        name,
        accuracy: Number(v?.accuracy ?? 0),
        samples: Number(v?.total_predictions ?? 0),
      }))

      setLearningData({
        modelsTrained: metrics.length,
        accuracy: outcomesLogged >= 2 ? Number(overall.accuracy ?? 0) : null,
        samplesProcessed: outcomesLogged,
        predictionsLogged,
        lastUpdate: new Date().toLocaleDateString(),
        metrics: metrics.length ? metrics : [{ name: 'Baseline', accuracy: outcomesLogged >= 2 ? Number(overall.accuracy ?? 0) : 0, samples: outcomesLogged }],
        risk: {
          sharpe: Number(overall.sharpe_ratio ?? 0),
          maxDrawdown: Number(overall.max_drawdown ?? 0),
          winRate: Number(overall.win_rate ?? 0),
        },
      })
    } catch (error) {
      console.error('Error fetching learning data:', error)
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
            <h1 className="text-4xl font-bold gradient-text mb-2">Auto-Learning</h1>
            <p className="text-text-secondary">Real-time machine learning model training and updates</p>
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center text-text-secondary">Loading learning data...</div>
        ) : learningData ? (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid md:grid-cols-4 gap-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <Brain className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Models Trained</span>
                </div>
                <div className="text-3xl font-bold">{learningData.modelsTrained}</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="w-6 h-6 text-bullish" />
                  <span className="text-text-secondary">Accuracy</span>
                </div>
                <div className="text-3xl font-bold">
                  {typeof learningData.accuracy === 'number' ? `${(learningData.accuracy * 100).toFixed(0)}%` : '—'}
                </div>
                {typeof learningData.accuracy !== 'number' ? (
                  <div className="text-sm text-text-secondary mt-2">Waiting for outcomes</div>
                ) : null}
              </motion.div>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <Activity className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Samples Processed</span>
                </div>
                <div className="text-3xl font-bold">{learningData.samplesProcessed.toLocaleString()}</div>
                <div className="text-sm text-text-secondary mt-2">
                  {Number(learningData.predictionsLogged ?? 0).toLocaleString()} predictions logged
                </div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <Zap className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Last Update</span>
                </div>
                <div className="text-3xl font-bold">{learningData.lastUpdate}</div>
              </motion.div>
            </div>

            {/* Model Performance */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text">Model Performance</h3>
              <div className="space-y-4">
                {learningData.metrics.map((metric: any, index: number) => (
                  <div key={metric.name} className="p-4 bg-panel-bg rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-bold">{metric.name}</div>
                      <div className="text-bullish font-bold">{(metric.accuracy * 100).toFixed(0)}%</div>
                    </div>
                    <div className="w-full bg-panel-bg rounded-full h-2">
                      <div
                        className="bg-accent h-2 rounded-full transition-all"
                        style={{ width: `${metric.accuracy * 100}%` }}
                      />
                    </div>
                    <div className="text-sm text-text-secondary mt-2">
                      {metric.samples.toLocaleString()} samples processed
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Risk-adjusted KPIs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text">Risk-adjusted Performance</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-text-secondary text-sm">Sharpe (proxy)</div>
                  <div className="text-2xl font-bold">{learningData.risk?.sharpe?.toFixed?.(2) ?? '0.00'}</div>
                </div>
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-text-secondary text-sm">Max Drawdown</div>
                  <div className="text-2xl font-bold">{learningData.risk?.maxDrawdown?.toFixed?.(2) ?? '0.00'}</div>
                </div>
                <div className="p-4 bg-panel-bg rounded-lg">
                  <div className="text-text-secondary text-sm">Win Rate</div>
                  <div className="text-2xl font-bold">{((learningData.risk?.winRate ?? 0) * 100).toFixed(0)}%</div>
                </div>
              </div>
            </motion.div>

            {/* Learning Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text">Learning Status</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span>Online learning active</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span>Model validation running</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse" />
                  <span>Hyperparameter optimization pending</span>
                </div>
              </div>
            </motion.div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
