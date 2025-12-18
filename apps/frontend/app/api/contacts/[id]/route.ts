import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken } from "@/lib/api-client"

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const authToken = getAuthToken(request)
    const data = await apiRequest(`/api/contacts/${id}/`, {
      method: 'GET',
      authToken,
    })
    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error fetching contact:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch contact" },
      { status: 500 }
    )
  }
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const updates = await request.json()
    const authToken = getAuthToken(request)
    
    const data = await apiRequest(`/api/contacts/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
      authToken,
    })
    
    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error updating contact:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to update contact" },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const authToken = getAuthToken(request)
    
    await apiRequest(`/api/contacts/${id}/`, {
      method: 'DELETE',
      authToken,
    })
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[API] Error deleting contact:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to delete contact" },
      { status: 500 }
    )
  }
}
