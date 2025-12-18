"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UserPlus, CheckCircle, Target, Send } from "lucide-react"

export function QuickActions() {
  const actions = [
    {
      icon: UserPlus,
      label: "Create Contact",
      description: "Add a new contact to your database",
      action: () => console.log("[v0] Create contact clicked"),
    },
    {
      icon: CheckCircle,
      label: "Approve Waitlist",
      description: "Review and approve pending entries",
      action: () => console.log("[v0] Approve waitlist clicked"),
    },
    {
      icon: Target,
      label: "Qualify Lead",
      description: "Process and qualify new leads",
      action: () => console.log("[v0] Qualify lead clicked"),
    },
    {
      icon: Send,
      label: "Send Newsletter",
      description: "Create and send newsletter campaign",
      action: () => console.log("[v0] Send newsletter clicked"),
    },
  ]

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {actions.map((action) => {
            const Icon = action.icon
            return (
              <Button
                key={action.label}
                variant="outline"
                className="h-auto flex-col items-start gap-2 p-4 border-border hover:bg-accent bg-transparent"
                onClick={action.action}
              >
                <Icon className="h-5 w-5 text-primary" />
                <div className="text-left">
                  <div className="font-medium text-foreground">{action.label}</div>
                  <div className="text-xs text-muted-foreground">{action.description}</div>
                </div>
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
