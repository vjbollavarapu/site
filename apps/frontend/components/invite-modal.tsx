"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Mail } from "lucide-react"
import type { WaitlistEntry } from "@/types/waitlist"

interface InviteModalProps {
  entry: WaitlistEntry
  onClose: () => void
}

export function InviteModal({ entry, onClose }: InviteModalProps) {
  const [subject, setSubject] = useState(`Welcome to the Platform, ${entry.name.split(" ")[0]}!`)
  const [message, setMessage] = useState(
    `Hi ${entry.name.split(" ")[0]},\n\nWe're excited to welcome you to our platform! Your waitlist application has been approved.\n\nYour unique invitation link: [INVITATION_LINK]\n\nClick the link above to get started.\n\nBest regards,\nThe Team`,
  )
  const [isSending, setIsSending] = useState(false)

  const handleSend = async () => {
    setIsSending(true)
    try {
      // Simulate sending email
      await new Promise((resolve) => setTimeout(resolve, 1500))
      onClose()
    } finally {
      setIsSending(false)
    }
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Send Invitation Email
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label htmlFor="to">To</Label>
            <Input id="to" value={`${entry.name} <${entry.email}>`} disabled />
          </div>

          <div>
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Email subject"
            />
          </div>

          <div>
            <Label htmlFor="message">Message</Label>
            <Textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Email message"
              className="min-h-[250px] font-mono text-sm"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSending}>
            Cancel
          </Button>
          <Button onClick={handleSend} disabled={isSending}>
            {isSending ? "Sending..." : "Send Invitation"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
