import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    // Mock implementation - replace with database query
    return NextResponse.json({
      entry: {
        id,
        // ... mock data
      },
    })
  } catch (error) {
    console.error("[v0] Error fetching entry:", error)
    return NextResponse.json({ error: "Failed to fetch entry" }, { status: 500 })
  }
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const updates = await request.json()

    // Add timestamp fields based on status change
    const timestampUpdates: Record<string, string> = {}
    if (updates.status === "approved" && !updates.approvedAt) {
      timestampUpdates.approvedAt = new Date().toISOString()
    }
    if (updates.status === "invited" && !updates.invitedAt) {
      timestampUpdates.invitedAt = new Date().toISOString()
    }
    if (updates.status === "onboarded" && !updates.onboardedAt) {
      timestampUpdates.onboardedAt = new Date().toISOString()
    }

    // Mock implementation - replace with database update
    return NextResponse.json({
      entry: {
        id,
        ...updates,
        ...timestampUpdates,
      },
    })
  } catch (error) {
    console.error("[v0] Error updating entry:", error)
    return NextResponse.json({ error: "Failed to update entry" }, { status: 500 })
  }
}
