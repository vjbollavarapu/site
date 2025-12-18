import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    const endpoint = queryString ? `/api/contacts/?${queryString}` : '/api/contacts/'
    
    // Get auth token from headers or cookies
    let authToken = getAuthToken(request)
    
    // If no token in headers, try to get from cookie (for session-based auth)
    if (!authToken) {
      const cookies = request.headers.get('cookie')
      // For now, we'll rely on Basic Auth token passed from client
      // In production, you might want to use session cookies
    }
    
    // Try to fetch from backend
    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken: authToken || undefined,
    })

    // Transform Django response to match frontend format
    // Django returns { results: [...], count: ... } for paginated responses
    // or just an array for non-paginated
    const contacts = Array.isArray(data) ? data : (data.results || data || [])
    
    return NextResponse.json({ contacts })
  } catch (error) {
    console.error("[API] Error fetching contacts:", error)
    
    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch contacts"
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
