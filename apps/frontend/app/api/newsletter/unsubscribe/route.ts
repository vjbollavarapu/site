import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function POST(request: NextRequest) {
  try {
    const { ids } = await request.json()
    const authToken = getAuthToken(request)

    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      return NextResponse.json(
        { error: "No subscriber IDs provided" },
        { status: 400 }
      )
    }

    // Update each subscriber to unsubscribed status
    const updatePromises = ids.map((id: string) =>
      apiRequest(`/api/newsletter/subscribers/${id}/`, {
        method: 'PATCH',
        authToken,
        body: JSON.stringify({ subscription_status: 'unsubscribed' }),
      })
    )

    await Promise.all(updatePromises)

    return NextResponse.json({ success: true, count: ids.length })
  } catch (error) {
    console.error("[API] Error bulk unsubscribing:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to unsubscribe subscribers"
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
