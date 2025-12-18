import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken } from "@/lib/api-client"

export async function POST(request: NextRequest) {
  try {
    const { ids, status, ...otherUpdates } = await request.json()
    const authToken = getAuthToken(request)
    
    // Update each contact individually (Django doesn't have bulk update endpoint)
    // In production, you might want to add a bulk update endpoint to Django
    const updatePromises = ids.map((id: string) =>
      apiRequest(`/api/contacts/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ status, ...otherUpdates }),
        authToken,
      }).catch((error) => {
        console.error(`[API] Error updating contact ${id}:`, error)
        return null
      })
    )
    
    const results = await Promise.all(updatePromises)
    const successful = results.filter(r => r !== null).length
    
    return NextResponse.json({ 
      success: true, 
      updated: successful,
      total: ids.length 
    })
  } catch (error) {
    console.error("[API] Error bulk updating contacts:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to bulk update contacts" },
      { status: 500 }
    )
  }
}
