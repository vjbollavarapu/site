import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    const endpoint = queryString ? `/api/leads/?${queryString}` : '/api/leads/'
    
    // Get auth token from headers (X-Auth-Token) or Authorization header
    let authToken = getAuthToken(request)
    
    // If no token in Authorization header, try X-Auth-Token header
    if (!authToken) {
      authToken = request.headers.get('x-auth-token')
    }
    
    // Try to fetch from backend
    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    // Transform Django response to match frontend format
    const leads = Array.isArray(data) ? data : (data.results || data || [])
    
    return NextResponse.json(leads)
  } catch (error) {
    console.error("[API] Error fetching leads:", error)
    
    // Provide more detailed error information
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch leads"
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
