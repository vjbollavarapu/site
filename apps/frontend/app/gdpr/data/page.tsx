"use client"

import { useState } from "react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Download, Trash2, AlertTriangle, CheckCircle2, Info } from "lucide-react"

export default function GDPRDataPage() {
  const [exportEmail, setExportEmail] = useState("")
  const [deleteEmail, setDeleteEmail] = useState("")
  const [deleteConfirmed, setDeleteConfirmed] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [exportSuccess, setExportSuccess] = useState<string | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [downloadLink, setDownloadLink] = useState<string | null>(null)

  const handleExportData = async () => {
    if (!exportEmail) return

    setExportLoading(true)
    setExportSuccess(null)
    setExportError(null)
    setDownloadLink(null)

    try {
      const response = await fetch(`/api/gdpr/export/${encodeURIComponent(exportEmail)}`)
      const data = await response.json()

      if (response.ok) {
        setExportSuccess("Your data export will be emailed to you shortly")
        if (data.downloadUrl) {
          setDownloadLink(data.downloadUrl)
        }
      } else {
        setExportError(data.message || "Failed to export data")
      }
    } catch (error) {
      setExportError("An error occurred while exporting your data")
    } finally {
      setExportLoading(false)
    }
  }

  const handleDeleteConfirmation = () => {
    if (!deleteEmail || !deleteConfirmed) return
    setShowDeleteDialog(true)
  }

  const handleDeleteData = async () => {
    setDeleteLoading(true)
    setDeleteSuccess(null)
    setDeleteError(null)

    try {
      const response = await fetch(`/api/gdpr/delete/${encodeURIComponent(deleteEmail)}?confirmation=true`, {
        method: "DELETE",
      })
      const data = await response.json()

      if (response.ok) {
        setDeleteSuccess("Your data has been successfully deleted")
        setDeleteEmail("")
        setDeleteConfirmed(false)
        setShowDeleteDialog(false)
      } else {
        setDeleteError(data.message || "Failed to delete data")
        setShowDeleteDialog(false)
      }
    } catch (error) {
      setDeleteError("An error occurred while deleting your data")
      setShowDeleteDialog(false)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">GDPR Data Management</h1>
              <p className="text-muted-foreground mt-2">
                Export or delete your personal data in compliance with GDPR regulations
              </p>
            </div>

            <Tabs defaultValue="export" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="export" className="gap-2">
                  <Download className="h-4 w-4" />
                  Export Data
                </TabsTrigger>
                <TabsTrigger value="delete" className="gap-2">
                  <Trash2 className="h-4 w-4" />
                  Delete Data
                </TabsTrigger>
              </TabsList>

              <TabsContent value="export" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Export Your Data</CardTitle>
                    <CardDescription>Request a copy of all your personal data stored in our system</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        We will prepare a comprehensive export of your data including contacts, waitlist entries, leads,
                        newsletter subscriptions, and consent records.
                      </AlertDescription>
                    </Alert>

                    <div className="space-y-2">
                      <Label htmlFor="export-email">Email Address</Label>
                      <Input
                        id="export-email"
                        type="email"
                        placeholder="your@email.com"
                        value={exportEmail}
                        onChange={(e) => setExportEmail(e.target.value)}
                        disabled={exportLoading}
                      />
                    </div>

                    {exportSuccess && (
                      <Alert className="border-green-200 bg-green-50">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <AlertDescription className="text-green-800">{exportSuccess}</AlertDescription>
                      </Alert>
                    )}

                    {downloadLink && (
                      <Alert className="border-blue-200 bg-blue-50">
                        <Download className="h-4 w-4 text-blue-600" />
                        <AlertDescription className="text-blue-800">
                          Your data is ready for download.{" "}
                          <a href={downloadLink} download className="font-semibold underline hover:no-underline">
                            Click here to download
                          </a>
                        </AlertDescription>
                      </Alert>
                    )}

                    {exportError && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{exportError}</AlertDescription>
                      </Alert>
                    )}

                    <Button onClick={handleExportData} disabled={!exportEmail || exportLoading} className="w-full">
                      {exportLoading ? (
                        <>
                          <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                          Preparing Export...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Export My Data
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="delete" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-destructive">Delete Your Data</CardTitle>
                    <CardDescription>Permanently remove all your personal data from our system</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Alert variant="destructive">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Warning:</strong> This action is permanent and cannot be undone. All your data including
                        contacts, waitlist entries, leads, newsletter subscriptions, and consent records will be
                        permanently deleted.
                      </AlertDescription>
                    </Alert>

                    <div className="space-y-2">
                      <Label htmlFor="delete-email">Email Address</Label>
                      <Input
                        id="delete-email"
                        type="email"
                        placeholder="your@email.com"
                        value={deleteEmail}
                        onChange={(e) => setDeleteEmail(e.target.value)}
                        disabled={deleteLoading}
                      />
                    </div>

                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="delete-confirmation"
                        checked={deleteConfirmed}
                        onCheckedChange={(checked) => setDeleteConfirmed(checked as boolean)}
                        disabled={deleteLoading}
                      />
                      <label
                        htmlFor="delete-confirmation"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        I understand this action cannot be undone and all my data will be permanently deleted
                      </label>
                    </div>

                    {deleteSuccess && (
                      <Alert className="border-green-200 bg-green-50">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <AlertDescription className="text-green-800">{deleteSuccess}</AlertDescription>
                      </Alert>
                    )}

                    {deleteError && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{deleteError}</AlertDescription>
                      </Alert>
                    )}

                    <Button
                      onClick={handleDeleteConfirmation}
                      disabled={!deleteEmail || !deleteConfirmed || deleteLoading}
                      variant="destructive"
                      className="w-full"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete My Data
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Confirm Data Deletion
            </DialogTitle>
            <DialogDescription>
              Are you absolutely sure you want to delete all your data? This action cannot be reversed.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              We will permanently delete all data associated with <strong>{deleteEmail}</strong> including:
            </p>
            <ul className="mt-2 text-sm text-muted-foreground list-disc list-inside space-y-1">
              <li>Contact information</li>
              <li>Waitlist entries</li>
              <li>Lead records</li>
              <li>Newsletter subscriptions</li>
              <li>Consent preferences</li>
            </ul>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)} disabled={deleteLoading}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteData} disabled={deleteLoading}>
              {deleteLoading ? (
                <>
                  <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                  Deleting...
                </>
              ) : (
                "Yes, Delete My Data"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
