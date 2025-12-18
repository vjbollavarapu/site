"use client"

import { useState } from "react"
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Eye, MailX, Trash2, ArrowUpDown, Check, RefreshCw } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import type { Subscriber } from "@/types/subscriber"
import { format } from "date-fns"
import { useSubscribers } from "@/hooks/use-subscribers"
import { toast } from "@/hooks/use-toast"

interface SubscribersTableProps {
  subscribers: Subscriber[]
  isLoading: boolean
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  onViewDetails: (subscriber: Subscriber) => void
}

export function SubscribersTable({
  subscribers,
  isLoading,
  selectedIds,
  onSelectionChange,
  onViewDetails,
}: SubscribersTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const { unsubscribe, deleteSubscriber, resendVerification } = useSubscribers({})

  const handleUnsubscribe = async (id: string) => {
    const success = await unsubscribe(id)
    if (success) {
      toast({
        title: "Unsubscribed",
        description: "Subscriber has been unsubscribed",
      })
    }
  }

  const handleDelete = async (id: string) => {
    const success = await deleteSubscriber(id)
    if (success) {
      toast({
        title: "Deleted",
        description: "Subscriber has been deleted",
      })
    }
  }

  const handleResendVerification = async (id: string) => {
    const success = await resendVerification(id)
    if (success) {
      toast({
        title: "Verification sent",
        description: "Verification email has been resent",
      })
    }
  }

  const columns: ColumnDef<Subscriber>[] = [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => {
            table.toggleAllPageRowsSelected(!!value)
            if (value) {
              onSelectionChange(subscribers.map((s) => s.id))
            } else {
              onSelectionChange([])
            }
          }}
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={selectedIds.includes(row.original.id)}
          onCheckedChange={(value) => {
            if (value) {
              onSelectionChange([...selectedIds, row.original.id])
            } else {
              onSelectionChange(selectedIds.filter((id) => id !== row.original.id))
            }
          }}
        />
      ),
    },
    {
      accessorKey: "email",
      header: ({ column }) => {
        return (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Email
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => <div className="font-medium">{row.getValue("email")}</div>,
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <div>{row.getValue("name") || "-"}</div>,
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as string
        const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
          subscribed: "default",
          unsubscribed: "secondary",
          bounced: "destructive",
          complained: "destructive",
        }
        return <Badge variant={variants[status] || "outline"}>{status}</Badge>
      },
    },
    {
      accessorKey: "source",
      header: "Source",
      cell: ({ row }) => {
        const source = row.getValue("source") as string
        return <span className="text-muted-foreground capitalize">{source}</span>
      },
    },
    {
      accessorKey: "subscribedAt",
      header: ({ column }) => {
        return (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Subscribed At
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const date = new Date(row.getValue("subscribedAt"))
        return <span className="text-muted-foreground">{format(date, "MMM d, yyyy")}</span>
      },
    },
    {
      accessorKey: "verified",
      header: "Verified",
      cell: ({ row }) => {
        const verified = row.getValue("verified") as boolean
        return verified ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Button variant="ghost" size="sm" onClick={() => handleResendVerification(row.original.id)}>
            <RefreshCw className="h-3 w-3" />
          </Button>
        )
      },
    },
    {
      accessorKey: "lastEmailSent",
      header: "Last Email",
      cell: ({ row }) => {
        const date = row.getValue("lastEmailSent") as string | null
        if (!date) return <span className="text-muted-foreground">-</span>
        return <span className="text-muted-foreground">{format(new Date(date), "MMM d")}</span>
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const subscriber = row.original
        return (
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" onClick={() => onViewDetails(subscriber)}>
              <Eye className="h-4 w-4" />
            </Button>
            {subscriber.status === "subscribed" && (
              <Button variant="ghost" size="sm" onClick={() => handleUnsubscribe(subscriber.id)}>
                <MailX className="h-4 w-4" />
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={() => handleDelete(subscriber.id)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        )
      },
    },
  ]

  const table = useReactTable({
    data: subscribers,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
  })

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12" />
          ))}
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No subscribers found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}
