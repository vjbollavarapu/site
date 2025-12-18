"use client"

import { useState, useMemo } from "react"
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
import { ArrowUpDown, CheckCircle, TrendingUp } from "lucide-react"
import type { Lead } from "@/types/lead"
import { cn } from "@/lib/utils"

interface LeadsTableProps {
  leads: Lead[]
  isLoading: boolean
  onLeadClick: (id: string) => void
  onBulkQualify: (ids: string[]) => void
  onBulkConvert: (ids: string[]) => void
}

export function LeadsTable({ leads, isLoading, onLeadClick, onBulkQualify, onBulkConvert }: LeadsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [rowSelection, setRowSelection] = useState({})

  const getScoreColor = (score: number) => {
    if (score <= 30) return "text-red-500"
    if (score <= 60) return "text-yellow-500"
    return "text-green-500"
  }

  const getScoreBgColor = (score: number) => {
    if (score <= 30) return "bg-red-500"
    if (score <= 60) return "bg-yellow-500"
    return "bg-green-500"
  }

  const columns = useMemo<ColumnDef<Lead>[]>(
    () => [
      {
        id: "select",
        header: ({ table }) => (
          <Checkbox
            checked={table.getIsAllPageRowsSelected()}
            onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
            aria-label="Select all"
          />
        ),
        cell: ({ row }) => (
          <Checkbox
            checked={row.getIsSelected()}
            onCheckedChange={(value) => row.toggleSelected(!!value)}
            aria-label="Select row"
          />
        ),
        enableSorting: false,
      },
      {
        accessorKey: "name",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Name
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => <div className="font-medium">{row.original.name}</div>,
      },
      {
        accessorKey: "email",
        header: "Email",
        cell: ({ row }) => <div className="text-sm text-muted-foreground">{row.original.email}</div>,
      },
      {
        accessorKey: "company",
        header: "Company",
        cell: ({ row }) => <div className="text-sm">{row.original.company}</div>,
      },
      {
        accessorKey: "leadScore",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Lead Score
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const score = row.original.leadScore
          return (
            <div className="w-32">
              <div className="flex items-center gap-2 mb-1">
                <span className={cn("text-sm font-semibold", getScoreColor(score))}>{score}</span>
              </div>
              <Progress value={score} className="h-1.5" indicatorClassName={getScoreBgColor(score)} />
            </div>
          )
        },
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => {
          const statusColors: Record<string, string> = {
            new: "bg-blue-500/10 text-blue-500",
            contacted: "bg-purple-500/10 text-purple-500",
            qualified: "bg-green-500/10 text-green-500",
            unqualified: "bg-gray-500/10 text-gray-500",
            converted: "bg-emerald-500/10 text-emerald-500",
            lost: "bg-red-500/10 text-red-500",
          }
          return (
            <Badge variant="secondary" className={statusColors[row.original.status]}>
              {row.original.status}
            </Badge>
          )
        },
      },
      {
        accessorKey: "lifecycleStage",
        header: "Lifecycle Stage",
        cell: ({ row }) => <Badge variant="outline">{row.original.lifecycleStage}</Badge>,
      },
      {
        accessorKey: "source",
        header: "Source",
        cell: ({ row }) => <div className="text-sm text-muted-foreground">{row.original.source}</div>,
      },
      {
        accessorKey: "assignedTo",
        header: "Assigned To",
        cell: ({ row }) => <div className="text-sm">{row.original.assignedTo || "Unassigned"}</div>,
      },
      {
        accessorKey: "createdAt",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Created
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => (
          <div className="text-sm text-muted-foreground">{new Date(row.original.createdAt).toLocaleDateString()}</div>
        ),
      },
      {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => (
          <div className="flex items-center gap-1">
            {row.original.status === "contacted" && (
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation()
                  onBulkQualify([row.original.id])
                }}
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Qualify
              </Button>
            )}
            {row.original.status === "qualified" && (
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation()
                  onBulkConvert([row.original.id])
                }}
              >
                <TrendingUp className="h-4 w-4 mr-1" />
                Convert
              </Button>
            )}
          </div>
        ),
      },
    ],
    [onBulkQualify, onBulkConvert],
  )

  const table = useReactTable({
    data: leads,
    columns,
    state: { sorting, rowSelection },
    onSortingChange: setSorting,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  const selectedIds = Object.keys(rowSelection)
    .filter((key) => rowSelection[key as keyof typeof rowSelection])
    .map((key) => leads[Number.parseInt(key)].id)

  if (isLoading) {
    return <div className="text-center py-12 text-muted-foreground">Loading leads...</div>
  }

  return (
    <div className="space-y-4">
      {selectedIds.length > 0 && (
        <div className="flex items-center gap-2 bg-muted/50 p-3 rounded-lg">
          <span className="text-sm font-medium">{selectedIds.length} selected</span>
          <Button size="sm" variant="outline" onClick={() => onBulkQualify(selectedIds)}>
            Bulk Qualify
          </Button>
          <Button size="sm" variant="outline" onClick={() => onBulkConvert(selectedIds)}>
            Bulk Convert
          </Button>
        </div>
      )}

      <div className="border border-border rounded-lg overflow-hidden">
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
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onLeadClick(row.original.id)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No leads found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
