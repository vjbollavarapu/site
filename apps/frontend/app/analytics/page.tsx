"use client"

import { useState } from "react"
import { Calendar, Download, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { AnalyticsKPIs } from "@/components/analytics-kpis"
import { AnalyticsCharts } from "@/components/analytics-charts"
import { AnalyticsTables } from "@/components/analytics-tables"
import { useAnalytics } from "@/hooks/use-analytics"
import { format, subDays } from "date-fns"

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState("30")
  const [realtime, setRealtime] = useState(false)

  const startDate = format(subDays(new Date(), Number.parseInt(dateRange)), "yyyy-MM-dd")
  const endDate = format(new Date(), "yyyy-MM-dd")

  const { data, isLoading, error, refetch } = useAnalytics(startDate, endDate, realtime)

  const handleExport = async (format: string) => {
    // Export functionality
    console.log(`Exporting data in ${format} format`)
    const response = await fetch(`/api/analytics/export?format=${format}&start_date=${startDate}&end_date=${endDate}`)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `analytics-${startDate}-to-${endDate}.${format}`
    a.click()
  }

  return (
    <div className="flex min-h-screen bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col">
        <DashboardHeader />
        <main className="flex-1 p-6 lg:p-8 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
              <p className="text-muted-foreground mt-1">Monitor and analyze your business metrics</p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Switch id="realtime" checked={realtime} onCheckedChange={setRealtime} />
                <Label htmlFor="realtime" className="text-sm font-medium cursor-pointer">
                  Real-time
                </Label>
              </div>

              <Button variant="outline" size="sm" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>

              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="w-[180px]">
                  <Calendar className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Select range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 90 days</SelectItem>
                  <SelectItem value="365">Last year</SelectItem>
                </SelectContent>
              </Select>

              <Select onValueChange={handleExport}>
                <SelectTrigger className="w-[140px]">
                  <Download className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Export" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">Export CSV</SelectItem>
                  <SelectItem value="pdf">Export PDF</SelectItem>
                  <SelectItem value="json">Export JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* KPI Cards */}
          <AnalyticsKPIs data={data?.kpis} isLoading={isLoading} />

          {/* Charts */}
          <AnalyticsCharts data={data?.charts} isLoading={isLoading} dateRange={dateRange} />

          {/* Data Tables */}
          <AnalyticsTables data={data?.tables} isLoading={isLoading} startDate={startDate} endDate={endDate} />
        </main>
      </div>
    </div>
  )
}
