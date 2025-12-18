"use client"

import { useState } from "react"
import {
  DndContext,
  type DragEndEvent,
  DragOverlay,
  type DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core"
import { KanbanColumn } from "@/components/kanban-column"
import { KanbanCard } from "@/components/kanban-card"
import type { WaitlistEntry, WaitlistStatus } from "@/types/waitlist"

interface WaitlistKanbanProps {
  entries: WaitlistEntry[]
  onUpdateEntry: (id: string, updates: Partial<WaitlistEntry>) => Promise<void>
  onViewDetails: (entry: WaitlistEntry) => void
  onInvite: (entry: WaitlistEntry) => void
}

const STATUSES: { id: WaitlistStatus; label: string }[] = [
  { id: "pending", label: "Pending" },
  { id: "approved", label: "Approved" },
  { id: "invited", label: "Invited" },
  { id: "onboarded", label: "Onboarded" },
  { id: "declined", label: "Declined" },
]

export function WaitlistKanban({ entries, onUpdateEntry, onViewDetails, onInvite }: WaitlistKanbanProps) {
  const [activeEntry, setActiveEntry] = useState<WaitlistEntry | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
  )

  const handleDragStart = (event: DragStartEvent) => {
    const entry = entries.find((e) => e.id === event.active.id)
    if (entry) {
      setActiveEntry(entry)
    }
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      const entryId = active.id as string
      const newStatus = over.id as WaitlistStatus

      await onUpdateEntry(entryId, { status: newStatus })
    }

    setActiveEntry(null)
  }

  const getEntriesByStatus = (status: WaitlistStatus) => {
    return entries.filter((entry) => entry.status === status)
  }

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {STATUSES.map((status) => (
          <KanbanColumn
            key={status.id}
            status={status.id}
            label={status.label}
            entries={getEntriesByStatus(status.id)}
            onViewDetails={onViewDetails}
            onInvite={onInvite}
            onUpdateEntry={onUpdateEntry}
          />
        ))}
      </div>

      <DragOverlay>
        {activeEntry ? (
          <div className="rotate-3 opacity-80">
            <KanbanCard
              entry={activeEntry}
              onViewDetails={() => {}}
              onInvite={() => {}}
              onUpdateEntry={async () => {}}
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
