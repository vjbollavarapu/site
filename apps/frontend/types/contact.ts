export interface Contact {
  id: string
  name: string
  email: string
  company?: string
  subject: string
  message: string
  status: "new" | "contacted" | "resolved" | "archived"
  priority: "low" | "medium" | "high" | "urgent"
  assignedTo: string
  createdAt: string
  activity?: Activity[]
}

export interface Activity {
  id: string
  type: "note" | "status_change" | "priority_change"
  message: string
  timestamp: string
  user: string
}
