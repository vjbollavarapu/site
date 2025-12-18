"use client"

import { useState, useEffect } from "react"
import type { Lead, LeadFilters } from "@/types/lead"
import { getAuthToken } from "@/lib/auth"

export function useLeads(filters: LeadFilters) {
  const [leads, setLeads] = useState<Lead[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchLeads = async () => {
      setIsLoading(true)
      try {
        const queryParams = new URLSearchParams()
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, String(value))
          }
        })

        // Get auth token and pass it in headers
        const authToken = getAuthToken()
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        }
        
        if (authToken) {
          headers['X-Auth-Token'] = authToken
        }

        const response = await fetch(`/api/leads?${queryParams.toString()}`, {
          headers,
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          const errorMessage = errorData.error || `Failed to fetch leads (${response.status})`
          throw new Error(errorMessage)
        }

        const data = await response.json()
        setLeads(Array.isArray(data) ? data : [])
      } catch (error) {
        console.error("[useLeads] Error fetching leads:", error)
        // You might want to add error state here if needed
      } finally {
        setIsLoading(false)
      }
    }

    fetchLeads()
  }, [filters])

  const updateLead = async (id: string, updates: Partial<Lead>) => {
    try {
      const response = await fetch(`/api/leads/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      })
      const updatedLead = await response.json()
      setLeads((prev) => prev.map((l) => (l.id === id ? updatedLead : l)))
    } catch (error) {
      console.error("[v0] Error updating lead:", error)
    }
  }

  const bulkQualify = async (ids: string[]) => {
    try {
      await fetch("/api/leads/bulk-qualify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids }),
      })
      setLeads((prev) => prev.map((l) => (ids.includes(l.id) ? { ...l, status: "qualified" as const } : l)))
    } catch (error) {
      console.error("[v0] Error qualifying leads:", error)
    }
  }

  const bulkConvert = async (ids: string[]) => {
    try {
      await fetch("/api/leads/bulk-convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids }),
      })
      setLeads((prev) => prev.map((l) => (ids.includes(l.id) ? { ...l, status: "converted" as const } : l)))
    } catch (error) {
      console.error("[v0] Error converting leads:", error)
    }
  }

  const exportToCSV = () => {
    const headers = ["Name", "Email", "Company", "Lead Score", "Status", "Lifecycle Stage", "Source", "Created At"]
    const rows = leads.map((lead) => [
      lead.name,
      lead.email,
      lead.company,
      lead.leadScore,
      lead.status,
      lead.lifecycleStage,
      lead.source,
      new Date(lead.createdAt).toLocaleDateString(),
    ])

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `leads-${new Date().toISOString()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    leads,
    isLoading,
    updateLead,
    bulkQualify,
    bulkConvert,
    exportToCSV,
  }
}
