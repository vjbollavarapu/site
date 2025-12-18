export default function DataTableDemoLoading() {
  return (
    <div className="container mx-auto py-10">
      <div className="mb-8 space-y-2">
        <div className="h-9 w-64 animate-pulse rounded-md bg-muted" />
        <div className="h-5 w-96 animate-pulse rounded-md bg-muted" />
      </div>
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div className="h-10 w-64 animate-pulse rounded-md bg-muted" />
          <div className="flex items-center gap-2">
            <div className="h-9 w-20 animate-pulse rounded-md bg-muted" />
            <div className="h-9 w-24 animate-pulse rounded-md bg-muted" />
          </div>
        </div>
        <div className="h-[600px] animate-pulse rounded-md border bg-muted/20" />
        <div className="flex items-center justify-between">
          <div className="h-5 w-48 animate-pulse rounded-md bg-muted" />
          <div className="flex items-center gap-2">
            <div className="h-9 w-20 animate-pulse rounded-md bg-muted" />
            <div className="h-9 w-16 animate-pulse rounded-md bg-muted" />
          </div>
        </div>
      </div>
    </div>
  )
}
