"use client"

import { useState, useEffect } from "react"

interface AnalyticsData {
  kpis: {
    totalPageViews: number
    pageViewsChange: number
    uniqueVisitors: number
    visitorsChange: number
    totalEvents: number
    eventsChange: number
    conversionRate: number
    conversionChange: number
    avgSessionDuration: string
    durationChange: number
  }
  charts: {
    pageViewsOverTime: Array<{ date: string; views: number }>
    topPages: Array<{ page: string; views: number }>
    eventCategories: Array<{ name: string; value: number }>
    conversionsOverTime: Array<{ date: string; conversions: number }>
    trafficSources: Array<{ name: string; value: number }>
  }
  tables: {
    pageViews: Array<any>
    events: Array<any>
    conversions: Array<any>
  }
}

export function useAnalytics(startDate: string, endDate: string, realtime: boolean) {
  const [data, setData] = useState<AnalyticsData | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`/api/analytics/dashboard?start_date=${startDate}&end_date=${endDate}`)
      if (!response.ok) throw new Error("Failed to fetch analytics data")
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()

    // Set up real-time polling if enabled
    if (realtime) {
      const interval = setInterval(fetchData, 10000) // Poll every 10 seconds
      return () => clearInterval(interval)
    }
  }, [startDate, endDate, realtime])

  return { data, isLoading, error, refetch: fetchData }
}
