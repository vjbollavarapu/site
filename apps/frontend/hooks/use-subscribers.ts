"use client"

import { useState, useEffect } from "react"
import useSWR, { mutate } from "swr"
import type { Subscriber, SubscriberStats } from "@/types/subscriber"
import { getAuthToken } from "@/lib/auth"

const fetcher = (url: string) => {
  const token = getAuthToken()
  return fetch(url, {
    headers: {
      ...(token ? { 'X-Auth-Token': token } : {}),
    },
  }).then((res) => {
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    return res.json()
  })
}

interface UseSubscribersProps {
  search?: string
  status?: string
  source?: string
  verified?: boolean
}

export function useSubscribers(filters: UseSubscribersProps) {
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search || "")

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(filters.search || "")
    }, 300)
    return () => clearTimeout(timer)
  }, [filters.search])

  const queryParams = new URLSearchParams()
  if (debouncedSearch) queryParams.append("search", debouncedSearch)
  if (filters.status) queryParams.append("status", filters.status)
  if (filters.source) queryParams.append("source", filters.source)
  if (filters.verified !== undefined) queryParams.append("verified", String(filters.verified))

  const { data, error, isLoading } = useSWR<Subscriber[]>(
    `/api/newsletter/subscribers?${queryParams.toString()}`,
    fetcher,
  )

  const exportSubscribers = async () => {
    try {
      const token = getAuthToken()
      const response = await fetch("/api/newsletter/export", {
        headers: {
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
      })
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`)
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "newsletter_subscribers.csv"
      a.click()
      window.URL.revokeObjectURL(url)
      return true
    } catch (error) {
      console.error("Export failed:", error)
      return false
    }
  }

  const importSubscribers = async (file: File) => {
    try {
      const token = getAuthToken()
      const formData = new FormData()
      formData.append("file", file)
      const response = await fetch("/api/newsletter/import", {
        method: "POST",
        headers: {
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
        body: formData,
      })
      if (response.ok) {
        mutate(`/api/newsletter/subscribers?${queryParams.toString()}`)
        return true
      }
      const errorData = await response.json().catch(() => ({}))
      console.error("Import failed:", errorData.error || response.statusText)
      return false
    } catch (error) {
      console.error("Import failed:", error)
      return false
    }
  }

  const unsubscribe = async (id: string) => {
    try {
      const token = getAuthToken()
      const response = await fetch(`/api/newsletter/subscribers/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
        body: JSON.stringify({ subscription_status: "unsubscribed" }),
      })
      if (response.ok) {
        mutate(`/api/newsletter/subscribers?${queryParams.toString()}`)
        return true
      }
      const errorData = await response.json().catch(() => ({}))
      console.error("Unsubscribe failed:", errorData.error || response.statusText)
      return false
    } catch (error) {
      console.error("Unsubscribe failed:", error)
      return false
    }
  }

  const unsubscribeBulk = async (ids: string[]) => {
    try {
      const token = getAuthToken()
      const response = await fetch("/api/newsletter/unsubscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
        body: JSON.stringify({ ids }),
      })
      if (response.ok) {
        mutate(`/api/newsletter/subscribers?${queryParams.toString()}`)
        return true
      }
      const errorData = await response.json().catch(() => ({}))
      console.error("Bulk unsubscribe failed:", errorData.error || response.statusText)
      return false
    } catch (error) {
      console.error("Bulk unsubscribe failed:", error)
      return false
    }
  }

  const deleteSubscriber = async (id: string) => {
    try {
      const token = getAuthToken()
      const response = await fetch(`/api/newsletter/subscribers/${id}`, {
        method: "DELETE",
        headers: {
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
      })
      if (response.ok) {
        mutate(`/api/newsletter/subscribers?${queryParams.toString()}`)
        return true
      }
      const errorData = await response.json().catch(() => ({}))
      console.error("Delete failed:", errorData.error || response.statusText)
      return false
    } catch (error) {
      console.error("Delete failed:", error)
      return false
    }
  }

  const resendVerification = async (id: string) => {
    try {
      const token = getAuthToken()
      const response = await fetch(`/api/newsletter/subscribers/${id}/verify`, {
        method: "POST",
        headers: {
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error("Resend verification failed:", errorData.error || response.statusText)
      }
      return response.ok
    } catch (error) {
      console.error("Resend verification failed:", error)
      return false
    }
  }

  const sendTestEmail = async () => {
    try {
      const token = getAuthToken()
      const response = await fetch("/api/newsletter/test", {
        method: "POST",
        headers: {
          ...(token ? { 'X-Auth-Token': token } : {}),
        },
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error("Send test email failed:", errorData.error || response.statusText)
      }
      return response.ok
    } catch (error) {
      console.error("Send test email failed:", error)
      return false
    }
  }

  return {
    subscribers: data || [],
    isLoading,
    error,
    exportSubscribers,
    importSubscribers,
    unsubscribe,
    unsubscribeBulk,
    deleteSubscriber,
    resendVerification,
    sendTestEmail,
  }
}

export function useSubscriberStats() {
  const { data, error, isLoading } = useSWR<SubscriberStats>("/api/newsletter/stats", fetcher)

  return {
    stats: data || {
      totalSubscribers: 0,
      activeSubscribers: 0,
      unsubscribed30d: 0,
      bounced: 0,
      growthRate: 0,
    },
    isLoading,
    error,
  }
}
