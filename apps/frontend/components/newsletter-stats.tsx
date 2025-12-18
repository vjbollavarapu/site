"use client"

import { useSubscriberStats } from "@/hooks/use-subscribers"
import { Card } from "@/components/ui/card"
import { Users, CheckCircle, XCircle, AlertCircle, TrendingUp } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

export function NewsletterStats() {
  const { stats, isLoading } = useSubscriberStats()

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="p-6">
            <Skeleton className="h-20" />
          </Card>
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: "Total Subscribers",
      value: stats.totalSubscribers.toLocaleString(),
      icon: Users,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      title: "Active Subscribers",
      value: stats.activeSubscribers.toLocaleString(),
      icon: CheckCircle,
      color: "text-green-500",
      bgColor: "bg-green-500/10",
    },
    {
      title: "Unsubscribed (30d)",
      value: stats.unsubscribed30d.toLocaleString(),
      icon: XCircle,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
    },
    {
      title: "Bounced",
      value: stats.bounced.toLocaleString(),
      icon: AlertCircle,
      color: "text-red-500",
      bgColor: "bg-red-500/10",
    },
    {
      title: "Growth Rate",
      value: `${stats.growthRate >= 0 ? "+" : ""}${stats.growthRate.toFixed(1)}%`,
      icon: TrendingUp,
      color: stats.growthRate >= 0 ? "text-green-500" : "text-red-500",
      bgColor: stats.growthRate >= 0 ? "bg-green-500/10" : "bg-red-500/10",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.title} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">{card.title}</p>
                <p className="text-2xl font-bold text-foreground mt-2">{card.value}</p>
              </div>
              <div className={`${card.bgColor} p-3 rounded-lg`}>
                <Icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
