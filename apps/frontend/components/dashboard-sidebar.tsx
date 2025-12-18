"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  Target,
  Mail,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  Database,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Overview", icon: LayoutDashboard, href: "/" },
  { name: "Contacts", icon: Users, href: "/contacts" },
  { name: "Waitlist", icon: ClipboardList, href: "/waitlist" },
  { name: "Leads", icon: Target, href: "/leads" },
  { name: "Newsletter", icon: Mail, href: "/newsletter" },
  { name: "Analytics", icon: BarChart3, href: "/analytics" },
  { name: "GDPR Consent", icon: Shield, href: "/gdpr/consent" },
  { name: "GDPR Data", icon: Database, href: "/gdpr/data" },
  { name: "Settings", icon: Settings, href: "/settings" },
]

export function DashboardSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <aside
      className={cn(
        "relative border-r border-sidebar-border bg-sidebar transition-all duration-300 shadow-sm",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <div className="flex h-16 items-center border-b border-sidebar-border px-4 shadow-sm">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-sidebar-primary to-sidebar-primary/80 flex items-center justify-center shadow-sm">
              <LayoutDashboard className="h-4 w-4 text-sidebar-primary-foreground" />
            </div>
            <span className="font-semibold text-sidebar-foreground">Admin Panel</span>
          </div>
        )}
      </div>

      <nav className="p-2 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground",
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      <Button
        variant="ghost"
        size="icon"
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 h-6 w-6 rounded-full border border-sidebar-border bg-sidebar shadow-md hover:shadow-lg transition-shadow"
      >
        {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </Button>
    </aside>
  )
}
