import axios from 'axios'

// Use Render backend in production, Render URL for local development
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  'https://finance-1ylw.onrender.com'

export interface CompositeScore {
  total_score: number
  technical_score: number
  momentum_score: number
  macro_score: number
  fundamental_score: number
  ml_probability: number
  ml_score?: number
  trend: string
  momentum: string
  macro_alignment: string
  fundamental_strength: string
  confidence: number
}

export interface Insight {
  assessment: string
  strategic_consideration: string
  key_drivers: string[]
  key_risks: string[]
}

export interface IntelligenceResponse {
  composite_score: CompositeScore
  insight: Insight
  ml_prediction: {
    direction: string
    confidence: number
  }
}

export interface MacroOverview {
  interest_rates: {
    fed: number
    ecb: number
    boe: number
    boj: number
  }
  inflation: {
    cpi: number
    ppi: number
  }
  yield_curve: {
    two_year: number
    ten_year: number
    spread: number
  }
  risk_sentiment: {
    vix: number
    interpretation: string
  }
  economic_cycle: {
    phase: string
    confidence: number
  }
}

export interface Scenario {
  name: string
  probability: number
  description: string
  implications: {
    equities: string
    bonds: string
    commodities: string
    crypto: string
  }
}

export interface AssetAnalysis {
  asset: string
  asset_class: string
  current_price: number
  technical: any
  volatility: number
  insight: string
  strategic_consideration: string
}

export interface ForecastResponse {
  symbol: string
  last_price: number
  horizon_days: number
  return_quantiles: { p10: number; p50: number; p90: number }
  price_quantiles: { p10: number; p50: number; p90: number }
  direction_up_prob: number
}

