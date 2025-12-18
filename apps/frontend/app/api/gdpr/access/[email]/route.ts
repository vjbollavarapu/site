import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: Promise<{ email: string }> }) {
  try {
    const { email } = await params

    if (!email) {
      return NextResponse.json({ message: "Email is required" }, { status: 400 })
    }

    // Mock data access - in production, this would fetch all user data from database
    const userData = {
      email,
      accessDate: new Date().toISOString(),
      personalInfo: {
        email,
        name: "John Doe",
        company: "Acme Inc",
        phone: "+1234567890",
      },
      dataCategories: {
        contacts: 15,
        waitlistEntries: 1,
        leads: 8,
        newsletterSubscriptions: 1,
        consentRecords: 1,
      },
      storageLocations: ["Primary Database", "Analytics Service", "Email Service"],
      retentionPeriods: {
        contacts: "5 years",
        waitlistEntries: "Until processed",
        leads: "3 years",
        newsletterSubscriptions: "Until unsubscribed",
        consentRecords: "7 years",
      },
    }

    return NextResponse.json(userData)
  } catch (error) {
    console.error("[v0] Error accessing data:", error)
    return NextResponse.json({ message: "Failed to access data" }, { status: 500 })
  }
}
