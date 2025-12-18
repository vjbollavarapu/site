"use client"

import { Card } from "@/components/ui/card"
import { Eye, Users, MousePointerClick, TrendingUp, Clock } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface KPIData {
  totalPageViews: number
  pageViewsChange: number
  uniqueVisitors: number
  visitorsChange: number
  totalEvents: number
  eventsChange: number
  conversionRate: number
  conversionChange: number
  avgSessionDuration: string
  durationChange: number
}

interface AnalyticsKPIsProps {
  data?: KPIData
  isLoading: boolean
}

export function AnalyticsKPIs({ data, isLoading }: AnalyticsKPIsProps) {
  const kpis = [
    {
      title: "Total Page Views",
      value: data?.totalPageViews?.toLocaleString() || "0",
      change: data?.pageViewsChange || 0,
      icon: Eye,
      color: "from-blue-500 to-blue-600",
    },
    {
      title: "Unique Visitors",
      value: data?.uniqueVisitors?.toLocaleString() || "0",
      change: data?.visitorsChange || 0,
      icon: Users,
      color: "from-purple-500 to-purple-600",
    },
    {
      title: "Total Events",
      value: data?.totalEvents?.toLocaleString() || "0",
      change: data?.eventsChange || 0,
      icon: MousePointerClick,
      color: "from-green-500 to-green-600",
    },
    {
      title: "Conversion Rate",
      value: `${data?.conversionRate || 0}%`,
      change: data?.conversionChange || 0,
      icon: TrendingUp,
      color: "from-orange-500 to-orange-600",
    },
    {
      title: "Avg Session Duration",
      value: data?.avgSessionDuration || "0m 0s",
      change: data?.durationChange || 0,
      icon: Clock,
      color: "from-pink-500 to-pink-600",
    },
  ]

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="p-6">
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-8 w-32 mb-1" />
            <Skeleton className="h-3 w-20" />
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {kpis.map((kpi, index) => {
        const Icon = kpi.icon
        const isPositive = kpi.change >= 0

        return (
          <Card key={index} className="p-6 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium text-muted-foreground">{kpi.title}</p>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${kpi.color}`}>
                <Icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-3xl font-bold tracking-tight">{kpi.value}</p>
              <div className="flex items-center gap-1">
                <span className={`text-xs font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
                  {isPositive ? "↑" : "↓"} {Math.abs(kpi.change)}%
                </span>
                <span className="text-xs text-muted-foreground">vs last period</span>
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
