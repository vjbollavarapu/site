"use client"

import type React from "react"

import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import {
  Circle,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  Send,
  UserCheck,
  Archive,
  Phone,
  ThumbsUp,
  ThumbsDown,
  Mail,
  MailWarning,
  AlertTriangle,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"

// Contact Status Types
type ContactStatus = "new" | "contacted" | "resolved" | "archived"

// Waitlist Status Types
type WaitlistStatus = "pending" | "approved" | "invited" | "onboarded" | "declined"

// Lead Status Types
type LeadStatus = "new" | "contacted" | "qualified" | "unqualified" | "converted" | "lost"

// Newsletter Status Types
type NewsletterStatus = "subscribed" | "unsubscribed" | "bounced" | "complained"

// Priority Types
type Priority = "low" | "medium" | "high" | "urgent"

type StatusType = "contact" | "waitlist" | "lead" | "newsletter" | "priority"

interface StatusBadgeProps {
  type: StatusType
  status: ContactStatus | WaitlistStatus | LeadStatus | NewsletterStatus | Priority
  showIcon?: boolean
  showTooltip?: boolean
  className?: string
}

interface BadgeConfig {
  label: string
  color: string
  icon: React.ComponentType<{ className?: string }>
  description: string
}

const contactStatusConfig: Record<ContactStatus, BadgeConfig> = {
  new: {
    label: "New",
    color: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
    icon: Circle,
    description: "New contact - not yet contacted",
  },
  contacted: {
    label: "Contacted",
    color:
      "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800",
    icon: Phone,
    description: "Contact has been reached",
  },
  resolved: {
    label: "Resolved",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: CheckCircle2,
    description: "Issue resolved successfully",
  },
  archived: {
    label: "Archived",
    color: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700",
    icon: Archive,
    description: "Contact archived",
  },
}

const waitlistStatusConfig: Record<WaitlistStatus, BadgeConfig> = {
  pending: {
    label: "Pending",
    color:
      "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800",
    icon: Clock,
    description: "Waiting for approval",
  },
  approved: {
    label: "Approved",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: CheckCircle2,
    description: "Entry approved",
  },
  invited: {
    label: "Invited",
    color: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
    icon: Send,
    description: "Invitation sent",
  },
  onboarded: {
    label: "Onboarded",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: UserCheck,
    description: "Successfully onboarded",
  },
  declined: {
    label: "Declined",
    color: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
    icon: XCircle,
    description: "Entry declined",
  },
}

const leadStatusConfig: Record<LeadStatus, BadgeConfig> = {
  new: {
    label: "New",
    color: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
    icon: Circle,
    description: "New lead",
  },
  contacted: {
    label: "Contacted",
    color:
      "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800",
    icon: Phone,
    description: "Lead has been contacted",
  },
  qualified: {
    label: "Qualified",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: ThumbsUp,
    description: "Qualified lead",
  },
  unqualified: {
    label: "Unqualified",
    color: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700",
    icon: ThumbsDown,
    description: "Not a qualified lead",
  },
  converted: {
    label: "Converted",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: CheckCircle2,
    description: "Lead converted to customer",
  },
  lost: {
    label: "Lost",
    color: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
    icon: XCircle,
    description: "Lead lost",
  },
}

const newsletterStatusConfig: Record<NewsletterStatus, BadgeConfig> = {
  subscribed: {
    label: "Subscribed",
    color: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
    icon: Mail,
    description: "Active subscriber",
  },
  unsubscribed: {
    label: "Unsubscribed",
    color: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700",
    icon: XCircle,
    description: "Unsubscribed from newsletter",
  },
  bounced: {
    label: "Bounced",
    color: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
    icon: MailWarning,
    description: "Email bounced",
  },
  complained: {
    label: "Complained",
    color:
      "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800",
    icon: AlertTriangle,
    description: "Marked as spam",
  },
}

const priorityConfig: Record<Priority, BadgeConfig> = {
  low: {
    label: "Low",
    color: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700",
    icon: Circle,
    description: "Low priority",
  },
  medium: {
    label: "Medium",
    color:
      "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800",
    icon: AlertCircle,
    description: "Medium priority",
  },
  high: {
    label: "High",
    color:
      "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800",
    icon: AlertTriangle,
    description: "High priority",
  },
  urgent: {
    label: "Urgent",
    color: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
    icon: Zap,
    description: "Urgent - requires immediate attention",
  },
}

export function StatusBadge({ type, status, showIcon = true, showTooltip = true, className }: StatusBadgeProps) {
  const getConfig = (): BadgeConfig => {
    switch (type) {
      case "contact":
        return contactStatusConfig[status as ContactStatus]
      case "waitlist":
        return waitlistStatusConfig[status as WaitlistStatus]
      case "lead":
        return leadStatusConfig[status as LeadStatus]
      case "newsletter":
        return newsletterStatusConfig[status as NewsletterStatus]
      case "priority":
        return priorityConfig[status as Priority]
      default:
        return contactStatusConfig.new
    }
  }

  const config = getConfig()
  const Icon = config.icon

  const badge = (
    <Badge
      variant="outline"
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium transition-colors",
        config.color,
        className,
      )}
      aria-label={`${type} status: ${config.label}`}
    >
      {showIcon && <Icon className="h-3 w-3" aria-hidden="true" />}
      <span>{config.label}</span>
    </Badge>
  )

  if (!showTooltip) {
    return badge
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent>
          <p>{config.description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// Helper components for convenience
export function ContactStatusBadge({
  status,
  showIcon = true,
  showTooltip = true,
  className,
}: Omit<StatusBadgeProps, "type"> & { status: ContactStatus }) {
  return (
    <StatusBadge type="contact" status={status} showIcon={showIcon} showTooltip={showTooltip} className={className} />
  )
}

export function WaitlistStatusBadge({
  status,
  showIcon = true,
  showTooltip = true,
  className,
}: Omit<StatusBadgeProps, "type"> & { status: WaitlistStatus }) {
  return (
    <StatusBadge type="waitlist" status={status} showIcon={showIcon} showTooltip={showTooltip} className={className} />
  )
}

export function LeadStatusBadge({
  status,
  showIcon = true,
  showTooltip = true,
  className,
}: Omit<StatusBadgeProps, "type"> & { status: LeadStatus }) {
  return <StatusBadge type="lead" status={status} showIcon={showIcon} showTooltip={showTooltip} className={className} />
}

export function NewsletterStatusBadge({
  status,
  showIcon = true,
  showTooltip = true,
  className,
}: Omit<StatusBadgeProps, "type"> & { status: NewsletterStatus }) {
  return (
    <StatusBadge
      type="newsletter"
      status={status}
      showIcon={showIcon}
      showTooltip={showTooltip}
      className={className}
    />
  )
}

export function PriorityBadge({
  status,
  showIcon = true,
  showTooltip = true,
  className,
}: Omit<StatusBadgeProps, "type"> & { status: Priority }) {
  return (
    <StatusBadge type="priority" status={status} showIcon={showIcon} showTooltip={showTooltip} className={className} />
  )
}
