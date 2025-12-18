import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import {
  ContactStatusBadge,
  WaitlistStatusBadge,
  LeadStatusBadge,
  NewsletterStatusBadge,
  PriorityBadge,
} from "@/components/status-badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function StatusBadgesDemoPage() {
  return (
    <div className="flex h-screen overflow-hidden">
      <DashboardSidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto bg-muted/30 p-6">
          <div className="mx-auto max-w-6xl space-y-6">
            <div>
              <h1 className="text-3xl font-bold">Status Badge Component Library</h1>
              <p className="mt-2 text-muted-foreground">
                Reusable status badges with consistent styling, icons, and tooltips
              </p>
            </div>

            {/* Contact Status Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Contact Status Badges</CardTitle>
                <CardDescription>Status indicators for contact management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">Default (with icons and tooltips)</h3>
                  <div className="flex flex-wrap gap-3">
                    <ContactStatusBadge status="new" />
                    <ContactStatusBadge status="contacted" />
                    <ContactStatusBadge status="resolved" />
                    <ContactStatusBadge status="archived" />
                  </div>
                </div>
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">Without icons</h3>
                  <div className="flex flex-wrap gap-3">
                    <ContactStatusBadge status="new" showIcon={false} />
                    <ContactStatusBadge status="contacted" showIcon={false} />
                    <ContactStatusBadge status="resolved" showIcon={false} />
                    <ContactStatusBadge status="archived" showIcon={false} />
                  </div>
                </div>
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">Without tooltips</h3>
                  <div className="flex flex-wrap gap-3">
                    <ContactStatusBadge status="new" showTooltip={false} />
                    <ContactStatusBadge status="contacted" showTooltip={false} />
                    <ContactStatusBadge status="resolved" showTooltip={false} />
                    <ContactStatusBadge status="archived" showTooltip={false} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Waitlist Status Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Waitlist Status Badges</CardTitle>
                <CardDescription>Status indicators for waitlist management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">All statuses</h3>
                  <div className="flex flex-wrap gap-3">
                    <WaitlistStatusBadge status="pending" />
                    <WaitlistStatusBadge status="approved" />
                    <WaitlistStatusBadge status="invited" />
                    <WaitlistStatusBadge status="onboarded" />
                    <WaitlistStatusBadge status="declined" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lead Status Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Lead Status Badges</CardTitle>
                <CardDescription>Status indicators for lead management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">All statuses</h3>
                  <div className="flex flex-wrap gap-3">
                    <LeadStatusBadge status="new" />
                    <LeadStatusBadge status="contacted" />
                    <LeadStatusBadge status="qualified" />
                    <LeadStatusBadge status="unqualified" />
                    <LeadStatusBadge status="converted" />
                    <LeadStatusBadge status="lost" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Newsletter Status Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Newsletter Status Badges</CardTitle>
                <CardDescription>Status indicators for newsletter subscribers</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">All statuses</h3>
                  <div className="flex flex-wrap gap-3">
                    <NewsletterStatusBadge status="subscribed" />
                    <NewsletterStatusBadge status="unsubscribed" />
                    <NewsletterStatusBadge status="bounced" />
                    <NewsletterStatusBadge status="complained" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Priority Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Priority Badges</CardTitle>
                <CardDescription>Priority level indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">All priorities</h3>
                  <div className="flex flex-wrap gap-3">
                    <PriorityBadge status="low" />
                    <PriorityBadge status="medium" />
                    <PriorityBadge status="high" />
                    <PriorityBadge status="urgent" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Example */}
            <Card>
              <CardHeader>
                <CardTitle>Usage Example in Table</CardTitle>
                <CardDescription>How badges look in a typical data table</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="pb-3 text-left text-sm font-medium">Name</th>
                        <th className="pb-3 text-left text-sm font-medium">Contact Status</th>
                        <th className="pb-3 text-left text-sm font-medium">Lead Status</th>
                        <th className="pb-3 text-left text-sm font-medium">Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b">
                        <td className="py-3 text-sm">John Doe</td>
                        <td className="py-3">
                          <ContactStatusBadge status="new" />
                        </td>
                        <td className="py-3">
                          <LeadStatusBadge status="qualified" />
                        </td>
                        <td className="py-3">
                          <PriorityBadge status="high" />
                        </td>
                      </tr>
                      <tr className="border-b">
                        <td className="py-3 text-sm">Jane Smith</td>
                        <td className="py-3">
                          <ContactStatusBadge status="contacted" />
                        </td>
                        <td className="py-3">
                          <LeadStatusBadge status="converted" />
                        </td>
                        <td className="py-3">
                          <PriorityBadge status="medium" />
                        </td>
                      </tr>
                      <tr className="border-b">
                        <td className="py-3 text-sm">Bob Johnson</td>
                        <td className="py-3">
                          <ContactStatusBadge status="resolved" />
                        </td>
                        <td className="py-3">
                          <LeadStatusBadge status="lost" />
                        </td>
                        <td className="py-3">
                          <PriorityBadge status="low" />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Code Example */}
            <Card>
              <CardHeader>
                <CardTitle>Code Examples</CardTitle>
                <CardDescription>How to use the status badge components in your code</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="mb-2 text-sm font-semibold">Basic Usage</h3>
                  <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
                    <code>{`import { ContactStatusBadge, PriorityBadge } from '@/components/status-badge'

// Default with icon and tooltip
<ContactStatusBadge status="new" />

// Without icon
<ContactStatusBadge status="contacted" showIcon={false} />

// Without tooltip
<PriorityBadge status="urgent" showTooltip={false} />

// Custom className
<LeadStatusBadge status="qualified" className="ml-2" />`}</code>
                  </pre>
                </div>
                <div>
                  <h3 className="mb-2 text-sm font-semibold">Available Statuses</h3>
                  <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
                    <code>{`// Contact: 'new' | 'contacted' | 'resolved' | 'archived'
// Waitlist: 'pending' | 'approved' | 'invited' | 'onboarded' | 'declined'
// Lead: 'new' | 'contacted' | 'qualified' | 'unqualified' | 'converted' | 'lost'
// Newsletter: 'subscribed' | 'unsubscribed' | 'bounced' | 'complained'
// Priority: 'low' | 'medium' | 'high' | 'urgent'`}</code>
                  </pre>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
