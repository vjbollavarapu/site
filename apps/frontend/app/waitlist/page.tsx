"use client"

import { useState } from "react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { WaitlistKanban } from "@/components/waitlist-kanban"
import { WaitlistTable } from "@/components/waitlist-table"
import { WaitlistDetailModal } from "@/components/waitlist-detail-modal"
import { InviteModal } from "@/components/invite-modal"
import { useWaitlist } from "@/hooks/use-waitlist"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Kanban, List, Search, Download } from "lucide-react"
import type { WaitlistEntry } from "@/types/waitlist"

export default function WaitlistPage() {
  const [view, setView] = useState<"kanban" | "list">("kanban")
  const [searchQuery, setSearchQuery] = useState("")
  const [companySize, setCompanySize] = useState<string>("all")
  const [industry, setIndustry] = useState<string>("all")
  const [source, setSource] = useState<string>("all")
  const [selectedEntry, setSelectedEntry] = useState<WaitlistEntry | null>(null)
  const [inviteEntry, setInviteEntry] = useState<WaitlistEntry | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])

  const { entries, isLoading, updateEntry, bulkUpdateStatus, exportToCSV } = useWaitlist({
    companySize: companySize === "all" ? undefined : companySize,
    industry: industry === "all" ? undefined : industry,
    source: source === "all" ? undefined : source,
  })

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.company.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  const handleBulkApprove = async () => {
    if (selectedIds.length > 0) {
      await bulkUpdateStatus(selectedIds, "approved")
      setSelectedIds([])
    }
  }

  const handleBulkDecline = async () => {
    if (selectedIds.length > 0) {
      await bulkUpdateStatus(selectedIds, "declined")
      setSelectedIds([])
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-auto">
          <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Waitlist</h1>
                <p className="text-muted-foreground mt-1">Manage and track waitlist entries</p>
              </div>
              <div className="flex gap-2">
                {selectedIds.length > 0 && (
                  <>
                    <Button onClick={handleBulkApprove} variant="default">
                      Approve ({selectedIds.length})
                    </Button>
                    <Button onClick={handleBulkDecline} variant="destructive">
                      Decline ({selectedIds.length})
                    </Button>
                  </>
                )}
                <Button onClick={exportToCSV} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </div>

            {/* Filters and Search */}
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex-1 flex gap-3">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by email, name, or company..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={companySize} onValueChange={setCompanySize}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Company Size" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sizes</SelectItem>
                    <SelectItem value="1-10">1-10</SelectItem>
                    <SelectItem value="11-50">11-50</SelectItem>
                    <SelectItem value="51-200">51-200</SelectItem>
                    <SelectItem value="201-1000">201-1000</SelectItem>
                    <SelectItem value="1000+">1000+</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Industries</SelectItem>
                    <SelectItem value="technology">Technology</SelectItem>
                    <SelectItem value="finance">Finance</SelectItem>
                    <SelectItem value="healthcare">Healthcare</SelectItem>
                    <SelectItem value="retail">Retail</SelectItem>
                    <SelectItem value="education">Education</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={source} onValueChange={setSource}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sources</SelectItem>
                    <SelectItem value="website">Website</SelectItem>
                    <SelectItem value="referral">Referral</SelectItem>
                    <SelectItem value="social">Social Media</SelectItem>
                    <SelectItem value="direct">Direct</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Tabs value={view} onValueChange={(v) => setView(v as "kanban" | "list")}>
                <TabsList>
                  <TabsTrigger value="kanban">
                    <Kanban className="h-4 w-4 mr-2" />
                    Kanban
                  </TabsTrigger>
                  <TabsTrigger value="list">
                    <List className="h-4 w-4 mr-2" />
                    List
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            {/* Content */}
            {isLoading ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-muted-foreground">Loading waitlist entries...</div>
              </div>
            ) : view === "kanban" ? (
              <WaitlistKanban
                entries={filteredEntries}
                onUpdateEntry={updateEntry}
                onViewDetails={setSelectedEntry}
                onInvite={setInviteEntry}
              />
            ) : (
              <WaitlistTable
                entries={filteredEntries}
                onViewDetails={setSelectedEntry}
                onInvite={setInviteEntry}
                selectedIds={selectedIds}
                onSelectionChange={setSelectedIds}
              />
            )}
          </div>
        </main>
      </div>

      {/* Modals */}
      {selectedEntry && (
        <WaitlistDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} onUpdate={updateEntry} />
      )}
      {inviteEntry && <InviteModal entry={inviteEntry} onClose={() => setInviteEntry(null)} />}
    </div>
  )
}
