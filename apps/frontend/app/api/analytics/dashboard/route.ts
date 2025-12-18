import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"
import { format, parseISO } from "date-fns"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const startDate = searchParams.get("start_date") || searchParams.get("date_from")
    const endDate = searchParams.get("end_date") || searchParams.get("date_to")

    const queryParams = new URLSearchParams()
    if (startDate) queryParams.append('date_from', startDate)
    if (endDate) queryParams.append('date_to', endDate)

    const endpoint = queryParams.toString() 
      ? `/api/analytics/dashboard/?${queryParams.toString()}` 
      : '/api/analytics/dashboard/'

    const authToken = getAuthToken(request)

    // Fetch from backend
    const backendData = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    // Transform backend data to match frontend format
    const overview = backendData.overview || {}
    const dailyPageviews = backendData.daily_pageviews || []
    const topPages = backendData.top_pages || []
    const trafficSources = backendData.traffic_sources || []
    const conversionFunnel = backendData.conversion_funnel || []

    // Format average session duration
    const avgDurationSeconds = overview.avg_session_duration || 0
    const minutes = Math.floor(avgDurationSeconds / 60)
    const seconds = Math.floor(avgDurationSeconds % 60)
    const avgSessionDuration = `${minutes}m ${seconds}s`

    // Transform daily pageviews for chart
    const pageViewsOverTime = dailyPageviews.map((item: any) => ({
      date: format(parseISO(item.date), "MMM dd"),
      views: item.count || 0,
    }))

    // Transform top pages
    const topPagesFormatted = topPages.map((item: any) => ({
      page: item.page_url || item.page_title || '/',
      views: item.views || 0,
    }))

    // Transform traffic sources
    const trafficSourcesFormatted = trafficSources.map((item: any) => {
      // Extract domain name from referrer URL
      let name = "Direct"
      if (item.referrer_url) {
        try {
          const url = new URL(item.referrer_url)
          name = url.hostname.replace('www.', '')
        } catch {
          name = item.referrer_url
        }
      }
      return {
        name,
        value: item.count || 0,
      }
    })

    // Transform conversion funnel to event categories format
    const eventCategories = conversionFunnel.map((item: any) => ({
      name: item.conversion_type || 'Other',
      value: item.count || 0,
    }))

    // Transform conversions over time (using daily pageviews as proxy for now)
    const conversionsOverTime = dailyPageviews.map((item: any) => ({
      date: format(parseISO(item.date), "MMM dd"),
      conversions: 0, // Backend doesn't provide daily conversions breakdown
    }))

    const data = {
      kpis: {
        totalPageViews: overview.total_pageviews || 0,
        pageViewsChange: 0, // Backend doesn't provide change percentage
        uniqueVisitors: overview.unique_visitors || 0,
        visitorsChange: 0, // Backend doesn't provide change percentage
        totalEvents: 0, // Backend doesn't provide total events in overview
        eventsChange: 0,
        conversionRate: overview.bounce_rate ? (100 - overview.bounce_rate) : 0, // Using bounce rate as proxy
        conversionChange: 0,
        avgSessionDuration,
        durationChange: 0,
      },
      charts: {
        pageViewsOverTime,
        topPages: topPagesFormatted,
        eventCategories,
        conversionsOverTime,
        trafficSources: trafficSourcesFormatted,
      },
      tables: {
        pageViews: [], // Would need to fetch from /api/analytics/pageviews/
        events: [], // Would need to fetch from /api/analytics/events/
        conversions: [], // Would need to fetch from /api/analytics/conversions/
      },
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error fetching analytics dashboard:", error)

    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch analytics dashboard"
    const isConnectionError = errorMessage.includes('fetch') || errorMessage.includes('ECONNREFUSED') || errorMessage.includes('Failed to fetch')

    // If it's a connection error, provide helpful message
    if (isConnectionError) {
      return NextResponse.json(
        {
          error: `Cannot connect to backend API at ${API_BASE_URL}. Please ensure the Django backend is running.`,
          details: errorMessage
        },
        { status: 503 } // Service Unavailable
      )
    }

    // For authentication errors
    if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
      return NextResponse.json(
        {
          error: "Authentication required. Please log in.",
          details: errorMessage
        },
        { status: 401 }
      )
    }

    // For other errors, return empty data
    return NextResponse.json(
      {
        kpis: {
          totalPageViews: 0,
          pageViewsChange: 0,
          uniqueVisitors: 0,
          visitorsChange: 0,
          totalEvents: 0,
          eventsChange: 0,
          conversionRate: 0,
          conversionChange: 0,
          avgSessionDuration: "0m 0s",
          durationChange: 0,
        },
        charts: {
          pageViewsOverTime: [],
          topPages: [],
          eventCategories: [],
          conversionsOverTime: [],
          trafficSources: [],
        },
        tables: {
          pageViews: [],
          events: [],
          conversions: [],
        },
      },
      { status: 200 } // Return empty data instead of error
    )
  }
}
