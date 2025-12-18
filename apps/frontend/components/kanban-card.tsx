"use client"

import { useDraggable } from "@dnd-kit/core"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Building2, CheckCircle2, XCircle, Mail, MoreVertical, Eye } from "lucide-react"
import { cn } from "@/lib/utils"
import type { WaitlistEntry } from "@/types/waitlist"

interface KanbanCardProps {
  entry: WaitlistEntry
  onViewDetails: (entry: WaitlistEntry) => void
  onInvite: (entry: WaitlistEntry) => void
  onUpdateEntry: (id: string, updates: Partial<WaitlistEntry>) => Promise<void>
}

const getPriorityColor = (score: number) => {
  if (score >= 80) return "text-red-500"
  if (score >= 60) return "text-orange-500"
  if (score >= 40) return "text-yellow-500"
  return "text-green-500"
}

const getPriorityLabel = (score: number) => {
  if (score >= 80) return "Critical"
  if (score >= 60) return "High"
  if (score >= 40) return "Medium"
  return "Low"
}

export function KanbanCard({ entry, onViewDetails, onInvite, onUpdateEntry }: KanbanCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: entry.id,
  })

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={cn(
        "bg-card border border-border rounded-lg p-4 space-y-3 cursor-grab active:cursor-grabbing transition-all hover:shadow-lg",
        isDragging && "opacity-50",
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-foreground truncate">{entry.name}</h4>
          <p className="text-sm text-muted-foreground truncate">{entry.email}</p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onViewDetails(entry)}>
              <Eye className="h-4 w-4 mr-2" />
              View Details
            </DropdownMenuItem>
            {entry.status === "approved" && (
              <DropdownMenuItem onClick={() => onInvite(entry)}>
                <Mail className="h-4 w-4 mr-2" />
                Send Invite
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={() => onUpdateEntry(entry.id, { status: "approved" })}>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Approve
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onUpdateEntry(entry.id, { status: "declined" })}>
              <XCircle className="h-4 w-4 mr-2" />
              Decline
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Company */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Building2 className="h-4 w-4" />
        <span className="truncate">{entry.company}</span>
      </div>

      {/* Priority Score */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Priority Score</span>
          <span className={cn("font-semibold", getPriorityColor(entry.priorityScore))}>{entry.priorityScore}</span>
        </div>
        <Progress value={entry.priorityScore} className="h-1.5" />
        <div className="flex items-center justify-between">
          <Badge variant="outline" className={getPriorityColor(entry.priorityScore)}>
            {getPriorityLabel(entry.priorityScore)}
          </Badge>
          <span className="text-xs text-muted-foreground">{new Date(entry.createdAt).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-2 pt-2 border-t border-border">
        {entry.status === "pending" && (
          <>
            <Button
              size="sm"
              variant="outline"
              className="flex-1 bg-transparent"
              onClick={() => onUpdateEntry(entry.id, { status: "approved" })}
            >
              <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
              Approve
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="flex-1 bg-transparent"
              onClick={() => onUpdateEntry(entry.id, { status: "declined" })}
            >
              <XCircle className="h-3.5 w-3.5 mr-1" />
              Decline
            </Button>
          </>
        )}
        {entry.status === "approved" && (
          <Button size="sm" variant="outline" className="flex-1 bg-transparent" onClick={() => onInvite(entry)}>
            <Mail className="h-3.5 w-3.5 mr-1" />
            Send Invite
          </Button>
        )}
      </div>
    </div>
  )
}
