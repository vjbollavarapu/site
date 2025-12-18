import { type NextRequest, NextResponse } from "next/server"

// Mock lead detail (would come from database)
const mockLead = {
  id: "1",
  name: "Alice Johnson",
  email: "alice@techcorp.com",
  phone: "+1 (555) 123-4567",
  company: "TechCorp Solutions",
  location: "San Francisco, CA",
  leadScore: 85,
  status: "qualified",
  lifecycleStage: "sales-qualified",
  source: "LinkedIn",
  industry: "Technology",
  companySize: "51-200",
  assignedTo: "John Smith",
  createdAt: "2024-01-15T10:00:00Z",
  updatedAt: "2024-01-20T15:30:00Z",
  timeline: [
    {
      type: "event",
      title: "Downloaded whitepaper",
      date: "2024-01-20T15:30:00Z",
    },
    {
      type: "note",
      title: "Follow-up call scheduled",
      description: "Great conversation about their needs",
      date: "2024-01-18T11:00:00Z",
    },
    {
      type: "status_change",
      title: "Status changed to Qualified",
      date: "2024-01-17T09:00:00Z",
    },
  ],
  notes: [
    {
      content: "Very interested in our enterprise plan. Follow up next week.",
      author: "John Smith",
      date: "2024-01-18T11:00:00Z",
    },
  ],
  events: [
    { name: "Downloaded whitepaper", date: "2024-01-20T15:30:00Z" },
    { name: "Visited pricing page", date: "2024-01-19T14:20:00Z" },
    { name: "Signed up for newsletter", date: "2024-01-15T10:00:00Z" },
  ],
}

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  // In a real app, fetch from database
  return NextResponse.json(mockLead)
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const updates = await request.json()

  // In a real app, update database
  const updatedLead = { ...mockLead, ...updates, updatedAt: new Date().toISOString() }

  return NextResponse.json(updatedLead)
}
