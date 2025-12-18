import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: Promise<{ email: string }> }) {
  try {
    const { email } = await params

    if (!email) {
      return NextResponse.json({ message: "Email is required" }, { status: 400 })
    }

    // Mock data export - in production, this would gather all user data from database
    const userData = {
      email,
      exportDate: new Date().toISOString(),
      contacts: [{ id: 1, name: "John Doe", email: "john@example.com", company: "Acme Inc" }],
      waitlistEntries: [{ id: 1, email, company: "My Company", status: "pending" }],
      leads: [{ id: 1, name: "Jane Smith", email: "jane@example.com", status: "new" }],
      newsletterSubscriptions: [{ id: 1, email, status: "active", subscribedAt: new Date().toISOString() }],
      consentRecords: [
        {
          email,
          marketing: true,
          analytics: false,
          functionalCookies: true,
          updatedAt: new Date().toISOString(),
        },
      ],
    }

    // In production, you would:
    // 1. Generate a JSON or CSV file with the data
    // 2. Store it in a temporary location (e.g., cloud storage)
    // 3. Send an email with the download link
    // 4. Return a download URL

    // For this demo, we'll return success with a mock download URL
    const downloadUrl = `/api/gdpr/download/${encodeURIComponent(email)}`

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    return NextResponse.json({
      message: "Data export prepared successfully",
      downloadUrl,
      userData, // In production, don't return this directly
    })
  } catch (error) {
    console.error("[v0] Error exporting data:", error)
    return NextResponse.json({ message: "Failed to export data" }, { status: 500 })
  }
}
