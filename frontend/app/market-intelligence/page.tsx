'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, Newspaper, Globe, Activity } from 'lucide-react'
import { intelligenceApi } from '../../lib/api'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ReferenceLine, Scatter } from 'recharts'

export default function MarketIntelligencePage() {
  const router = useRouter()
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [selectedPeriod, setSelectedPeriod] = useState('1y')
  const [search, setSearch] = useState('')
  const [companyUniverse, setCompanyUniverse] = useState<any[]>([])
  const [historyView, setHistoryView] = useState<'chart' | 'table'>('chart')
  const [showProjection, setShowProjection] = useState(true)
  const [forecastHorizon, setForecastHorizon] = useState(20)
  const [forecast, setForecast] = useState<any>(null)
  const [historicalData, setHistoricalData] = useState<any[]>([])
  const [geopoliticalRisks, setGeopoliticalRisks] = useState<any>(null)
  const [riskSentiment, setRiskSentiment] = useState<any>(null)
  const [news, setNews] = useState<any[]>([])
  const [newsSummary, setNewsSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [selectedSymbol, selectedPeriod])

  useEffect(() => {
    if (historyView === 'chart' && showProjection) {
      fetchForecast()
    }
  }, [selectedSymbol, forecastHorizon, historyView, showProjection])

  useEffect(() => {
    fetchUniverse()
  }, [])

  const fetchUniverse = async () => {
    try {
      const [companies, holdings] = await Promise.all([
        intelligenceApi.getAvailableCompanies(),
        intelligenceApi.getUserHoldings(),
      ])

      const holdingSymbols = new Set((holdings || []).map((h: any) => String(h.symbol || '').toUpperCase()))

      // Put holdings first, then the rest
      const sorted = (companies || []).slice().sort((a: any, b: any) => {
        const aHold = holdingSymbols.has(String(a.symbol || '').toUpperCase()) ? 0 : 1
        const bHold = holdingSymbols.has(String(b.symbol || '').toUpperCase()) ? 0 : 1
        return aHold - bHold || String(a.symbol || '').localeCompare(String(b.symbol || ''))
      })

      setCompanyUniverse(sorted)
      // If selectedSymbol isn't in list (edge), keep it as-is
    } catch (e) {
      console.error('Error fetching company universe:', e)
    }
  }

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [histData, geoRisks, sentiment, newsData, newsSum] = await Promise.all([
        intelligenceApi.getHistoricalData(selectedSymbol, selectedPeriod),
        intelligenceApi.getGeopoliticalRisks(),
        intelligenceApi.getRiskSentiment(),
        intelligenceApi.getCompanyNews(selectedSymbol, 5),
        intelligenceApi.getCompanyNewsSummary(selectedSymbol, 20).catch(() => null),
      ])
      setHistoricalData(histData)
      setGeopoliticalRisks(geoRisks)
      setRiskSentiment(sentiment)
      // Be tolerant: backend may return either an array (normalized) or a provider envelope { value: [...] }
      const rawNews = Array.isArray(newsData) ? newsData : (newsData?.value || [])
      const normalized = (rawNews || []).map((it: any) => {
        // Some providers nest under { content: {...} }
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
        }
      }).filter((x: any) => x?.title)
      setNews(normalized)
      setNewsSummary(newsSum)
    } catch (error) {
      console.error('Error fetching market intelligence:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchForecast = async () => {
    try {
      const data = await intelligenceApi.getForecast(selectedSymbol, forecastHorizon)
      setForecast(data)
    } catch (e) {
      console.error('Error fetching forecast:', e)
      setForecast(null)
    }
  }

  const periods = [
    { value: '1d', label: '1 Day' },
    { value: '5d', label: '5 Days' },
    { value: '1mo', label: '1 Month' },
    { value: '3mo', label: '3 Months' },
    { value: '6mo', label: '6 Months' },
    { value: '1y', label: '1 Year' },
    { value: '2y', label: '2 Years' },
    { value: '5y', label: '5 Years' },
  ]

  const currencySymbol = selectedSymbol.endsWith('.NS') ? '₹' : '$'

  const filteredUniverse = companyUniverse.filter((c: any) => {
    const sym = String(c.symbol || '')
    const sec = String(c.sector || '')
    const mk = String(c.market || '')
    const q = search.trim().toLowerCase()
    if (!q) return true
    return sym.toLowerCase().includes(q) || sec.toLowerCase().includes(q) || mk.toLowerCase().includes(q)
  })

  const addTradingDays = (start: Date, tradingDays: number) => {
    const d = new Date(start.getTime())
    let added = 0
    while (added < tradingDays) {
      d.setDate(d.getDate() + 1)
      const day = d.getDay()
      if (day !== 0 && day !== 6) added += 1 // skip weekends
    }
    return d
  }

  const chartData = (historicalData || [])
    .map((d: any) => {
      const dt = d?.Date ? new Date(d.Date) : null
      return {
        date: dt && !isNaN(dt.getTime()) ? dt.toLocaleDateString() : '',
        dateTs: dt && !isNaN(dt.getTime()) ? dt.getTime() : null,
        dateObj: dt && !isNaN(dt.getTime()) ? dt : null,
        close: typeof d?.Close === 'number' ? d.Close : null,
      }
    })
    .filter((d: any) => d.dateObj && d.date && d.dateTs && typeof d.close === 'number')

  const chartDataWithProjection = (() => {
    if (!showProjection || !forecast || chartData.length === 0) return chartData

    const lastDateObj = chartData[chartData.length - 1].dateObj as Date
    const futureDateObj = addTradingDays(lastDateObj, Number(forecast.horizon_days || forecastHorizon))
    const futureLabel = futureDateObj.toLocaleDateString()
    const base = chartData.map((p: any) => ({ ...p, p10: null, p50: null, p90: null }))

    const lastIdx = base.length - 1
    base[lastIdx] = { ...base[lastIdx], p10: base[lastIdx].close, p50: base[lastIdx].close, p90: base[lastIdx].close }

    base.push({
      date: futureLabel,
      dateTs: futureDateObj.getTime(),
      dateObj: futureDateObj,
      close: null, // keep the historical line ending at "today"
      p10: forecast.price_quantiles?.p10 ?? null,
      p50: forecast.price_quantiles?.p50 ?? null,
      p90: forecast.price_quantiles?.p90 ?? null,
    })

    return base
  })()

  const projectionRowForTable = (() => {
    if (!showProjection || !forecast || chartData.length === 0) return null
    const lastDateObj = chartData[chartData.length - 1].dateObj as Date
    const futureDateObj = addTradingDays(lastDateObj, Number(forecast.horizon_days || forecastHorizon))
    return {
      date: futureDateObj.toLocaleDateString(),
      p10: forecast.price_quantiles?.p10 ?? null,
      p50: forecast.price_quantiles?.p50 ?? null,
      p90: forecast.price_quantiles?.p90 ?? null,
      upProb: typeof forecast.direction_up_prob === 'number' ? forecast.direction_up_prob : null,
    }
  })()

  const projectionMarkers = (() => {
    if (!showProjection || !forecast || chartData.length === 0) return null
    const last = chartData[chartData.length - 1]
    const lastDateObj = last.dateObj as Date
    const futureDateObj = addTradingDays(lastDateObj, Number(forecast.horizon_days || forecastHorizon))
    const futureTs = futureDateObj.getTime()
    return {
      lastTs: last.dateTs,
      futureTs,
      futureLabel: futureDateObj.toLocaleDateString(),
      p10: forecast.price_quantiles?.p10 ?? null,
      p50: forecast.price_quantiles?.p50 ?? null,
      p90: forecast.price_quantiles?.p90 ?? null,
      lastClose: last.close,
    }
  })()

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
            <h1 className="text-4xl font-bold gradient-text mb-2">Market Intelligence</h1>
            <p className="text-text-secondary">Comprehensive market analysis with geopolitical insights</p>
          </div>
        </motion.div>

        {/* Controls */}
        <div className="mb-6 flex flex-wrap gap-4">
          <div className="flex flex-col gap-2 min-w-[320px]">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search symbols (US + India)…"
              className="px-4 py-2 rounded-lg bg-panel-bg text-text-primary outline-none"
            />
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="px-4 py-2 rounded-lg bg-panel-bg text-text-primary outline-none"
            >
              {filteredUniverse.slice(0, 250).map((c: any) => (
                <option key={c.symbol} value={c.symbol}>
                  {c.symbol} ({c.market}) - {c.sector}
                </option>
              ))}
            </select>
            <div className="text-xs text-text-secondary">
              Showing {Math.min(filteredUniverse.length, 250)} of {filteredUniverse.length} companies
            </div>
          </div>
          <div className="flex gap-2">
            {periods.map((period) => (
              <button
                key={period.value}
                onClick={() => setSelectedPeriod(period.value)}
                className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                  selectedPeriod === period.value ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-center text-text-secondary">Loading market intelligence...</div>
        ) : (
          <div className="space-y-6">
            {/* Historical Data Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <Activity className="w-6 h-6 text-accent" />
                  <h3 className="text-xl font-bold gradient-text">Historical Price Data</h3>
                </div>
                <div className="flex gap-2">
                  <select
                    value={forecastHorizon}
                    onChange={(e) => setForecastHorizon(Number(e.target.value))}
                    className="px-3 py-2 rounded-lg text-sm bg-panel-bg text-text-primary outline-none"
                    title="Forecast horizon (trading days)"
                  >
                    <option value={20}>+20d</option>
                    <option value={60}>+60d</option>
                    <option value={252}>+252d</option>
                  </select>
                  <button
                    onClick={() => setShowProjection((v) => !v)}
                    className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                      showProjection ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                    }`}
                    title="Toggle forecast projection"
                  >
                    Projection
                  </button>
                  <button
                    onClick={() => setHistoryView('chart')}
                    className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                      historyView === 'chart' ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                    }`}
                  >
                    Chart
                  </button>
                  <button
                    onClick={() => setHistoryView('table')}
                    className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                      historyView === 'table' ? 'bg-accent text-white' : 'bg-panel-bg text-text-secondary hover:bg-panel-bg/80'
                    }`}
                  >
                    Table
                  </button>
                </div>
              </div>
              {historicalData.length > 0 ? (
                historyView === 'chart' ? (
                  <div className="h-[320px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartDataWithProjection}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis
                          dataKey="dateTs"
                          type="number"
                          scale="time"
                          tick={{ fontSize: 12 }}
                          domain={['dataMin', 'dataMax']}
                          tickFormatter={(ts: any) => {
                            const d = new Date(Number(ts))
                            return !isNaN(d.getTime()) ? d.toLocaleDateString() : ''
                          }}
                          minTickGap={24}
                        />
                        <YAxis
                          tick={{ fontSize: 12 }}
                          domain={['auto', 'auto']}
                          tickFormatter={(v) => `${currencySymbol}${Number(v).toFixed(0)}`}
                        />
                        <Tooltip
                          formatter={(v: any, name: any) => {
                            const label =
                              name === 'close' ? 'Close' :
                              name === 'p10' ? 'P10 (bear case)' :
                              name === 'p50' ? 'P50 (base case)' :
                              name === 'p90' ? 'P90 (bull case)' :
                              String(name)
                            if (v == null || Number.isNaN(Number(v))) return ['—', label]
                            return [`${currencySymbol}${Number(v).toFixed(2)}`, label]
                          }}
                          labelFormatter={(l: any) => {
                            const d = new Date(Number(l))
                            return `Date: ${!isNaN(d.getTime()) ? d.toLocaleDateString() : String(l)}`
                          }}
                        />
                        <Legend />
                        {showProjection && projectionMarkers?.futureTs && (
                          <ReferenceLine
                            x={projectionMarkers.futureTs}
                            stroke="#94a3b8"
                            strokeDasharray="3 3"
                            label={{ value: `Forecast ${projectionMarkers.futureLabel}`, position: 'insideTopRight', fill: '#94a3b8', fontSize: 12 }}
                            ifOverflow="extendDomain"
                          />
                        )}
                        <Line
                          type="monotone"
                          dataKey="close"
                          name="Close"
                          stroke="#60a5fa"
                          strokeWidth={2.5}
                          dot={false}
                          connectNulls={false}
                          isAnimationActive={false}
                        />
                        {showProjection && forecast && (
                          <>
                            <Line
                              type="monotone"
                              dataKey="p10"
                              name="P10 (bear)"
                              stroke="#f97316"
                              strokeOpacity={0.95}
                              strokeWidth={2.5}
                              strokeDasharray="8 6"
                              dot={{ r: 2.5 }}
                              isAnimationActive={false}
                              connectNulls
                            />
                            <Line
                              type="monotone"
                              dataKey="p50"
                              name="P50 (base)"
                              stroke="#a855f7"
                              strokeOpacity={0.95}
                              strokeWidth={3}
                              strokeDasharray="6 4"
                              dot={{ r: 3 }}
                              isAnimationActive={false}
                              connectNulls
                            />
                            <Line
                              type="monotone"
                              dataKey="p90"
                              name="P90 (bull)"
                              stroke="#22c55e"
                              strokeOpacity={0.95}
                              strokeWidth={2.5}
                              strokeDasharray="8 6"
                              dot={{ r: 2.5 }}
                              isAnimationActive={false}
                              connectNulls
                            />

                            {/* Explicit future markers (very visible) */}
                            {projectionMarkers?.futureTs && (
                              <>
                                <Scatter
                                  name="Forecast P10"
                                  data={[{ dateTs: projectionMarkers.futureTs, value: projectionMarkers.p10 }]}
                                  fill="#f97316"
                                  shape="circle"
                                  xAxisId={0}
                                  yAxisId={0}
                                  dataKey="value"
                                />
                                <Scatter
                                  name="Forecast P50"
                                  data={[{ dateTs: projectionMarkers.futureTs, value: projectionMarkers.p50 }]}
                                  fill="#a855f7"
                                  shape="circle"
                                  xAxisId={0}
                                  yAxisId={0}
                                  dataKey="value"
                                />
                                <Scatter
                                  name="Forecast P90"
                                  data={[{ dateTs: projectionMarkers.futureTs, value: projectionMarkers.p90 }]}
                                  fill="#22c55e"
                                  shape="circle"
                                  xAxisId={0}
                                  yAxisId={0}
                                  dataKey="value"
                                />
                                <Scatter
                                  name="Last close"
                                  data={[{ dateTs: projectionMarkers.lastTs, value: projectionMarkers.lastClose }]}
                                  fill="#60a5fa"
                                  shape="circle"
                                  xAxisId={0}
                                  yAxisId={0}
                                  dataKey="value"
                                />
                              </>
                            )}
                          </>
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                    {showProjection && forecast && (
                      <div className="mt-3 text-sm text-text-secondary">
                        Forecast (+{forecast.horizon_days}d): P10 {currencySymbol}{forecast.price_quantiles?.p10}, P50 {currencySymbol}{forecast.price_quantiles?.p50}, P90 {currencySymbol}{forecast.price_quantiles?.p90} · UpProb {(forecast.direction_up_prob * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="grid grid-cols-4 gap-4 text-sm text-text-secondary mb-2">
                      <div>Date</div>
                      <div>Open</div>
                      <div>High</div>
                      <div>Close</div>
                    </div>
                    {historicalData.slice(-10).map((data: any, index: number) => (
                      <div key={index} className="grid grid-cols-4 gap-4 p-2 bg-panel-bg rounded text-sm">
                        <div>{new Date(data.Date).toLocaleDateString()}</div>
                        <div>{currencySymbol}{data.Open?.toFixed(2)}</div>
                        <div>{currencySymbol}{data.High?.toFixed(2)}</div>
                        <div>{currencySymbol}{data.Close?.toFixed(2)}</div>
                      </div>
                    ))}

                    {projectionRowForTable && (
                      <div className="mt-4">
                        <div className="text-sm font-semibold mb-2 text-text-primary">Projection (P10 / P50 / P90)</div>
                        <div className="grid grid-cols-5 gap-4 text-sm text-text-secondary mb-2">
                          <div>Date</div>
                          <div>P10</div>
                          <div>P50</div>
                          <div>P90</div>
                          <div>UpProb</div>
                        </div>
                        <div className="grid grid-cols-5 gap-4 p-2 bg-panel-bg rounded text-sm">
                          <div>{projectionRowForTable.date}</div>
                          <div>{projectionRowForTable.p10 != null ? `${currencySymbol}${Number(projectionRowForTable.p10).toFixed(2)}` : 'N/A'}</div>
                          <div>{projectionRowForTable.p50 != null ? `${currencySymbol}${Number(projectionRowForTable.p50).toFixed(2)}` : 'N/A'}</div>
                          <div>{projectionRowForTable.p90 != null ? `${currencySymbol}${Number(projectionRowForTable.p90).toFixed(2)}` : 'N/A'}</div>
                          <div>{projectionRowForTable.upProb != null ? `${Math.round(Number(projectionRowForTable.upProb) * 100)}%` : 'N/A'}</div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              ) : (
                <div className="text-text-secondary">No historical data available</div>
              )}
            </motion.div>

            {/* Geopolitical Risks */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Geopolitical Risks</h3>
              </div>
              {geopoliticalRisks ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="text-text-secondary">Overall Risk Level:</span>
                    <span className={`font-bold ${geopoliticalRisks.overall_risk_level === 'high' ? 'text-red-500' : 'text-yellow-500'}`}>
                      {geopoliticalRisks.overall_risk_level?.toUpperCase()}
                    </span>
                  </div>
                  {geopoliticalRisks.critical_events && geopoliticalRisks.critical_events.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2">Critical Events:</div>
                      <div className="space-y-2">
                        {geopoliticalRisks.critical_events.map((event: any, index: number) => (
                          <div key={index} className="p-3 bg-panel-bg rounded-lg">
                            <div className="font-semibold">{event.name}</div>
                            <div className="text-sm text-text-secondary">Category: {event.category}</div>
                            <div className="text-sm text-text-secondary">Impact: {event.impact?.join(', ')}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {geopoliticalRisks.market_impact && (
                    <div>
                      <div className="text-sm font-semibold mb-2">Market Impact:</div>
                      <div className="grid md:grid-cols-2 gap-2">
                        {Object.entries(geopoliticalRisks.market_impact).map(([key, value]: [string, any]) => (
                          <div key={key} className="p-2 bg-panel-bg rounded text-sm">
                            <span className="text-text-secondary capitalize">{key.replace('_', ' ')}:</span>
                            <span className="ml-2 font-semibold">{typeof value === 'string' ? value : JSON.stringify(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-text-secondary">Geopolitical data not available</div>
              )}
            </motion.div>

            {/* Risk Sentiment */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Risk Sentiment</h3>
              </div>
              {riskSentiment ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="text-text-secondary">Current Sentiment:</span>
                    <span className="font-bold capitalize">{riskSentiment.current_sentiment}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-text-secondary">Trend:</span>
                    <span className={`font-bold ${riskSentiment.sentiment_trend === 'deteriorating' ? 'text-red-500' : 'text-green-500'}`}>
                      {riskSentiment.sentiment_trend}
                    </span>
                  </div>
                  {riskSentiment.key_risk_drivers && (
                    <div>
                      <div className="text-sm font-semibold mb-2">Key Risk Drivers:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {riskSentiment.key_risk_drivers.map((driver: string, index: number) => (
                          <li key={index} className="text-sm">{driver}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {riskSentiment.safe_haven_assets && (
                    <div>
                      <div className="text-sm font-semibold mb-2">Safe Haven Assets:</div>
                      <div className="flex gap-2 flex-wrap">
                        {riskSentiment.safe_haven_assets.map((asset: string, index: number) => (
                          <span key={index} className="px-3 py-1 bg-green-500/20 text-green-500 rounded-full text-sm">
                            {asset}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-text-secondary">Risk sentiment data not available</div>
              )}
            </motion.div>

            {/* News */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Newspaper className="w-6 h-6 text-accent" />
                <h3 className="text-xl font-bold gradient-text">Latest News</h3>
              </div>
              {newsSummary && (
                <div className="mb-4 flex flex-wrap items-center gap-2">
                  {(() => {
                    const v = Number(newsSummary.effective_sentiment_avg ?? 0)
                    const label = v > 0.1 ? 'Bullish' : v < -0.1 ? 'Bearish' : 'Neutral'
                    const cls = v > 0.1 ? 'bg-green-500/20 text-green-500' : v < -0.1 ? 'bg-red-500/20 text-red-500' : 'bg-yellow-500/20 text-yellow-500'
                    return (
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${cls}`}>
                        News sentiment: {label} ({v.toFixed(2)})
                      </span>
                    )
                  })()}
                  {newsSummary.event_counts &&
                    Object.entries(newsSummary.event_counts)
                      .sort((a: any, b: any) => Number(b[1]) - Number(a[1]))
                      .slice(0, 4)
                      .map(([k, v]: any) => (
                        <span key={k} className="px-3 py-1 rounded-full text-sm bg-panel-bg text-text-secondary">
                          {k}: {v}
                        </span>
                      ))}
                </div>
              )}
              {news && news.length > 0 ? (
                <div className="space-y-3">
                  {news.map((item: any, index: number) => (
                    <div key={index} className="p-4 bg-panel-bg rounded-lg hover:bg-panel-bg/80 transition-colors cursor-pointer">
                      <div className="font-semibold mb-1">{item.title}</div>
                      <div className="text-sm text-text-secondary">{item.publisher}</div>
                      {item.link && (
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-accent hover:underline"
                        >
                          Read more
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-text-secondary">No news available</div>
              )}
            </motion.div>
          </div>
        )}
      </div>
    </div>
  )
}
