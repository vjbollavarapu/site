import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  const { ids } = await request.json()

  // In a real app, update database
  console.log("[v0] Bulk converting leads:", ids)

  return NextResponse.json({ success: true, count: ids.length })
}
