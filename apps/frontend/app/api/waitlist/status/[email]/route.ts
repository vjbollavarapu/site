import { type NextRequest, NextResponse } from "next/server"

// Mock database - replace with your actual database
const mockWaitlistData = [
  {
    id: "1",
    email: "john@example.com",
    name: "John Doe",
    company: "Acme Corp",
    status: "pending",
    priorityScore: 85,
    position: 12,
    verified: true,
    createdAt: "2024-01-15T10:00:00Z",
  },
  {
    id: "2",
    email: "jane@startup.com",
    name: "Jane Smith",
    company: "Startup Inc",
    status: "approved",
    priorityScore: 92,
    verified: true,
    createdAt: "2024-01-10T08:30:00Z",
  },
  {
    id: "3",
    email: "bob@enterprise.com",
    name: "Bob Johnson",
    company: "Enterprise LLC",
    status: "invited",
    priorityScore: 88,
    verified: true,
    createdAt: "2024-01-05T14:20:00Z",
  },
  {
    id: "4",
    email: "alice@tech.com",
    name: "Alice Williams",
    company: "Tech Solutions",
    status: "onboarded",
    priorityScore: 95,
    verified: true,
    createdAt: "2023-12-20T09:15:00Z",
  },
  {
    id: "5",
    email: "charlie@declined.com",
    name: "Charlie Brown",
    company: "Small Biz",
    status: "declined",
    priorityScore: 45,
    verified: true,
    createdAt: "2024-01-20T11:45:00Z",
  },
]

export async function GET(request: NextRequest, { params }: { params: { email: string } }) {
  try {
    const email = decodeURIComponent(params.email)

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: "Invalid email format" }, { status: 400 })
    }

    // Find the waitlist entry
    const entry = mockWaitlistData.find((item) => item.email.toLowerCase() === email.toLowerCase())

    if (!entry) {
      return NextResponse.json({ error: "Email not found on waitlist" }, { status: 404 })
    }

    // Calculate position for pending entries
    let position = entry.position
    if (entry.status === "pending" && !position) {
      const pendingEntries = mockWaitlistData
        .filter((item) => item.status === "pending")
        .sort((a, b) => b.priorityScore - a.priorityScore)
      position = pendingEntries.findIndex((item) => item.email === email) + 1
    }

    return NextResponse.json({
      email: entry.email,
      name: entry.name,
      status: entry.status,
      priorityScore: entry.priorityScore,
      position: entry.status === "pending" ? position : undefined,
      verified: entry.verified,
      createdAt: entry.createdAt,
    })
  } catch (error) {
    console.error("[v0] Status check error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
