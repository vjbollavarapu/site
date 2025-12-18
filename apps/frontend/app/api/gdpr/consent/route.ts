import { type NextRequest, NextResponse } from "next/server"

// Mock database for storing consent preferences
const consentDatabase = new Map<string, Map<string, { consent_given: boolean; timestamp: string }>>()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, consent_type, consent_given } = body

    // Validate input
    if (!email || !consent_type || typeof consent_given !== "boolean") {
      return NextResponse.json(
        { error: "Missing required fields: email, consent_type, consent_given" },
        { status: 400 },
      )
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: "Invalid email address" }, { status: 400 })
    }

    // Get or create user consent record
    if (!consentDatabase.has(email)) {
      consentDatabase.set(email, new Map())
    }

    const userConsents = consentDatabase.get(email)!

    // Store the consent
    userConsents.set(consent_type, {
      consent_given,
      timestamp: new Date().toISOString(),
    })

    // Log the consent for audit purposes
    console.log(
      `[GDPR Consent] ${email} - ${consent_type}: ${consent_given ? "granted" : "withdrawn"} at ${new Date().toISOString()}`,
    )

    return NextResponse.json(
      {
        success: true,
        message: "Consent preference saved successfully",
        data: {
          email,
          consent_type,
          consent_given,
          timestamp: new Date().toISOString(),
        },
      },
      { status: 200 },
    )
  } catch (error) {
    console.error("[GDPR Consent Error]", error)
    return NextResponse.json({ error: "Failed to save consent preference" }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const email = searchParams.get("email")

    if (!email) {
      return NextResponse.json({ error: "Email parameter is required" }, { status: 400 })
    }

    const userConsents = consentDatabase.get(email)

    if (!userConsents) {
      return NextResponse.json({ error: "No consent records found for this email" }, { status: 404 })
    }

    // Convert Map to object for JSON response
    const consents: Record<string, { consent_given: boolean; timestamp: string }> = {}
    userConsents.forEach((value, key) => {
      consents[key] = value
    })

    return NextResponse.json(
      {
        success: true,
        email,
        consents,
      },
      { status: 200 },
    )
  } catch (error) {
    console.error("[GDPR Consent Error]", error)
    return NextResponse.json({ error: "Failed to retrieve consent preferences" }, { status: 500 })
  }
}
