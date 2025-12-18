"use client"

import { useDraggable } from "@dnd-kit/core"
import { Badge } from "@/components/ui/badge"
import { Building2, Mail, TrendingUp } from "lucide-react"
import type { Lead } from "@/types/lead"
import { cn } from "@/lib/utils"

interface PipelineCardProps {
  lead: Lead
  onClick: (id: string) => void
}

export function PipelineCard({ lead, onClick }: PipelineCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: lead.id,
  })

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined

  const getScoreColor = (score: number) => {
    if (score <= 30) return "text-red-500 bg-red-500/10"
    if (score <= 60) return "text-yellow-500 bg-yellow-500/10"
    return "text-green-500 bg-green-500/10"
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      onClick={(e) => {
        e.stopPropagation()
        onClick(lead.id)
      }}
      className={cn(
        "bg-background border border-border rounded-lg p-3 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow",
        isDragging && "opacity-50",
      )}
    >
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <div className="font-medium text-sm text-foreground truncate flex-1">{lead.name}</div>
          <Badge variant="secondary" className={cn("text-xs font-semibold ml-2", getScoreColor(lead.leadScore))}>
            {lead.leadScore}
          </Badge>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Building2 className="h-3 w-3" />
          <span className="truncate">{lead.company}</span>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Mail className="h-3 w-3" />
          <span className="truncate">{lead.email}</span>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-border">
          <Badge variant="outline" className="text-xs">
            {lead.lifecycleStage}
          </Badge>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <TrendingUp className="h-3 w-3" />
            <span>{lead.source}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
