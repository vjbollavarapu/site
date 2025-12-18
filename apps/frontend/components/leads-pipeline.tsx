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
import { PipelineColumn } from "@/components/pipeline-column"
import { PipelineCard } from "@/components/pipeline-card"
import type { Lead } from "@/types/lead"

interface LeadsPipelineProps {
  leads: Lead[]
  isLoading: boolean
  onLeadClick: (id: string) => void
  onUpdateLead: (id: string, updates: Partial<Lead>) => void
}

const stages = [
  { id: "new", label: "New", status: "new" },
  { id: "contacted", label: "Contacted", status: "contacted" },
  { id: "qualified", label: "Qualified", status: "qualified" },
  { id: "converted", label: "Converted", status: "converted" },
]

export function LeadsPipeline({ leads, isLoading, onLeadClick, onUpdateLead }: LeadsPipelineProps) {
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
  )

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (!over) {
      setActiveId(null)
      return
    }

    const leadId = active.id as string
    const newStatus = over.id as string

    if (stages.find((s) => s.status === newStatus)) {
      onUpdateLead(leadId, { status: newStatus as Lead["status"] })
    }

    setActiveId(null)
  }

  const getLeadsByStage = (status: string) => {
    return leads.filter((lead) => lead.status === status)
  }

  const getConversionRate = (fromStage: number, toStage: number) => {
    const fromCount = getLeadsByStage(stages[fromStage].status).length
    const toCount = getLeadsByStage(stages[toStage].status).length

    if (fromCount === 0) return 0
    return Math.round((toCount / fromCount) * 100)
  }

  const activeLead = activeId ? leads.find((l) => l.id === activeId) : null

  if (isLoading) {
    return <div className="text-center py-12 text-muted-foreground">Loading pipeline...</div>
  }

  return (
    <div className="space-y-6">
      {/* Conversion Rate Banner */}
      <div className="grid grid-cols-3 gap-4">
        {[0, 1, 2].map((idx) => (
          <div key={idx} className="bg-card border border-border rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-foreground">{getConversionRate(idx, idx + 1)}%</div>
            <div className="text-sm text-muted-foreground mt-1">
              {stages[idx].label} → {stages[idx + 1].label}
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline Kanban */}
      <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-4 gap-4">
          {stages.map((stage) => {
            const stageLeads = getLeadsByStage(stage.status)
            return (
              <PipelineColumn
                key={stage.id}
                id={stage.status}
                title={stage.label}
                count={stageLeads.length}
                leads={stageLeads}
                onLeadClick={onLeadClick}
              />
            )
          })}
        </div>

        <DragOverlay>
          {activeLead && (
            <div className="opacity-50">
              <PipelineCard lead={activeLead} onClick={() => {}} />
            </div>
          )}
        </DragOverlay>
      </DndContext>
    </div>
  )
}
