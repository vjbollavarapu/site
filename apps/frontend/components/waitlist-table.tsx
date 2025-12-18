"use client"

import { useState } from "react"
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ArrowUpDown, Mail, Eye } from "lucide-react"
import { cn } from "@/lib/utils"
import type { WaitlistEntry } from "@/types/waitlist"

interface WaitlistTableProps {
  entries: WaitlistEntry[]
  onViewDetails: (entry: WaitlistEntry) => void
  onInvite: (entry: WaitlistEntry) => void
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
}

const statusColors = {
  pending: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  approved: "bg-green-500/10 text-green-500 border-green-500/20",
  invited: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  onboarded: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  declined: "bg-red-500/10 text-red-500 border-red-500/20",
}

const getPriorityColor = (score: number) => {
  if (score >= 80) return "text-red-500"
  if (score >= 60) return "text-orange-500"
  if (score >= 40) return "text-yellow-500"
  return "text-green-500"
}

export function WaitlistTable({
  entries,
  onViewDetails,
  onInvite,
  selectedIds,
  onSelectionChange,
}: WaitlistTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])

  const columns: ColumnDef<WaitlistEntry>[] = [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => {
            table.toggleAllPageRowsSelected(!!value)
            if (value) {
              onSelectionChange(entries.map((e) => e.id))
            } else {
              onSelectionChange([])
            }
          }}
          aria-label="Select all"
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
          aria-label="Select row"
        />
      ),
      enableSorting: false,
    },
    {
      accessorKey: "email",
      header: ({ column }) => (
        <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Email
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => <div className="font-medium">{row.getValue("email")}</div>,
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <div>{row.getValue("name")}</div>,
    },
    {
      accessorKey: "company",
      header: "Company",
      cell: ({ row }) => <div>{row.getValue("company")}</div>,
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => <div className="text-muted-foreground">{row.getValue("role")}</div>,
    },
    {
      accessorKey: "companySize",
      header: "Company Size",
      cell: ({ row }) => (
        <Badge variant="secondary" className="font-normal">
          {row.getValue("companySize")}
        </Badge>
      ),
    },
    {
      accessorKey: "industry",
      header: "Industry",
      cell: ({ row }) => <div className="capitalize text-muted-foreground">{row.getValue("industry")}</div>,
    },
    {
      accessorKey: "priorityScore",
      header: ({ column }) => (
        <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Priority Score
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const score = row.getValue("priorityScore") as number
        return (
          <div className="space-y-1 min-w-[120px]">
            <div className="flex items-center justify-between">
              <span className={cn("font-semibold", getPriorityColor(score))}>{score}</span>
            </div>
            <Progress value={score} className="h-1" />
          </div>
        )
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as keyof typeof statusColors
        return (
          <Badge variant="outline" className={cn("capitalize", statusColors[status])}>
            {status}
          </Badge>
        )
      },
    },
    {
      accessorKey: "createdAt",
      header: ({ column }) => (
        <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Created At
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const date = new Date(row.getValue("createdAt"))
        return <div className="text-muted-foreground">{date.toLocaleDateString()}</div>
      },
    },
    {
      id: "actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="icon" onClick={() => onViewDetails(row.original)}>
            <Eye className="h-4 w-4" />
          </Button>
          {row.original.status === "approved" && (
            <Button variant="ghost" size="icon" onClick={() => onInvite(row.original)}>
              <Mail className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  const table = useReactTable({
    data: entries,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
  })

  return (
    <div className="rounded-lg border border-border bg-card">
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
                No entries found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
