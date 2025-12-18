import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const endpoint = `/api/newsletter/subscribers/${params.id}/`
    const authToken = getAuthToken(request)

    const data = await apiRequest(endpoint, {
      method: 'GET',
      authToken,
    })

    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error fetching subscriber:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to fetch subscriber"
    
    if (errorMessage.includes('404') || errorMessage.includes('Not found')) {
      return NextResponse.json(
        { error: "Subscriber not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const endpoint = `/api/newsletter/subscribers/${params.id}/`
    const authToken = getAuthToken(request)
    const body = await request.json()

    const data = await apiRequest(endpoint, {
      method: 'PATCH',
      authToken,
      body: JSON.stringify(body),
    })

    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error updating subscriber:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to update subscriber"
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const endpoint = `/api/newsletter/subscribers/${params.id}/`
    const authToken = getAuthToken(request)

    await apiRequest(endpoint, {
      method: 'DELETE',
      authToken,
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[API] Error deleting subscriber:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to delete subscriber"
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
