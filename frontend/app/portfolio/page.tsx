'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Briefcase, TrendingUp, TrendingDown, DollarSign, Plus, Trash2, Brain, Clock } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function PortfolioPage() {
  const router = useRouter()
  const [portfolioData, setPortfolioData] = useState<any>(null)
  const [userHoldings, setUserHoldings] = useState<any[]>([])
  const [portfolioStrategy, setPortfolioStrategy] = useState<any>(null)
  const [availableCompanies, setAvailableCompanies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newHolding, setNewHolding] = useState({ symbol: '', shares: 0, average_cost: 0, sector: '', market: 'US' })

  useEffect(() => {
    fetchPortfolioData()
    fetchUserHoldings()
    fetchPortfolioStrategy()
    fetchAvailableCompanies()
  }, [])

  const fetchPortfolioData = async () => {
    try {
      const data = await intelligenceApi.getPortfolioData()
      setPortfolioData(data)
    } catch (error) {
      console.error('Error fetching portfolio data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserHoldings = async () => {
    try {
      const holdings = await intelligenceApi.getUserHoldings()
      setUserHoldings(holdings)
    } catch (error) {
      console.error('Error fetching user holdings:', error)
    }
  }

  const fetchPortfolioStrategy = async () => {
    try {
      const strategy = await intelligenceApi.getPortfolioStrategy()
      setPortfolioStrategy(strategy)
    } catch (error) {
      console.error('Error fetching portfolio strategy:', error)
    }
  }

  const fetchAvailableCompanies = async () => {
    try {
      const companies = await intelligenceApi.getAvailableCompanies()
      setAvailableCompanies(companies)
    } catch (error) {
      console.error('Error fetching available companies:', error)
    }
  }

  const handleAddHolding = async () => {
    try {
      await intelligenceApi.addHolding(newHolding)
      setShowAddModal(false)
      setNewHolding({ symbol: '', shares: 0, average_cost: 0, sector: '', market: 'US' })
      fetchUserHoldings()
      fetchPortfolioStrategy()
    } catch (error) {
      console.error('Error adding holding:', error)
    }
  }

  const handleDeleteHolding = async (holdingId: string) => {
    try {
      await intelligenceApi.deleteHolding(holdingId)
      fetchUserHoldings()
      fetchPortfolioStrategy()
    } catch (error) {
      console.error('Error deleting holding:', error)
    }
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center justify-between"
        >
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-panel-bg rounded-lg transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">My Portfolio</h1>
              <p className="text-text-secondary">Manage your holdings and get personalized strategies</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors cursor-pointer text-white"
          >
            <Plus className="w-5 h-5" />
            Add Holding
          </button>
        </motion.div>

        {loading ? (
          <div className="text-center text-text-secondary">Loading portfolio data...</div>
        ) : (
          <div className="space-y-6">
            {/* Portfolio Summary */}
            <div className="grid md:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <DollarSign className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Total Value</span>
                </div>
                <div className="text-3xl font-bold">${portfolioData?.totalValue?.toLocaleString() || 0}</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="w-6 h-6 text-bullish" />
                  <span className="text-text-secondary">Daily Change</span>
                </div>
                <div className={`text-3xl font-bold ${portfolioData?.dailyChange >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                  ${portfolioData?.dailyChange?.toLocaleString() || 0}
                </div>
                <div className={`text-sm ${portfolioData?.dailyChange >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                  {portfolioData?.dailyChangePercent >= 0 ? '+' : ''}{portfolioData?.dailyChangePercent || 0}%
                </div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-2">
                  <Briefcase className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Holdings</span>
                </div>
                <div className="text-3xl font-bold">{userHoldings.length}</div>
              </motion.div>
            </div>

            {/* My Holdings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text">My Holdings</h3>
              <div className="space-y-3">
                {userHoldings.length > 0 ? (
                  userHoldings.map((holding: any, index: number) => (
                    <div
                      key={holding.id || index}
                      className="flex items-center justify-between p-4 bg-panel-bg rounded-lg hover:bg-panel-bg/80 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center font-bold text-accent">
                          {holding.symbol[0]}
                        </div>
                        <div>
                          <div className="font-bold">{holding.symbol}</div>
                          <div className="text-sm text-text-secondary">{holding.shares} shares @ ${holding.average_cost}</div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteHolding(holding.id)}
                        className="p-2 hover:bg-red-500/20 rounded-lg transition-colors cursor-pointer text-red-500"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-text-secondary py-8">
                    No holdings yet. Click "Add Holding" to get started.
                  </div>
                )}
              </div>
            </motion.div>

            {/* Personalized Strategy */}
            {portfolioStrategy && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Short-term Strategy */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <Clock className="w-6 h-6 text-accent" />
                    <h3 className="text-xl font-bold gradient-text">Short-term Strategy</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-text-secondary">Market Sentiment:</span>
                      <span className={`font-bold ${portfolioStrategy.market_sentiment === 'bullish' ? 'text-bullish' : portfolioStrategy.market_sentiment === 'bearish' ? 'text-bearish' : 'text-yellow-500'}`}>
                        {portfolioStrategy.market_sentiment}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-text-secondary">Risk Level:</span>
                      <span className="font-bold">{portfolioStrategy.risk_level}</span>
                    </div>
                    {portfolioStrategy.short_term_strategy?.map((strategy: any, index: number) => (
                      <div key={index} className="p-3 bg-panel-bg rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold">{strategy.symbol}</span>
                          <span className="text-sm text-text-secondary">{strategy.shares} shares</span>
                        </div>
                        <div className="text-sm font-semibold text-accent mb-1">{strategy.action}</div>
                        <div className="text-xs text-text-secondary">{strategy.reasoning}</div>
                        <div className="text-xs mt-2 text-text-secondary">Confidence: {(strategy.confidence * 100).toFixed(0)}%</div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Long-term Strategy */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <Brain className="w-6 h-6 text-accent" />
                    <h3 className="text-xl font-bold gradient-text">Long-term Strategy</h3>
                  </div>
                  <div className="space-y-3">
                    {portfolioStrategy.long_term_strategy?.map((strategy: any, index: number) => (
                      <div key={index} className="p-3 bg-panel-bg rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold">{strategy.symbol}</span>
                          <span className="text-sm text-text-secondary">{strategy.time_horizon}</span>
                        </div>
                        <div className="text-sm font-semibold text-accent mb-1">{strategy.action}</div>
                        <div className="text-xs text-text-secondary">{strategy.reasoning}</div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>
            )}
          </div>
        )}

        {/* Add Holding Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass rounded-2xl p-6 w-full max-w-md"
            >
              <h3 className="text-xl font-bold mb-4 gradient-text">Add Holding</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Symbol</label>
                  <select
                    value={newHolding.symbol}
                    onChange={(e) => {
                      const selectedCompany = availableCompanies.find(c => c.symbol === e.target.value)
                      setNewHolding({
                        ...newHolding,
                        symbol: e.target.value,
                        sector: selectedCompany?.sector || '',
                        market: selectedCompany?.market || 'US'
                      })
                    }}
                    className="w-full p-2 bg-panel-bg rounded-lg text-text-primary border border-white/10 focus:border-accent outline-none"
                  >
                    <option value="">Select a company...</option>
                    {availableCompanies.map((company) => (
                      <option key={company.symbol} value={company.symbol}>
                        {company.symbol} - {company.sector} ({company.market})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Shares</label>
                  <input
                    type="number"
                    value={newHolding.shares}
                    onChange={(e) => setNewHolding({ ...newHolding, shares: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 bg-panel-bg rounded-lg text-text-primary border border-white/10 focus:border-accent outline-none"
                    placeholder="100"
                  />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Average Cost</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newHolding.average_cost}
                    onChange={(e) => setNewHolding({ ...newHolding, average_cost: parseFloat(e.target.value) || 0 })}
                    className="w-full p-2 bg-panel-bg rounded-lg text-text-primary border border-white/10 focus:border-accent outline-none"
                    placeholder="150.00"
                  />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Sector</label>
                  <input
                    type="text"
                    value={newHolding.sector}
                    readOnly
                    className="w-full p-2 bg-panel-bg/50 rounded-lg text-text-secondary border border-white/10 outline-none"
                    placeholder="Auto-populated"
                  />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Market</label>
                  <input
                    type="text"
                    value={newHolding.market}
                    readOnly
                    className="w-full p-2 bg-panel-bg/50 rounded-lg text-text-secondary border border-white/10 outline-none"
                    placeholder="Auto-populated"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 p-2 bg-panel-bg hover:bg-panel-bg/80 rounded-lg transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddHolding}
                    className="flex-1 p-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors cursor-pointer text-white"
                  >
                    Add
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  )
}
