"use client"

import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"
import type { LeadFilters } from "@/types/lead"

interface LeadsFiltersProps {
  filters: LeadFilters
  onFiltersChange: (filters: LeadFilters) => void
}

export function LeadsFilters({ filters, onFiltersChange }: LeadsFiltersProps) {
  const updateFilter = (key: keyof LeadFilters, value: any) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  const clearFilters = () => {
    onFiltersChange({})
  }

  const hasFilters = Object.keys(filters).length > 0

  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-foreground">Filters</h3>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label>Search</Label>
          <Input
            placeholder="Search leads..."
            value={filters.search || ""}
            onChange={(e) => updateFilter("search", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label>Status</Label>
          <Select
            value={filters.status || "all"}
            onValueChange={(v) => updateFilter("status", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="contacted">Contacted</SelectItem>
              <SelectItem value="qualified">Qualified</SelectItem>
              <SelectItem value="unqualified">Unqualified</SelectItem>
              <SelectItem value="converted">Converted</SelectItem>
              <SelectItem value="lost">Lost</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Lifecycle Stage</Label>
          <Select
            value={filters.lifecycleStage || "all"}
            onValueChange={(v) => updateFilter("lifecycleStage", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All stages" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All stages</SelectItem>
              <SelectItem value="subscriber">Subscriber</SelectItem>
              <SelectItem value="lead">Lead</SelectItem>
              <SelectItem value="marketing-qualified">Marketing Qualified</SelectItem>
              <SelectItem value="sales-qualified">Sales Qualified</SelectItem>
              <SelectItem value="opportunity">Opportunity</SelectItem>
              <SelectItem value="customer">Customer</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Source</Label>
          <Select
            value={filters.source || "all"}
            onValueChange={(v) => updateFilter("source", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All sources" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All sources</SelectItem>
              <SelectItem value="Website">Website</SelectItem>
              <SelectItem value="Referral">Referral</SelectItem>
              <SelectItem value="LinkedIn">LinkedIn</SelectItem>
              <SelectItem value="Email Campaign">Email Campaign</SelectItem>
              <SelectItem value="Trade Show">Trade Show</SelectItem>
              <SelectItem value="Cold Call">Cold Call</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Industry</Label>
          <Select
            value={filters.industry || "all"}
            onValueChange={(v) => updateFilter("industry", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All industries" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All industries</SelectItem>
              <SelectItem value="Technology">Technology</SelectItem>
              <SelectItem value="Healthcare">Healthcare</SelectItem>
              <SelectItem value="Finance">Finance</SelectItem>
              <SelectItem value="Retail">Retail</SelectItem>
              <SelectItem value="Manufacturing">Manufacturing</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Company Size</Label>
          <Select
            value={filters.companySize || "all"}
            onValueChange={(v) => updateFilter("companySize", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All sizes" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All sizes</SelectItem>
              <SelectItem value="1-10">1-10</SelectItem>
              <SelectItem value="11-50">11-50</SelectItem>
              <SelectItem value="51-200">51-200</SelectItem>
              <SelectItem value="201-500">201-500</SelectItem>
              <SelectItem value="501+">501+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Assigned To</Label>
          <Select
            value={filters.assignedTo || "all"}
            onValueChange={(v) => updateFilter("assignedTo", v === "all" ? undefined : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All users" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All users</SelectItem>
              <SelectItem value="John Smith">John Smith</SelectItem>
              <SelectItem value="Sarah Johnson">Sarah Johnson</SelectItem>
              <SelectItem value="Mike Davis">Mike Davis</SelectItem>
              <SelectItem value="Unassigned">Unassigned</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>
            Lead Score Range: {filters.scoreMin || 0} - {filters.scoreMax || 100}
          </Label>
          <div className="pt-2">
            <Slider
              min={0}
              max={100}
              step={5}
              value={[filters.scoreMin || 0, filters.scoreMax || 100]}
              onValueChange={([min, max]) => {
                updateFilter("scoreMin", min)
                updateFilter("scoreMax", max)
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
