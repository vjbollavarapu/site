import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const endpoint = '/api/newsletter/subscribers/stats/'
    const authToken = getAuthToken(request)

    // Try to fetch from backend
    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    // Transform Django response to match frontend format
    const stats = {
      totalSubscribers: data.total_subscribers || 0,
      activeSubscribers: data.total_subscribers || 0,
      unsubscribed30d: data.total_unsubscribed || 0,
      bounced: data.total_bounced || 0,
      growthRate: data.subscription_growth_last_30_days || 0,
      // Additional stats from backend
      unsubscribeRate: data.unsubscribe_rate || 0,
      bounceRate: data.bounce_rate || 0,
      byStatus: data.by_status || {},
      byPreference: data.by_preference || {},
      bySource: data.by_source || {},
      dailyGrowth: data.daily_growth || [],
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error("[API] Error fetching newsletter stats:", error)

    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch newsletter stats"
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

    // For other errors, return default stats
    return NextResponse.json(
      {
        totalSubscribers: 0,
        activeSubscribers: 0,
        unsubscribed30d: 0,
        bounced: 0,
        growthRate: 0,
      },
      { status: 200 } // Return default stats instead of error
    )
  }
}
