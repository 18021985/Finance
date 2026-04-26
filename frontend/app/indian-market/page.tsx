'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, TrendingDown, Globe, Building2, BarChart3, DollarSign, Activity, Sparkles } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'

export default function IndianMarketPage() {
  const router = useRouter()
  const [marketData, setMarketData] = useState<any>(null)
  const [selectedStock, setSelectedStock] = useState('RELIANCE.NS')
  const [stockData, setStockData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMarketData()
  }, [])

  useEffect(() => {
    if (selectedStock) {
      fetchStockData(selectedStock)
    }
  }, [selectedStock])

  const fetchMarketData = async () => {
    try {
      const data = await intelligenceApi.getIndianMarket()
      setMarketData(data)
    } catch (error) {
      console.error('Error fetching Indian market data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStockData = async (symbol: string) => {
    try {
      const data = await intelligenceApi.analyzeIndianStock(symbol)
      setStockData(data)
    } catch (error) {
      console.error('Error fetching stock data:', error)
    }
  }

  const indianStocks = [
    { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy' },
    { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'IT' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', sector: 'Banking' },
    { symbol: 'INFY.NS', name: 'Infosys', sector: 'IT' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank', sector: 'Banking' },
    { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever', sector: 'FMCG' },
    { symbol: 'ITC.NS', name: 'ITC Limited', sector: 'FMCG' },
    { symbol: 'SBIN.NS', name: 'State Bank of India', sector: 'Banking' },
    { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel', sector: 'Telecom' },
    { symbol: 'LT.NS', name: 'Larsen & Toubro', sector: 'Infrastructure' },
  ]

  const getSectorColor = (sector: string) => {
    const colors: { [key: string]: string } = {
      'IT': 'bg-blue-500/20 text-blue-400',
      'Banking': 'bg-green-500/20 text-green-400',
      'Energy': 'bg-orange-500/20 text-orange-400',
      'FMCG': 'bg-purple-500/20 text-purple-400',
      'Telecom': 'bg-pink-500/20 text-pink-400',
      'Infrastructure': 'bg-yellow-500/20 text-yellow-400',
    }
    return colors[sector] || 'bg-gray-500/20 text-gray-400'
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
            <h1 className="text-4xl font-bold gradient-text mb-2">Indian Market (NSE/BSE)</h1>
            <p className="text-text-secondary">Real-time analysis of Indian stock market indices and stocks</p>
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center text-text-secondary py-20">Loading Indian market data...</div>
        ) : marketData ? (
          <div className="space-y-6">
            {/* Market Indices */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Market Indices</h3>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {marketData.indices && Object.entries(marketData.indices).map(([name, data]: [string, any], index) => (
                  <motion.div
                    key={name}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 bg-panel-bg rounded-lg hover:bg-panel-bg/80 transition-colors cursor-pointer border border-transparent hover:border-accent/30"
                  >
                    <div className="text-sm text-text-secondary mb-1">{name}</div>
                    <div className="text-2xl font-bold">₹{data.current?.toFixed(2) || 'N/A'}</div>
                    <div className={`flex items-center gap-1 text-sm ${data.change >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                      {data.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      <span className="font-semibold">{data.change >= 0 ? '+' : ''}{data.change?.toFixed(2)}%</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Market Overview Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="grid md:grid-cols-3 gap-6"
            >
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <DollarSign className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Market Cap</span>
                </div>
                <div className="text-3xl font-bold">
                  {marketData.market_cap ? `₹${(marketData.market_cap / 100000000000).toFixed(2)}T` : 'N/A'}
                </div>
              </div>
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <Activity className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Volume</span>
                </div>
                <div className="text-3xl font-bold">
                  {marketData.volume ? `${(marketData.volume / 10000000).toFixed(2)}Cr` : 'N/A'}
                </div>
              </div>
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <BarChart3 className="w-6 h-6 text-accent" />
                  <span className="text-text-secondary">Volatility Index</span>
                </div>
                <div className="text-3xl font-bold">
                  {marketData.vix?.toFixed(2) || 'N/A'}
                </div>
              </div>
            </motion.div>

            {/* Stock Selector */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Building2 className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Key Stocks</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
                {indianStocks.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => setSelectedStock(stock.symbol)}
                    className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                      selectedStock === stock.symbol ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                    }`}
                  >
                    {stock.name}
                  </button>
                ))}
              </div>

              {stockData && (
                <div className="p-4 bg-panel-bg rounded-lg border border-accent/20">
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-lg font-bold">{selectedStock}</div>
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getSectorColor(indianStocks.find(s => s.symbol === selectedStock)?.sector || '')}`}>
                      {indianStocks.find(s => s.symbol === selectedStock)?.sector || 'N/A'}
                    </span>
                  </div>
                  <div className="grid md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <div className="text-sm text-text-secondary mb-1">Current Price</div>
                      <div className="text-xl font-bold">
                        ₹{typeof stockData.current_price === 'number' ? stockData.current_price.toFixed(2) : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-text-secondary mb-1">1M Change</div>
                      <div className={`text-xl font-bold ${Number(stockData.performance?.['1m'] ?? 0) >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                        {Number(stockData.performance?.['1m'] ?? 0) >= 0 ? '+' : ''}{typeof stockData.performance?.['1m'] === 'number' ? stockData.performance['1m'].toFixed(2) : 'N/A'}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-text-secondary mb-1">Market Cap</div>
                      <div className="text-xl font-bold">
                        {typeof stockData.valuation?.market_cap === 'number'
                          ? `₹${(stockData.valuation.market_cap / 10000000).toFixed(2)} Cr`
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-text-secondary mb-1">P/E Ratio</div>
                      <div className="text-xl font-bold">
                        {typeof stockData.valuation?.pe_ratio === 'number' ? stockData.valuation.pe_ratio.toFixed(2) : 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-3 bg-panel-bg/50 rounded-lg">
                      <div className="text-sm text-text-secondary mb-1">52W High/Low</div>
                      <div className="text-lg font-bold">
                        ₹{typeof stockData.technical?.recent_high === 'number' ? stockData.technical.recent_high.toFixed(2) : 'N/A'}
                        {' / '}
                        ₹{typeof stockData.technical?.recent_low === 'number' ? stockData.technical.recent_low.toFixed(2) : 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-panel-bg/50 rounded-lg">
                      <div className="text-sm text-text-secondary mb-1">Volume</div>
                      <div className="text-lg font-bold">
                        {typeof stockData.volume === 'number' ? `${(stockData.volume / 1000000).toFixed(2)}M` : 
                         typeof marketData.volume === 'number' ? `${(marketData.volume / 1000000).toFixed(2)}M` : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Sector Performance */}
            {marketData.sectors && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Sparkles className="w-6 h-6 text-accent" />
                  <h3 className="text-xl font-bold gradient-text">Sector Performance</h3>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(marketData.sectors)
                    .sort((a: any, b: any) => Number(b[1].change) - Number(a[1].change))
                    .map(([name, data]: [string, any], index) => (
                    <motion.div
                      key={name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="p-4 bg-panel-bg rounded-lg flex items-center justify-between hover:bg-panel-bg/80 transition-colors cursor-pointer"
                    >
                      <div>
                        <div className="font-semibold">{name}</div>
                        <div className="text-sm text-text-secondary">NSE</div>
                      </div>
                      <div className={`flex items-center gap-2 ${data.change >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                        {data.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        <span className="font-bold">{data.change?.toFixed(2)}%</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}
