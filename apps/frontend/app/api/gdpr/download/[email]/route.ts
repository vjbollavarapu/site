import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: Promise<{ email: string }> }) {
  try {
    const { email } = await params

    if (!email) {
      return NextResponse.json({ message: "Email is required" }, { status: 400 })
    }

    // Mock data for download - in production, this would fetch from a secure storage location
    const userData = {
      exportDate: new Date().toISOString(),
      email,
      contacts: [
        { id: 1, name: "John Doe", email: "john@example.com", company: "Acme Inc", status: "active" },
        { id: 2, name: "Jane Smith", email: "jane@example.com", company: "Tech Corp", status: "active" },
      ],
      waitlistEntries: [
        {
          id: 1,
          email,
          company: "My Company",
          status: "pending",
          priority: 75,
          submittedAt: "2024-01-15T10:30:00Z",
        },
      ],
      leads: [
        {
          id: 1,
          name: "Bob Johnson",
          email: "bob@example.com",
          company: "Startup Inc",
          status: "new",
          score: 85,
        },
      ],
      newsletterSubscriptions: [
        {
          id: 1,
          email,
          status: "active",
          subscribedAt: "2024-01-01T00:00:00Z",
          source: "website",
        },
      ],
      consentRecords: [
        {
          email,
          marketing: true,
          analytics: false,
          functionalCookies: true,
          performanceCookies: false,
          targetingCookies: false,
          updatedAt: "2024-01-10T15:20:00Z",
        },
      ],
    }

    // Convert to JSON string with formatting
    const jsonData = JSON.stringify(userData, null, 2)

    // Return as downloadable file
    return new NextResponse(jsonData, {
      headers: {
        "Content-Type": "application/json",
        "Content-Disposition": `attachment; filename="gdpr-data-export-${email}-${Date.now()}.json"`,
      },
    })
  } catch (error) {
    console.error("[v0] Error downloading data:", error)
    return NextResponse.json({ message: "Failed to download data" }, { status: 500 })
  }
}
