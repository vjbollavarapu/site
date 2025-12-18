export type WaitlistStatus = "pending" | "approved" | "invited" | "onboarded" | "declined"

export interface WaitlistEntry {
  id: string
  email: string
  name: string
  company: string
  role: string
  companySize: string
  industry: string
  source: string
  priorityScore: number
  priorityScoreBreakdown?: {
    companySize: number
    industryMatch: number
    roleFit: number
  }
  status: WaitlistStatus
  verified: boolean
  notes?: string
  createdAt: string
  verifiedAt?: string
  approvedAt?: string
  invitedAt?: string
  onboardedAt?: string
}
