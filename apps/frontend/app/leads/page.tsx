"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LeadsTable } from "@/components/leads-table"
import { LeadsPipeline } from "@/components/leads-pipeline"
import { LeadDetailModal } from "@/components/lead-detail-modal"
import { LeadsFilters } from "@/components/leads-filters"
import { Button } from "@/components/ui/button"
import { Download, Upload, Plus } from "lucide-react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { useLeads } from "@/hooks/use-leads"
import type { LeadFilters } from "@/types/lead"

export default function LeadsPage() {
  const [view, setView] = useState<"list" | "pipeline">("list")
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null)
  const [filters, setFilters] = useState<LeadFilters>({})

  const { leads, isLoading, updateLead, bulkQualify, bulkConvert, exportToCSV } = useLeads(filters)

  const handleExport = () => {
    exportToCSV()
  }

  const handleImport = () => {
    // Trigger file input
    const input = document.createElement("input")
    input.type = "file"
    input.accept = ".csv"
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        console.log("[v0] Importing leads from CSV:", file.name)
        // Handle CSV import logic here
      }
    }
    input.click()
  }

  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />

        <main className="flex-1 overflow-auto">
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Leads</h1>
                <p className="text-sm text-muted-foreground mt-1">Manage and track your sales leads</p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleImport}>
                  <Upload className="h-4 w-4 mr-2" />
                  Import
                </Button>
                <Button variant="outline" size="sm" onClick={handleExport}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Lead
                </Button>
              </div>
            </div>

            <LeadsFilters filters={filters} onFiltersChange={setFilters} />

            <Tabs value={view} onValueChange={(v) => setView(v as "list" | "pipeline")}>
              <TabsList>
                <TabsTrigger value="list">List View</TabsTrigger>
                <TabsTrigger value="pipeline">Pipeline View</TabsTrigger>
              </TabsList>

              <TabsContent value="list" className="mt-6">
                <LeadsTable
                  leads={leads}
                  isLoading={isLoading}
                  onLeadClick={setSelectedLeadId}
                  onBulkQualify={bulkQualify}
                  onBulkConvert={bulkConvert}
                />
              </TabsContent>

              <TabsContent value="pipeline" className="mt-6">
                <LeadsPipeline
                  leads={leads}
                  isLoading={isLoading}
                  onLeadClick={setSelectedLeadId}
                  onUpdateLead={updateLead}
                />
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {selectedLeadId && <LeadDetailModal leadId={selectedLeadId} onClose={() => setSelectedLeadId(null)} />}
    </div>
  )
}
