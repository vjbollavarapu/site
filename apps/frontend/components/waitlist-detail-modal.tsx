"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { Building2, Mail, User, Briefcase, Users, Globe, Calendar, CheckCircle2, Clock, Send } from "lucide-react"
import { cn } from "@/lib/utils"
import type { WaitlistEntry } from "@/types/waitlist"

interface WaitlistDetailModalProps {
  entry: WaitlistEntry
  onClose: () => void
  onUpdate: (id: string, updates: Partial<WaitlistEntry>) => Promise<void>
}

const statusColors = {
  pending: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  approved: "bg-green-500/10 text-green-500 border-green-500/20",
  invited: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  onboarded: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  declined: "bg-red-500/10 text-red-500 border-red-500/20",
}

const getPriorityColor = (score: number) => {
  if (score >= 80) return "text-red-500"
  if (score >= 60) return "text-orange-500"
  if (score >= 40) return "text-yellow-500"
  return "text-green-500"
}

export function WaitlistDetailModal({ entry, onClose, onUpdate }: WaitlistDetailModalProps) {
  const [notes, setNotes] = useState(entry.notes || "")
  const [isSaving, setIsSaving] = useState(false)

  const handleSaveNotes = async () => {
    setIsSaving(true)
    try {
      await onUpdate(entry.id, { notes })
    } finally {
      setIsSaving(false)
    }
  }

  const handleStatusChange = async (status: WaitlistEntry["status"]) => {
    await onUpdate(entry.id, { status })
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Waitlist Entry Details</span>
            <Badge variant="outline" className={cn("capitalize", statusColors[entry.status])}>
              {entry.status}
            </Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Contact Information */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Contact Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Name</div>
                  <div className="font-medium">{entry.name}</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Email</div>
                  <div className="font-medium">{entry.email}</div>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Company Information */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Company Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Company</div>
                  <div className="font-medium">{entry.company}</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Briefcase className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Role</div>
                  <div className="font-medium">{entry.role}</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Users className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Company Size</div>
                  <div className="font-medium">{entry.companySize}</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Globe className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Industry</div>
                  <div className="font-medium capitalize">{entry.industry}</div>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Priority Score */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Priority Score</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Overall Score</span>
                <span className={cn("text-2xl font-bold", getPriorityColor(entry.priorityScore))}>
                  {entry.priorityScore}
                </span>
              </div>
              <Progress value={entry.priorityScore} className="h-2" />
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Company Size</div>
                  <div className="font-medium">{entry.priorityScoreBreakdown?.companySize || 0}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Industry Match</div>
                  <div className="font-medium">{entry.priorityScoreBreakdown?.industryMatch || 0}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Role Fit</div>
                  <div className="font-medium">{entry.priorityScoreBreakdown?.roleFit || 0}</div>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Verification Status */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Verification Status</h3>
            <div className="flex items-center gap-2">
              {entry.verified ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <span className="text-sm font-medium">Email Verified</span>
                </>
              ) : (
                <>
                  <Clock className="h-5 w-5 text-yellow-500" />
                  <span className="text-sm font-medium">Pending Verification</span>
                </>
              )}
            </div>
          </div>

          <Separator />

          {/* Timeline */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Timeline</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="text-sm text-muted-foreground">Created</div>
                  <div className="font-medium">{new Date(entry.createdAt).toLocaleString()}</div>
                </div>
              </div>
              {entry.approvedAt && (
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                  <div>
                    <div className="text-sm text-muted-foreground">Approved</div>
                    <div className="font-medium">{new Date(entry.approvedAt).toLocaleString()}</div>
                  </div>
                </div>
              )}
              {entry.invitedAt && (
                <div className="flex items-start gap-3">
                  <Send className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div>
                    <div className="text-sm text-muted-foreground">Invited</div>
                    <div className="font-medium">{new Date(entry.invitedAt).toLocaleString()}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Notes */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Notes</h3>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this entry..."
              className="min-h-[100px]"
            />
            <Button onClick={handleSaveNotes} disabled={isSaving} className="mt-2 bg-transparent" variant="outline">
              {isSaving ? "Saving..." : "Save Notes"}
            </Button>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            {entry.status === "pending" && (
              <>
                <Button onClick={() => handleStatusChange("approved")} className="flex-1">
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Approve
                </Button>
                <Button onClick={() => handleStatusChange("declined")} variant="destructive" className="flex-1">
                  Decline
                </Button>
              </>
            )}
            {entry.status === "approved" && (
              <Button onClick={() => handleStatusChange("invited")} className="flex-1">
                <Send className="h-4 w-4 mr-2" />
                Mark as Invited
              </Button>
            )}
            {entry.status === "invited" && (
              <Button onClick={() => handleStatusChange("onboarded")} className="flex-1">
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Mark as Onboarded
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
