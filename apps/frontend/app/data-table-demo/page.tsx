"use client"

import * as React from "react"
import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { DataTable, RowActionsDropdown, SortableHeader } from "@/components/data-table/data-table"
import { useToast } from "@/hooks/use-toast"

// Sample data type
type User = {
  id: string
  name: string
  email: string
  status: "active" | "inactive" | "pending"
  role: string
  createdAt: string
}

// Sample data
const sampleData: User[] = Array.from({ length: 50 }, (_, i) => ({
  id: `user-${i + 1}`,
  name: `User ${i + 1}`,
  email: `user${i + 1}@example.com`,
  status: ["active", "inactive", "pending"][Math.floor(Math.random() * 3)] as User["status"],
  role: ["Admin", "Editor", "Viewer"][Math.floor(Math.random() * 3)],
  createdAt: new Date(Date.now() - Math.random() * 10000000000).toISOString().split("T")[0],
}))

export default function DataTableDemoPage() {
  const { toast } = useToast()
  const [selectedRows, setSelectedRows] = React.useState<User[]>([])

  const columns: ColumnDef<User>[] = [
    {
      accessorKey: "name",
      header: ({ column }) => <SortableHeader column={column}>Name</SortableHeader>,
    },
    {
      accessorKey: "email",
      header: ({ column }) => <SortableHeader column={column}>Email</SortableHeader>,
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as string
        return (
          <Badge variant={status === "active" ? "default" : status === "pending" ? "secondary" : "outline"}>
            {status}
          </Badge>
        )
      },
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => <span className="font-medium">{row.getValue("role")}</span>,
    },
    {
      accessorKey: "createdAt",
      header: ({ column }) => <SortableHeader column={column}>Created</SortableHeader>,
    },
  ]

  const handleRowClick = (row: User) => {
    toast({
      title: "Row clicked",
      description: `You clicked on ${row.name}`,
    })
  }

  const handleSelectionChange = (rows: User[]) => {
    setSelectedRows(rows)
  }

  const rowActions = (row: User) => (
    <RowActionsDropdown
      actions={[
        {
          label: "View details",
          onClick: () => {
            toast({
              title: "View details",
              description: `Viewing details for ${row.name}`,
            })
          },
        },
        {
          label: "Edit",
          onClick: () => {
            toast({
              title: "Edit",
              description: `Editing ${row.name}`,
            })
          },
        },
        {
          label: "Delete",
          onClick: () => {
            toast({
              title: "Delete",
              description: `Deleting ${row.name}`,
              variant: "destructive",
            })
          },
          destructive: true,
        },
      ]}
    />
  )

  return (
    <div className="container mx-auto py-10">
      <div className="mb-8 space-y-2">
        <h1 className="text-3xl font-bold">Data Table Demo</h1>
        <p className="text-muted-foreground">
          A powerful, reusable data table component with sorting, filtering, pagination, and more.
        </p>
      </div>

      {selectedRows.length > 0 && (
        <div className="mb-4 rounded-md border bg-muted/50 p-4">
          <h3 className="mb-2 font-semibold">Selected Rows:</h3>
          <div className="flex flex-wrap gap-2">
            {selectedRows.map((row) => (
              <Badge key={row.id} variant="secondary">
                {row.name}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <DataTable
        columns={columns}
        data={sampleData}
        searchKey="name"
        searchPlaceholder="Search by name..."
        onRowClick={handleRowClick}
        onSelectionChange={handleSelectionChange}
        rowActions={rowActions}
        enableRowSelection={true}
        enableMultiRowSelection={true}
        enableColumnVisibility={true}
        enableExport={true}
      />
    </div>
  )
}
