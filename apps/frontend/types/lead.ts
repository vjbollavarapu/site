export type LeadStatus = "new" | "contacted" | "qualified" | "unqualified" | "converted" | "lost"

export type LifecycleStage =
  | "subscriber"
  | "lead"
  | "marketing-qualified"
  | "sales-qualified"
  | "opportunity"
  | "customer"

export interface Lead {
  id: string
  name: string
  email: string
  phone: string
  company: string
  location: string
  leadScore: number
  status: LeadStatus
  lifecycleStage: LifecycleStage
  source: string
  industry: string
  companySize: string
  assignedTo: string | null
  createdAt: string
  updatedAt: string
  timeline?: Array<{
    type: "note" | "event" | "status_change"
    title: string
    description?: string
    date: string
  }>
  notes?: Array<{
    content: string
    author: string
    date: string
  }>
  events?: Array<{
    name: string
    date: string
  }>
}

export interface LeadFilters {
  search?: string
  status?: string
  lifecycleStage?: string
  source?: string
  industry?: string
  companySize?: string
  assignedTo?: string
  scoreMin?: number
  scoreMax?: number
}
