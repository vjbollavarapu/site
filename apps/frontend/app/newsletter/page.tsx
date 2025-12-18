"use client"

import { useState } from "react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { NewsletterStats } from "@/components/newsletter-stats"
import { SubscribersTable } from "@/components/subscribers-table"
import { SubscriberDetailModal } from "@/components/subscriber-detail-modal"
import { ImportSubscribersModal } from "@/components/import-subscribers-modal"
import { useSubscribers } from "@/hooks/use-subscribers"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Download, Upload, Search, Send } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "@/hooks/use-toast"
import type { Subscriber } from "@/types/subscriber"

export default function NewsletterPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [sourceFilter, setSourceFilter] = useState<string>("all")
  const [verifiedFilter, setVerifiedFilter] = useState<string>("all")
  const [selectedSubscriber, setSelectedSubscriber] = useState<Subscriber | null>(null)
  const [isImportModalOpen, setIsImportModalOpen] = useState(false)
  const [selectedIds, setSelectedIds] = useState<string[]>([])

  const { subscribers, isLoading, exportSubscribers, unsubscribeBulk, sendTestEmail } = useSubscribers({
    search: searchQuery,
    status: statusFilter !== "all" ? statusFilter : undefined,
    source: sourceFilter !== "all" ? sourceFilter : undefined,
    verified: verifiedFilter !== "all" ? verifiedFilter === "verified" : undefined,
  })

  const handleExport = async () => {
    const success = await exportSubscribers()
    if (success) {
      toast({
        title: "Export successful",
        description: "Subscribers list has been exported to CSV",
      })
    }
  }

  const handleBulkUnsubscribe = async () => {
    if (selectedIds.length === 0) return
    const success = await unsubscribeBulk(selectedIds)
    if (success) {
      toast({
        title: "Unsubscribed",
        description: `${selectedIds.length} subscriber(s) have been unsubscribed`,
      })
      setSelectedIds([])
    }
  }

  const handleSendTest = async () => {
    const success = await sendTestEmail()
    if (success) {
      toast({
        title: "Test email sent",
        description: "Check your inbox for the test email",
      })
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-[1600px] mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Newsletter Subscribers</h1>
                <p className="text-muted-foreground mt-1">Manage your newsletter subscriber list</p>
              </div>
              <div className="flex items-center gap-2">
                <Button onClick={handleSendTest} variant="outline" size="sm">
                  <Send className="h-4 w-4 mr-2" />
                  Send Test
                </Button>
                <Button onClick={() => setIsImportModalOpen(true)} variant="outline" size="sm">
                  <Upload className="h-4 w-4 mr-2" />
                  Import
                </Button>
                <Button onClick={handleExport} variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </div>

            {/* Stats */}
            <NewsletterStats />

            {/* Filters */}
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search by email or name..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="subscribed">Subscribed</SelectItem>
                    <SelectItem value="unsubscribed">Unsubscribed</SelectItem>
                    <SelectItem value="bounced">Bounced</SelectItem>
                    <SelectItem value="complained">Complained</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={sourceFilter} onValueChange={setSourceFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sources</SelectItem>
                    <SelectItem value="website">Website</SelectItem>
                    <SelectItem value="landing-page">Landing Page</SelectItem>
                    <SelectItem value="imported">Imported</SelectItem>
                    <SelectItem value="api">API</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={verifiedFilter} onValueChange={setVerifiedFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Verification" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="verified">Verified</SelectItem>
                    <SelectItem value="unverified">Unverified</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Bulk Actions */}
              {selectedIds.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{selectedIds.length} subscriber(s) selected</span>
                  <Button onClick={handleBulkUnsubscribe} variant="destructive" size="sm">
                    Unsubscribe Selected
                  </Button>
                </div>
              )}
            </div>

            {/* Table */}
            <SubscribersTable
              subscribers={subscribers}
              isLoading={isLoading}
              selectedIds={selectedIds}
              onSelectionChange={setSelectedIds}
              onViewDetails={setSelectedSubscriber}
            />
          </div>
        </main>
      </div>

      {/* Modals */}
      {selectedSubscriber && (
        <SubscriberDetailModal
          subscriber={selectedSubscriber}
          open={!!selectedSubscriber}
          onOpenChange={(open) => !open && setSelectedSubscriber(null)}
        />
      )}
      <ImportSubscribersModal open={isImportModalOpen} onOpenChange={setIsImportModalOpen} />
    </div>
  )
}
