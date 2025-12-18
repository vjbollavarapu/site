import { type NextRequest, NextResponse } from "next/server"
import { apiRequest, getAuthToken, API_BASE_URL } from "@/lib/api-client"

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    // Note: The backend doesn't have a specific resend verification endpoint
    // We'll need to check if this functionality exists or implement it
    // For now, we'll return an error indicating it's not implemented
    return NextResponse.json(
      { error: "Resend verification not yet implemented in backend" },
      { status: 501 } // Not Implemented
    )
  } catch (error) {
    console.error("[API] Error resending verification:", error)
    const errorMessage = error instanceof Error ? error.message : "Failed to resend verification"
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
