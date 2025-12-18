import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const endpoint = '/api/dashboard/stats/'
    const authToken = getAuthToken(request)

    // Fetch from backend
    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error fetching dashboard stats:", error)

    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch dashboard stats"
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
        contacts: { total: 0, new: 0, pending: 0, trend: 0 },
        waitlist: { total: 0, pending: 0, avgScore: 0, trend: 0 },
        leads: { total: 0, qualified: 0, conversionRate: 0, trend: 0 },
        newsletter: { total: 0, active: 0, unsubscribes: 0, growthRate: 0 },
      },
      { status: 200 } // Return default stats instead of error
    )
  }
}

