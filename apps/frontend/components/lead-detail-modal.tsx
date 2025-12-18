"use client"

import { useEffect, useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  Calendar,
  User,
  TrendingUp,
  CheckCircle,
  Clock,
  MessageSquare,
  Plus,
} from "lucide-react"
import { Progress } from "@/components/ui/progress"
import type { Lead } from "@/types/lead"

interface LeadDetailModalProps {
  leadId: string
  onClose: () => void
}

export function LeadDetailModal({ leadId, onClose }: LeadDetailModalProps) {
  const [lead, setLead] = useState<Lead | null>(null)
  const [newNote, setNewNote] = useState("")
  const [newEvent, setNewEvent] = useState("")

  useEffect(() => {
    // Fetch lead details
    fetch(`/api/leads/${leadId}`)
      .then((res) => res.json())
      .then((data) => setLead(data))
      .catch((err) => console.error("[v0] Error fetching lead:", err))
  }, [leadId])

  const handleAddNote = () => {
    if (!newNote.trim()) return
    console.log("[v0] Adding note:", newNote)
    setNewNote("")
  }

  const handleAddEvent = () => {
    if (!newEvent.trim()) return
    console.log("[v0] Tracking event:", newEvent)
    setNewEvent("")
  }

  if (!lead) {
    return (
      <Dialog open onOpenChange={onClose}>
        <DialogContent className="max-w-4xl">
          <div className="text-center py-8">Loading...</div>
        </DialogContent>
      </Dialog>
    )
  }

  const getScoreColor = (score: number) => {
    if (score <= 30) return "text-red-500 bg-red-500"
    if (score <= 60) return "text-yellow-500 bg-yellow-500"
    return "text-green-500 bg-green-500"
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>{lead.name}</span>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline">
                <CheckCircle className="h-4 w-4 mr-2" />
                Qualify
              </Button>
              <Button size="sm">
                <TrendingUp className="h-4 w-4 mr-2" />
                Convert
              </Button>
            </div>
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[70vh]">
          <div className="space-y-6">
            {/* Lead Score */}
            <div className="bg-muted/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Lead Score</span>
                <span className={`text-2xl font-bold ${getScoreColor(lead.leadScore).split(" ")[0]}`}>
                  {lead.leadScore}
                </span>
              </div>
              <Progress
                value={lead.leadScore}
                className="h-2"
                indicatorClassName={getScoreColor(lead.leadScore).split(" ")[1]}
              />
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Engagement:</span>
                  <span className="font-medium">25/30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Fit:</span>
                  <span className="font-medium">20/30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Intent:</span>
                  <span className="font-medium">15/20</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Demographics:</span>
                  <span className="font-medium">15/20</span>
                </div>
              </div>
            </div>

            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{lead.email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{lead.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span>{lead.company}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span>{lead.location}</span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Status:</span>
                  <Badge>{lead.status}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Lifecycle:</span>
                  <Badge variant="outline">{lead.lifecycleStage}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Source:</span>
                  <span className="text-sm">{lead.source}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Assigned to:</span>
                  <span className="text-sm">{lead.assignedTo || "Unassigned"}</span>
                </div>
              </div>
            </div>

            <Separator />

            <Tabs defaultValue="timeline">
              <TabsList>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
                <TabsTrigger value="notes">Notes</TabsTrigger>
                <TabsTrigger value="events">Events</TabsTrigger>
              </TabsList>

              <TabsContent value="timeline" className="space-y-4 mt-4">
                <div className="space-y-3">
                  {lead.timeline?.map((item, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                          {item.type === "note" ? (
                            <MessageSquare className="h-4 w-4 text-primary" />
                          ) : item.type === "event" ? (
                            <CheckCircle className="h-4 w-4 text-primary" />
                          ) : (
                            <Clock className="h-4 w-4 text-primary" />
                          )}
                        </div>
                        {idx < lead.timeline!.length - 1 && <div className="w-px h-full bg-border mt-1" />}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="text-sm font-medium">{item.title}</div>
                        <div className="text-xs text-muted-foreground mt-1">{new Date(item.date).toLocaleString()}</div>
                        {item.description && (
                          <div className="text-sm text-muted-foreground mt-2">{item.description}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="notes" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Add Note</Label>
                  <Textarea
                    placeholder="Enter your note..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    rows={3}
                  />
                  <Button size="sm" onClick={handleAddNote}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Note
                  </Button>
                </div>
                <Separator />
                <div className="space-y-3">
                  {lead.notes?.map((note, idx) => (
                    <div key={idx} className="bg-muted/50 rounded-lg p-3">
                      <div className="text-sm">{note.content}</div>
                      <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                        <User className="h-3 w-3" />
                        <span>{note.author}</span>
                        <span>•</span>
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(note.date).toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="events" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Track Event</Label>
                  <Input
                    placeholder="Event name (e.g., Downloaded whitepaper)"
                    value={newEvent}
                    onChange={(e) => setNewEvent(e.target.value)}
                  />
                  <Button size="sm" onClick={handleAddEvent}>
                    <Plus className="h-4 w-4 mr-2" />
                    Track Event
                  </Button>
                </div>
                <Separator />
                <div className="space-y-2">
                  {lead.events?.map((event, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm">
                      <span>{event.name}</span>
                      <span className="text-xs text-muted-foreground">{new Date(event.date).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
