"use client"

import { useState, useEffect } from "react"
import type { WaitlistEntry } from "@/types/waitlist"
import { getAuthToken } from "@/lib/auth"

interface UseWaitlistParams {
  companySize?: string
  industry?: string
  source?: string
}

export function useWaitlist(params?: UseWaitlistParams) {
  const [entries, setEntries] = useState<WaitlistEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetchEntries()
  }, [params?.companySize, params?.industry, params?.source])

  const fetchEntries = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const queryParams = new URLSearchParams()
      if (params?.companySize) queryParams.append("companySize", params.companySize)
      if (params?.industry) queryParams.append("industry", params.industry)
      if (params?.source) queryParams.append("source", params.source)

      // Get auth token and pass it in headers
      const authToken = getAuthToken()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (authToken) {
        headers['X-Auth-Token'] = authToken
      }

      const response = await fetch(`/api/waitlist/entries?${queryParams.toString()}`, {
        headers,
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.error || `Failed to fetch waitlist entries (${response.status})`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setEntries(data.entries || [])
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error occurred")
      setError(error)
      console.error("[useWaitlist] Error fetching entries:", error.message, err)
    } finally {
      setIsLoading(false)
    }
  }

  const updateEntry = async (id: string, updates: Partial<WaitlistEntry>) => {
    try {
      const response = await fetch(`/api/waitlist/entries/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      })

      if (!response.ok) throw new Error("Failed to update entry")

      const updatedEntry = await response.json()
      setEntries((prev) => prev.map((e) => (e.id === id ? { ...e, ...updatedEntry.entry } : e)))
    } catch (err) {
      console.error("[v0] Error updating entry:", err)
      throw err
    }
  }

  const bulkUpdateStatus = async (ids: string[], status: string) => {
    try {
      const response = await fetch("/api/waitlist/bulk-update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids, status }),
      })

      if (!response.ok) throw new Error("Failed to bulk update entries")

      await fetchEntries()
    } catch (err) {
      console.error("[v0] Error bulk updating entries:", err)
      throw err
    }
  }

  const exportToCSV = () => {
    const headers = [
      "Email",
      "Name",
      "Company",
      "Role",
      "Company Size",
      "Industry",
      "Priority Score",
      "Status",
      "Created At",
    ]
    const rows = entries.map((entry) => [
      entry.email,
      entry.name,
      entry.company,
      entry.role,
      entry.companySize,
      entry.industry,
      entry.priorityScore,
      entry.status,
      new Date(entry.createdAt).toLocaleDateString(),
    ])

    const csvContent = [headers, ...rows].map((row) => row.join(",")).join("\n")
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `waitlist-${new Date().toISOString().split("T")[0]}.csv`
    a.click()
  }

  return {
    entries,
    isLoading,
    error,
    updateEntry,
    bulkUpdateStatus,
    exportToCSV,
    refetch: fetchEntries,
  }
}
