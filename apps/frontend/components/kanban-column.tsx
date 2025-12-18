"use client"

import { useDroppable } from "@dnd-kit/core"
import { KanbanCard } from "@/components/kanban-card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { WaitlistEntry, WaitlistStatus } from "@/types/waitlist"

interface KanbanColumnProps {
  status: WaitlistStatus
  label: string
  entries: WaitlistEntry[]
  onViewDetails: (entry: WaitlistEntry) => void
  onInvite: (entry: WaitlistEntry) => void
  onUpdateEntry: (id: string, updates: Partial<WaitlistEntry>) => Promise<void>
}

const statusColors: Record<WaitlistStatus, string> = {
  pending: "bg-yellow-500/10 text-yellow-500",
  approved: "bg-green-500/10 text-green-500",
  invited: "bg-blue-500/10 text-blue-500",
  onboarded: "bg-purple-500/10 text-purple-500",
  declined: "bg-red-500/10 text-red-500",
}

export function KanbanColumn({ status, label, entries, onViewDetails, onInvite, onUpdateEntry }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: status,
  })

  return (
    <div className="flex flex-col min-w-[320px] flex-shrink-0">
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-foreground">{label}</h3>
          <Badge variant="secondary" className="rounded-full">
            {entries.length}
          </Badge>
        </div>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          "flex-1 rounded-lg border-2 border-dashed p-2 space-y-2 min-h-[600px] transition-colors",
          isOver ? "border-primary bg-primary/5" : "border-border bg-card/50",
        )}
      >
        {entries.map((entry) => (
          <KanbanCard
            key={entry.id}
            entry={entry}
            onViewDetails={onViewDetails}
            onInvite={onInvite}
            onUpdateEntry={onUpdateEntry}
          />
        ))}
      </div>
    </div>
  )
}
