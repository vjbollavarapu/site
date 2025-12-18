"use client"

import * as React from "react"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Upload, X, File, AlertCircle, Loader2 } from "lucide-react"

export interface FormFileUploadProps {
  label?: string
  accept?: string
  multiple?: boolean
  maxSize?: number // in MB
  value?: File[]
  onChange?: (files: File[]) => void
  error?: string
  helperText?: string
  isRequired?: boolean
  isLoading?: boolean
  disabled?: boolean
  showPreview?: boolean
  id?: string
}

export const FormFileUpload: React.FC<FormFileUploadProps> = ({
  label,
  accept,
  multiple = false,
  maxSize = 5,
  value = [],
  onChange,
  error,
  helperText,
  isRequired = false,
  isLoading = false,
  disabled = false,
  showPreview = true,
  id,
}) => {
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const uploadId = id || `upload-${label?.toLowerCase().replace(/\s+/g, "-")}`

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])

    // Validate file size
    const validFiles = files.filter((file) => {
      const fileSizeMB = file.size / (1024 * 1024)
      return fileSizeMB <= maxSize
    })

    if (multiple) {
      onChange?.([...value, ...validFiles])
    } else {
      onChange?.(validFiles.slice(0, 1))
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleRemove = (index: number) => {
    onChange?.(value.filter((_, i) => i !== index))
  }

  const getPreviewUrl = (file: File) => {
    if (file.type.startsWith("image/")) {
      return URL.createObjectURL(file)
    }
    return null
  }

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={uploadId} className="text-sm font-medium">
          {label}
          {isRequired && (
            <span className="text-destructive ml-1" aria-label="required">
              *
            </span>
          )}
        </Label>
      )}
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center",
          error ? "border-destructive" : "border-border",
          disabled && "opacity-50 cursor-not-allowed",
        )}
      >
        <input
          ref={fileInputRef}
          id={uploadId}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileChange}
          disabled={disabled || isLoading}
          className="hidden"
          aria-invalid={!!error}
          aria-required={isRequired}
        />
        <div className="space-y-3">
          <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            {isLoading ? (
              <Loader2 className="h-6 w-6 text-primary animate-spin" />
            ) : (
              <Upload className="h-6 w-6 text-primary" />
            )}
          </div>
          <div>
            <Button
              type="button"
              variant="secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled || isLoading}
            >
              Choose {multiple ? "files" : "file"}
            </Button>
            <p className="text-sm text-muted-foreground mt-2">
              {accept ? `Accepted formats: ${accept}` : "All file types accepted"}
            </p>
            <p className="text-xs text-muted-foreground">Maximum file size: {maxSize}MB</p>
          </div>
        </div>
      </div>

      {showPreview && value.length > 0 && (
        <div className="space-y-2">
          {value.map((file, index) => {
            const previewUrl = getPreviewUrl(file)
            return (
              <div key={index} className="flex items-center gap-3 p-3 border rounded-lg bg-card">
                {previewUrl ? (
                  <img
                    src={previewUrl || "/placeholder.svg"}
                    alt={file.name}
                    className="w-12 h-12 rounded object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded bg-muted flex items-center justify-center">
                    <File className="h-6 w-6 text-muted-foreground" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(2)} KB</p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemove(index)}
                  disabled={disabled}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )
          })}
        </div>
      )}

      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      {!error && helperText && <p className="text-sm text-muted-foreground">{helperText}</p>}
    </div>
  )
}
