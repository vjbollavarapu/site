"use client"

import { useDroppable } from "@dnd-kit/core"
import { PipelineCard } from "@/components/pipeline-card"
import type { Lead } from "@/types/lead"
import { cn } from "@/lib/utils"

interface PipelineColumnProps {
  id: string
  title: string
  count: number
  leads: Lead[]
  onLeadClick: (id: string) => void
}

export function PipelineColumn({ id, title, count, leads, onLeadClick }: PipelineColumnProps) {
  const { isOver, setNodeRef } = useDroppable({ id })

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "bg-card border border-border rounded-lg p-4 min-h-[600px] transition-colors",
        isOver && "border-primary bg-primary/5",
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-foreground">{title}</h3>
        <span className="text-sm font-medium text-muted-foreground bg-muted px-2 py-1 rounded">{count}</span>
      </div>

      <div className="space-y-2">
        {leads.map((lead) => (
          <PipelineCard key={lead.id} lead={lead} onClick={onLeadClick} />
        ))}
      </div>

      {leads.length === 0 && (
        <div className="text-center py-8 text-sm text-muted-foreground">No leads in this stage</div>
      )}
    </div>
  )
}
