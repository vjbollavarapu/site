"use client"

import { useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { CheckCircle2, Clock, Mail, MessageSquare, X } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Contact } from "@/types/contact"

interface ContactDetailModalProps {
  contact: Contact | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpdate: (id: string, updates: Partial<Contact>) => Promise<void>
}

const statusColors = {
  new: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  contacted: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  resolved: "bg-green-500/10 text-green-500 border-green-500/20",
  archived: "bg-gray-500/10 text-gray-500 border-gray-500/20",
}

const priorityColors = {
  low: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  medium: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  urgent: "bg-red-500/10 text-red-500 border-red-500/20",
}

export function ContactDetailModal({ contact, open, onOpenChange, onUpdate }: ContactDetailModalProps) {
  const [note, setNote] = useState("")
  const [isUpdating, setIsUpdating] = useState(false)

  if (!contact) return null

  const handleStatusUpdate = async (status: string) => {
    setIsUpdating(true)
    await onUpdate(contact.id, { status })
    setIsUpdating(false)
  }

  const handlePriorityUpdate = async (priority: string) => {
    setIsUpdating(true)
    await onUpdate(contact.id, { priority })
    setIsUpdating(false)
  }

  const handleAddNote = async () => {
    if (!note.trim()) return
    setIsUpdating(true)
    const newActivity = {
      id: Date.now().toString(),
      type: "note",
      message: note,
      timestamp: new Date().toISOString(),
      user: "Current User",
    }
    await onUpdate(contact.id, {
      activity: [...(contact.activity || []), newActivity],
    })
    setNote("")
    setIsUpdating(false)
  }

  const initials = contact.name
    .split(" ")
    .map((n) => n[0])
    .join("")

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div>
              <div className="font-semibold">{contact.name}</div>
              <div className="text-sm text-muted-foreground font-normal">{contact.email}</div>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Contact Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Company</label>
              <p className="mt-1">{contact.company || "N/A"}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Created</label>
              <p className="mt-1">{formatDistanceToNow(new Date(contact.createdAt), { addSuffix: true })}</p>
            </div>
          </div>

          {/* Status and Priority */}
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium text-muted-foreground mb-2 block">Status</label>
              <Select value={contact.status} onValueChange={handleStatusUpdate} disabled={isUpdating}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="contacted">Contacted</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="archived">Archived</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-muted-foreground mb-2 block">Priority</label>
              <Select value={contact.priority} onValueChange={handlePriorityUpdate} disabled={isUpdating}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          {/* Message */}
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Message
            </label>
            <div className="bg-muted/50 p-4 rounded-lg border border-border">
              <p className="text-sm font-medium mb-2">{contact.subject}</p>
              <p className="text-sm text-muted-foreground">{contact.message}</p>
            </div>
          </div>

          <Separator />

          {/* Quick Actions */}
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-3 block">Quick Actions</label>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => handleStatusUpdate("contacted")} disabled={isUpdating}>
                <Mail className="mr-2 h-4 w-4" />
                Mark as Contacted
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleStatusUpdate("resolved")} disabled={isUpdating}>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Resolve
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleStatusUpdate("archived")} disabled={isUpdating}>
                <X className="mr-2 h-4 w-4" />
                Archive
              </Button>
            </div>
          </div>

          <Separator />

          {/* Notes Section */}
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-3 block">Add Note</label>
            <div className="flex gap-2">
              <Textarea
                placeholder="Add a note or comment..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                className="flex-1"
              />
            </div>
            <Button onClick={handleAddNote} disabled={!note.trim() || isUpdating} size="sm" className="mt-2">
              Add Note
            </Button>
          </div>

          {/* Activity Log */}
          {contact.activity && contact.activity.length > 0 && (
            <>
              <Separator />
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Activity Log
                </label>
                <div className="space-y-3">
                  {contact.activity.map((activity) => (
                    <div key={activity.id} className="flex gap-3 text-sm">
                      <div className="flex-shrink-0 w-2 h-2 mt-1.5 rounded-full bg-primary" />
                      <div className="flex-1">
                        <p className="text-foreground">{activity.message}</p>
                        <p className="text-muted-foreground text-xs mt-1">
                          {activity.user} • {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