export interface NewsSummaryResponse {
  symbol: string
  count: number
  effective_sentiment_avg: number
  event_counts: Record<string, number>
  items: any[]
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s (increased to handle concurrent backend requests)
})

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    const base = config.baseURL || API_BASE_URL
    console.log(`API Request: ${config.method?.toUpperCase()} ${base}${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.config.url} - Status: ${response.status}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.message)
    if (error.response) {
      console.error('Response data:', error.response.data)
      console.error('Response status:', error.response.status)
    } else if (error.request) {
      console.error('No response received:', error.request)
    }
    return Promise.reject(error)
  }
)

export const intelligenceApi = {
  // Get composite intelligence score
  getCompositeScore: async (symbol: string): Promise<IntelligenceResponse> => {
    try {
      const response = await api.get(`/intelligence/${symbol}`, { timeout: 20000 })
      return response.data
    } catch (e: any) {
      const msg = String(e?.message || '').toLowerCase()
      if (msg.includes('network error') || msg.includes('timeout')) {
        const response = await api.get(`/intelligence/${symbol}`, { timeout: 20000 })
        return response.data
      }
      throw e
    }
  },

  // Get macro intelligence
  getMacroIntelligence: async (): Promise<MacroOverview> => {
    try {
      const response = await api.get('/macro', { timeout: 20000 })
      return response.data
    } catch (e: any) {
      const msg = String(e?.message || '').toLowerCase()
      if (msg.includes('network error') || msg.includes('timeout')) {
        const response = await api.get('/macro', { timeout: 20000 })
        return response.data
      }
      throw e
    }
  },

  // Get macro scenarios
  getMacroScenarios: async (): Promise<Scenario[]> => {
    const response = await api.get('/macro/scenarios')
    return response.data.scenarios
  },

  // Analyze multi-asset
  analyzeMultiAsset: async (symbol: string): Promise<AssetAnalysis> => {
    const response = await api.get(`/multi-asset/${symbol}`)
    return response.data
  },

  // Get asset scenarios
  getAssetScenarios: async (symbol: string): Promise<Scenario[]> => {
    const response = await api.get(`/scenarios/${symbol}`)
    return response.data.scenarios
  },

  // Get correlation matrix
  getCorrelationMatrix: async (assets: string[]): Promise<any> => {
    const response = await api.get('/correlation', { params: { assets: assets.join(',') } })
    return response.data
  },

  // Get asset allocation by strategy
  getAllocationByStrategy: async (strategy: string): Promise<any> => {
    const response = await api.get(`/allocation/strategy/${strategy}`)
    return response.data
  },

  // Compare allocation strategies
  compareAllocations: async (): Promise<any> => {
    const response = await api.get('/allocation/compare')
    return response.data
  },

  // Get risk sentiment
  getRiskSentiment: async (): Promise<any> => {
    const response = await api.get('/risk-sentiment')
    return response.data
  },

  // Get Indian market overview
  getIndianMarket: async (): Promise<any> => {
    const response = await api.get('/indian-market')
    return response.data
  },

  // Analyze Indian stock
  analyzeIndianStock: async (symbol: string): Promise<any> => {
    const response = await api.get(`/indian-market/${symbol}`, { params: { period: '3mo' } })
    return response.data
  },

  // Get historical data
  getHistoricalData: async (symbol: string, period: string = '1y'): Promise<any> => {
    const response = await api.get(`/historical/${symbol}`, { params: { period } })
    return response.data
  },

  // Forecast fan for chart overlay
  getForecast: async (symbol: string, horizonDays: number = 20): Promise<ForecastResponse> => {
    const response = await api.get(`/forecast/${symbol}`, { params: { horizon_days: horizonDays } })
    return response.data
  },

  // Get geopolitical risks
  getGeopoliticalRisks: async (): Promise<any> => {
    const response = await api.get('/geopolitical-risks')
    return response.data
  },

  // Get company news
  getCompanyNews: async (symbol: string, limit: number = 10): Promise<any> => {
    const response = await api.get(`/news/${symbol}`, { params: { limit } })
    const data: any = response.data
    const raw = Array.isArray(data) ? data : (data?.value || [])
    const normalized = (raw || [])
      .map((it: any) => {
        const c = it?.content && typeof it.content === 'object' ? it.content : it
        const provider = c?.provider && typeof c.provider === 'object' ? c.provider : null
        const publisher = c?.publisher || provider?.displayName || provider?.sourceId
        const link =
          c?.link ||
          c?.canonicalUrl?.url ||
          c?.clickThroughUrl?.url ||
          c?.previewUrl ||
          null
        return {
          title: c?.title,
          publisher,
          link,
          pubDate: c?.pubDate || c?.displayTime,
          summary: c?.summary || c?.description,
        }
      })
      .filter((x: any) => x?.title)
    return normalized
  },

  getCompanyNewsSummary: async (symbol: string, limit: number = 20): Promise<NewsSummaryResponse> => {
    const response = await api.get(`/news/${symbol}/summary`, { params: { limit } })
    return response.data
  },

  // Get investment recommendations
  getRecommendations: async (limit: number = 25): Promise<any> => {
    try {
      const response = await api.get('/recommendations', { params: { limit }, timeout: 45000 })
      return response.data
    } catch (e: any) {
      const msg = String(e?.message || '').toLowerCase()
      // Backend can stall or restart; retry once on network/timeout.
      if (msg.includes('network error') || msg.includes('timeout')) {
        const response = await api.get('/recommendations', { params: { limit }, timeout: 45000 })
        return response.data
      }
      throw e
    }
  },

  // Get market opportunities
  getOpportunities: async (): Promise<any> => {
    const response = await api.get('/market-opportunities')
    return response.data
  },

  // Get live intelligence feed
  getIntelligenceFeed: async (): Promise<any[]> => {
    // Network errors happen when backend restarts; retry once.
    try {
      const response = await api.get('/intelligence-feed', { timeout: 20000 })
      return response.data
    } catch (e: any) {
      const msg = String(e?.message || '')
      if (msg.toLowerCase().includes('network error')) {
        const response = await api.get('/intelligence-feed', { timeout: 20000 })
        return response.data
      }
      throw e
    }
  },

  // Get portfolio data
  getPortfolioData: async (): Promise<any> => {
    const response = await api.get('/portfolio')
    return response.data
  },

  // Get available companies
  getAvailableCompanies: async (): Promise<any[]> => {
    const response = await api.get('/available-companies')
    return response.data
  },

  // Get user holdings
  getUserHoldings: async (): Promise<any[]> => {
    const response = await api.get('/user-holdings')
    return response.data
  },

  // Add holding
  addHolding: async (holding: any): Promise<any> => {
    const response = await api.post('/user-holdings', holding)
    return response.data
  },

  // Delete holding
  deleteHolding: async (holdingId: string): Promise<any> => {
    const response = await api.delete(`/user-holdings/${holdingId}`)
    return response.data
  },

  // Get portfolio strategy
  getPortfolioStrategy: async (): Promise<any> => {
    const response = await api.get('/portfolio-strategy')
    return response.data
  },

  // Get investment tips
  getTips: async (): Promise<any> => {
    const response = await api.get('/tips')
    return response.data
  },

  getAutoLearningReport: async (windowSize: number = 200): Promise<any> => {
    try {
      const response = await api.get('/auto-learning/report', { params: { window_size: windowSize }, timeout: 15000 })
      return response.data
    } catch (e: any) {
      const msg = String(e?.message || '').toLowerCase()
      if (msg.includes('network error') || msg.includes('timeout')) {
        const response = await api.get('/auto-learning/report', { params: { window_size: windowSize }, timeout: 15000 })
        return response.data
      }
      throw e
    }
  },

  // Get portfolio allocation
  getAllocation: async (riskProfile: string = 'moderate'): Promise<any> => {
    const response = await api.get(`/allocation/profile/${riskProfile}`)
    return response.data
  },
}

export default api
