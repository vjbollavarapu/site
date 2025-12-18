import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    const endpoint = queryString ? `/api/newsletter/subscribers/?${queryString}` : '/api/newsletter/subscribers/'

    const authToken = getAuthToken(request)

    // Try to fetch from backend
    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    // Transform Django response to match frontend format
    // Django returns { results: [...], count: ... } for paginated responses
    // or just an array for non-paginated
    const rawSubscribers = Array.isArray(data) ? data : (data.results || data || [])

    // Transform backend fields to frontend format
    const subscribers = rawSubscribers.map((sub: any) => ({
      id: sub.id,
      email: sub.email,
      name: sub.name || null,
      status: sub.subscription_status || 'subscribed', // Map subscription_status to status
      source: sub.source || 'website',
      subscribedAt: sub.created_at || new Date().toISOString(),
      verified: sub.is_verified || false,
      lastEmailSent: null, // Not available in backend model
      location: undefined, // Not available in backend model
      preferences: sub.interests || [],
      unsubscribeReason: sub.unsubscribe_reason || undefined,
      unsubscribedAt: sub.unsubscribed_at || undefined,
      engagement: {
        emailsSent: 0, // Not tracked in backend model
        opens: 0, // Not tracked in backend model
        clicks: 0, // Not tracked in backend model
        lastOpened: undefined,
        lastClicked: undefined,
      },
      timeline: [
        {
          date: sub.created_at || new Date().toISOString(),
          event: "Subscribed",
          details: `Via ${sub.source || 'website'}`,
        },
        ...(sub.verified_at ? [{
          date: sub.verified_at,
          event: "Verified",
          details: "Email verified",
        }] : []),
        ...(sub.unsubscribed_at ? [{
          date: sub.unsubscribed_at,
          event: "Unsubscribed",
          details: sub.unsubscribe_reason || "User unsubscribed",
        }] : []),
      ],
    }))

    return NextResponse.json(subscribers)
  } catch (error) {
    console.error("[API] Error fetching newsletter subscribers:", error)

    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch newsletter subscribers"
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

    // For other errors
    return NextResponse.json(
      {
        error: errorMessage,
        details: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    )
  }
}
