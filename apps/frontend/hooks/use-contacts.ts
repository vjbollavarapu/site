"use client"

import { useState, useEffect } from "react"
import type { Contact } from "@/types/contact"
import { getAuthToken } from "@/lib/auth"

interface UseContactsParams {
  status?: string
  priority?: string
}

export function useContacts(params?: UseContactsParams) {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetchContacts()
  }, [params?.status, params?.priority])

  const fetchContacts = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const queryParams = new URLSearchParams()
      if (params?.status) queryParams.append("status", params.status)
      if (params?.priority) queryParams.append("priority", params.priority)

      // Get auth token and pass it in headers
      const authToken = getAuthToken()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (authToken) {
        headers['X-Auth-Token'] = authToken
      }

      const response = await fetch(`/api/contacts?${queryParams.toString()}`, {
        headers,
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.error || `Failed to fetch contacts (${response.status})`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setContacts(data.contacts || [])
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error occurred")
      setError(error)
      console.error("[useContacts] Error fetching contacts:", error.message, err)
    } finally {
      setIsLoading(false)
    }
  }

  const updateContact = async (id: string, updates: Partial<Contact>) => {
    try {
      const response = await fetch(`/api/contacts/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      })

      if (!response.ok) throw new Error("Failed to update contact")

      const updatedContact = await response.json()
      setContacts((prev) => prev.map((c) => (c.id === id ? { ...c, ...updatedContact } : c)))
    } catch (err) {
      console.error("[v0] Error updating contact:", err)
      throw err
    }
  }

  const deleteContact = async (id: string) => {
    try {
      const response = await fetch(`/api/contacts/${id}`, {
        method: "DELETE",
      })

      if (!response.ok) throw new Error("Failed to delete contact")

      setContacts((prev) => prev.filter((c) => c.id !== id))
    } catch (err) {
      console.error("[v0] Error deleting contact:", err)
      throw err
    }
  }

  const bulkUpdateStatus = async (ids: string[], status: string) => {
    try {
      const response = await fetch("/api/contacts/bulk-update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids, status }),
      })

      if (!response.ok) throw new Error("Failed to bulk update contacts")

      setContacts((prev) => prev.map((c) => (ids.includes(c.id) ? { ...c, status } : c)))
    } catch (err) {
      console.error("[v0] Error bulk updating contacts:", err)
      throw err
    }
  }

  return {
    contacts,
    isLoading,
    error,
    updateContact,
    deleteContact,
    bulkUpdateStatus,
    refetch: fetchContacts,
  }
}
