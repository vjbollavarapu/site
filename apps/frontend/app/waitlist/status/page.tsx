"use client"

import type React from "react"

import { useState } from "react"
import { XCircle, Clock, Mail, Loader2, Trophy, Send, UserCheck } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface WaitlistStatusData {
  email: string
  name: string
  status: "pending" | "approved" | "invited" | "onboarded" | "declined"
  priorityScore: number
  position?: number
  createdAt: string
  verified: boolean
}

const statusMessages = {
  pending: {
    title: "You're on the waitlist!",
    message: "We'll notify you soon.",
    icon: Clock,
    variant: "default" as const,
    color: "text-blue-500",
  },
  approved: {
    title: "Congratulations!",
    message: "You've been approved.",
    icon: Trophy,
    variant: "default" as const,
    color: "text-green-500",
  },
  invited: {
    title: "Check your email!",
    message: "Your invitation has been sent.",
    icon: Send,
    variant: "default" as const,
    color: "text-purple-500",
  },
  onboarded: {
    title: "Welcome!",
    message: "You're all set.",
    icon: UserCheck,
    variant: "default" as const,
    color: "text-emerald-500",
  },
  declined: {
    title: "Application Declined",
    message: "Unfortunately, your application was declined.",
    icon: XCircle,
    variant: "destructive" as const,
    color: "text-red-500",
  },
}

export default function WaitlistStatusPage() {
  const [email, setEmail] = useState("")
  const [status, setStatus] = useState<WaitlistStatusData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    setSubmitted(true)

    try {
      const response = await fetch(`/api/waitlist/status/${encodeURIComponent(email)}`)

      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      } else if (response.status === 404) {
        setError("Email not found on the waitlist.")
      } else {
        setError("Failed to check status. Please try again.")
      }
    } catch (error) {
      console.error("[v0] Status check error:", error)
      setError("An error occurred. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmail("")
    setStatus(null)
    setError("")
    setSubmitted(false)
  }

  if (submitted && !loading && status) {
    const statusConfig = statusMessages[status.status]
    const StatusIcon = statusConfig.icon

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-lg">
          <CardHeader className="text-center">
            <div
              className={`mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full ${status.status === "declined" ? "bg-red-500/10" : "bg-primary/10"}`}
            >
              <StatusIcon className={`h-8 w-8 ${statusConfig.color}`} />
            </div>
            <CardTitle className="text-2xl">{statusConfig.title}</CardTitle>
            <CardDescription className="text-base">{statusConfig.message}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Email Display */}
            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">{status.email}</span>
              </div>
              <Badge variant={status.verified ? "default" : "secondary"}>
                {status.verified ? "Verified" : "Pending"}
              </Badge>
            </div>

            {/* Status Details */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-muted/50 rounded-lg text-center">
                <div className="text-2xl font-bold text-primary">{status.priorityScore}</div>
                <p className="text-xs text-muted-foreground mt-1">Priority Score</p>
              </div>
              {status.position && (
                <div className="p-4 bg-muted/50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-primary">#{status.position}</div>
                  <p className="text-xs text-muted-foreground mt-1">Position</p>
                </div>
              )}
              {!status.position && (
                <div className="p-4 bg-muted/50 rounded-lg text-center">
                  <div className="text-sm font-medium capitalize">{status.status}</div>
                  <p className="text-xs text-muted-foreground mt-1">Current Status</p>
                </div>
              )}
            </div>

            {/* Additional Info */}
            <div className="p-4 bg-muted/50 border border-border rounded-lg">
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Joined:</span>{" "}
                {new Date(status.createdAt).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>

            {/* Check Another Email Button */}
            <Button onClick={resetForm} variant="outline" className="w-full bg-transparent">
              Check Another Email
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Check Waitlist Status</CardTitle>
          <CardDescription>Enter your email to view your current waitlist status</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking Status...
                </>
              ) : (
                "Check Status"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
