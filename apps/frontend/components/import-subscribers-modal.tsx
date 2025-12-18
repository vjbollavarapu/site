"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Upload, FileText, CheckCircle } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import { useSubscribers } from "@/hooks/use-subscribers"

interface ImportSubscribersModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ImportSubscribersModal({ open, onOpenChange }: ImportSubscribersModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isImporting, setIsImporting] = useState(false)
  const { importSubscribers } = useSubscribers({})

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "text/csv") {
      setFile(selectedFile)
    } else {
      toast({
        title: "Invalid file",
        description: "Please select a CSV file",
        variant: "destructive",
      })
    }
  }

  const handleImport = async () => {
    if (!file) return

    setIsImporting(true)
    const success = await importSubscribers(file)
    setIsImporting(false)

    if (success) {
      toast({
        title: "Import successful",
        description: "Subscribers have been imported",
      })
      setFile(null)
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Import Subscribers</DialogTitle>
          <DialogDescription>
            Upload a CSV file with subscriber information. The file should include columns for email, name, and source.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {!file ? (
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:bg-accent/50 transition-colors">
              <div className="flex flex-col items-center justify-center">
                <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">Click to upload or drag and drop</p>
                <p className="text-xs text-muted-foreground mt-1">CSV files only</p>
              </div>
              <input type="file" className="hidden" accept=".csv" onChange={handleFileChange} />
            </label>
          ) : (
            <div className="flex items-center gap-3 p-4 border border-border rounded-lg">
              <FileText className="h-8 w-8 text-blue-500" />
              <div className="flex-1">
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
          )}

          <div className="bg-accent/50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">CSV Format Example:</h4>
            <pre className="text-xs text-muted-foreground">
              {`email,name,source
john@example.com,John Doe,website
jane@example.com,Jane Smith,landing-page`}
            </pre>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleImport} disabled={!file || isImporting}>
            {isImporting ? "Importing..." : "Import"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
