import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { ContactsTable } from "@/components/contacts-table"

export default function ContactsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col">
        <DashboardHeader />
        <main className="flex-1 p-6 lg:p-8">
          <div className="mb-6">
            <h1 className="text-3xl font-semibold text-foreground">Contacts Management</h1>
            <p className="text-muted-foreground mt-1">Manage and track all customer contacts</p>
          </div>
          <ContactsTable />
        </main>
      </div>
    </div>
  )
}
