export interface Subscriber {
  id: string
  email: string
  name: string | null
  status: "subscribed" | "unsubscribed" | "bounced" | "complained"
  source: "website" | "landing-page" | "imported" | "api"
  subscribedAt: string
  verified: boolean
  lastEmailSent: string | null
  location?: string
  preferences: string[]
  unsubscribeReason?: string
  unsubscribedAt?: string
  engagement: {
    emailsSent: number
    opens: number
    clicks: number
    lastOpened?: string
    lastClicked?: string
  }
  timeline: {
    date: string
    event: string
    details?: string
  }[]
}

export interface SubscriberStats {
  totalSubscribers: number
  activeSubscribers: number
  unsubscribed30d: number
  bounced: number
  growthRate: number
}
