import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { StatsCards } from "@/components/stats-cards"
import { ChartsSection } from "@/components/charts-section"
import { QuickActions } from "@/components/quick-actions"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col">
        <DashboardHeader />
        <main className="flex-1 p-6 lg:p-8 space-y-8 bg-gradient-to-br from-background via-background to-muted/20">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard Overview</h1>
            <p className="text-muted-foreground mt-2">Monitor your business metrics in real-time</p>
          </div>
          <StatsCards />
          <ChartsSection />
          <QuickActions />
        </main>
      </div>
    </div>
  )
}
