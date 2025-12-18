"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, ClipboardList, Target, Mail, TrendingUp, TrendingDown } from "lucide-react"
import { fetchDashboardStats } from "@/lib/api"

export function StatsCards() {
  const [stats, setStats] = useState({
    contacts: { total: 0, new: 0, pending: 0, trend: 0 },
    waitlist: { total: 0, pending: 0, avgScore: 0, trend: 0 },
    leads: { total: 0, qualified: 0, conversionRate: 0, trend: 0 },
    newsletter: { total: 0, active: 0, unsubscribes: 0, growthRate: 0 },
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchDashboardStats()
        setStats(data)
      } catch (error) {
        console.error("[v0] Failed to load stats:", error)
      } finally {
        setLoading(false)
      }
    }
    loadStats()
  }, [])

  const cards = [
    {
      title: "Contacts Overview",
      icon: Users,
      data: [
        { label: "Total Contacts", value: stats.contacts.total.toLocaleString() },
        { label: "New (7 days)", value: stats.contacts.new },
        { label: "Pending", value: stats.contacts.pending },
      ],
      trend: stats.contacts.trend,
      link: "/contacts",
      gradient: "from-blue-500/10 to-blue-600/5",
      iconBg: "bg-blue-500/10",
      iconColor: "text-blue-600",
    },
    {
      title: "Waitlist Overview",
      icon: ClipboardList,
      data: [
        { label: "Total Entries", value: stats.waitlist.total.toLocaleString() },
        { label: "Pending", value: stats.waitlist.pending },
        { label: "Avg Priority", value: stats.waitlist.avgScore.toFixed(1) },
      ],
      trend: stats.waitlist.trend,
      link: "/waitlist",
      gradient: "from-emerald-500/10 to-emerald-600/5",
      iconBg: "bg-emerald-500/10",
      iconColor: "text-emerald-600",
    },
    {
      title: "Leads Overview",
      icon: Target,
      data: [
        { label: "Total Leads", value: stats.leads.total.toLocaleString() },
        { label: "Qualified", value: stats.leads.qualified },
        { label: "Conversion", value: `${stats.leads.conversionRate}%` },
      ],
      trend: stats.leads.trend,
      link: "/leads",
      gradient: "from-violet-500/10 to-violet-600/5",
      iconBg: "bg-violet-500/10",
      iconColor: "text-violet-600",
    },
    {
      title: "Newsletter Overview",
      icon: Mail,
      data: [
        { label: "Subscribers", value: stats.newsletter.total.toLocaleString() },
        { label: "Active", value: stats.newsletter.active.toLocaleString() },
        { label: "Growth Rate", value: `${stats.newsletter.growthRate}%` },
      ],
      trend: stats.newsletter.growthRate,
      link: "/newsletter",
      gradient: "from-orange-500/10 to-orange-600/5",
      iconBg: "bg-orange-500/10",
      iconColor: "text-orange-600",
    },
  ]

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon
        const isPositive = card.trend >= 0
        return (
          <Card
            key={card.title}
            className={`relative overflow-hidden border-border bg-gradient-to-br ${card.gradient} backdrop-blur-sm shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer group`}
          >
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-sm font-medium text-card-foreground">{card.title}</CardTitle>
              <div className={`p-2 rounded-lg ${card.iconBg} group-hover:scale-110 transition-transform duration-200`}>
                <Icon className={`h-5 w-5 ${card.iconColor}`} />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {loading ? (
                <div className="space-y-2">
                  <div className="h-8 bg-muted animate-pulse rounded" />
                  <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
                </div>
              ) : (
                <>
                  {card.data.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <span className="text-xs text-muted-foreground">{item.label}</span>
                      <span className={`${idx === 0 ? "text-2xl" : "text-sm"} font-semibold text-foreground`}>
                        {item.value}
                      </span>
                    </div>
                  ))}
                  <div
                    className={`flex items-center gap-1.5 pt-2 px-2 py-1 rounded-md ${isPositive ? "bg-emerald-500/10" : "bg-red-500/10"}`}
                  >
                    {isPositive ? (
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-600" />
                    ) : (
                      <TrendingDown className="h-3.5 w-3.5 text-red-600" />
                    )}
                    <span className={`text-xs font-semibold ${isPositive ? "text-emerald-600" : "text-red-600"}`}>
                      {isPositive ? "+" : ""}
                      {card.trend}%
                    </span>
                    <span className="text-xs text-muted-foreground">vs last month</span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
