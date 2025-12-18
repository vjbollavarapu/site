import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    const endpoint = queryString 
      ? `/api/newsletter/subscribers/export_csv/?${queryString}` 
      : '/api/newsletter/subscribers/export_csv/'

    const authToken = getAuthToken(request)

    // Fetch CSV from backend
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': authToken ? `Basic ${authToken}` : '',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const csv = await response.text()

    return new NextResponse(csv, {
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=newsletter_subscribers.csv",
      },
    })
  } catch (error) {
    console.error("[API] Error exporting subscribers:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to export subscribers"
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
