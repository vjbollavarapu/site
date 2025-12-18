"use client"

import * as React from "react"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Check, ChevronsUpDown, X, AlertCircle, Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export interface SelectOption {
  label: string
  value: string
  disabled?: boolean
}

export interface FormSelectProps {
  label?: string
  placeholder?: string
  options: SelectOption[]
  value?: string | string[]
  onChange?: (value: string | string[]) => void
  error?: string
  helperText?: string
  isRequired?: boolean
  isLoading?: boolean
  disabled?: boolean
  multiSelect?: boolean
  searchable?: boolean
  id?: string
}

export const FormSelect: React.FC<FormSelectProps> = ({
  label,
  placeholder = "Select option...",
  options,
  value,
  onChange,
  error,
  helperText,
  isRequired = false,
  isLoading = false,
  disabled = false,
  multiSelect = false,
  searchable = true,
  id,
}) => {
  const [open, setOpen] = React.useState(false)
  const selectId = id || `select-${label?.toLowerCase().replace(/\s+/g, "-")}`

  const selectedValues = React.useMemo(() => {
    if (multiSelect) {
      return Array.isArray(value) ? value : []
    }
    return value ? [value as string] : []
  }, [value, multiSelect])

  const handleSelect = (selectedValue: string) => {
    if (multiSelect) {
      const newValues = selectedValues.includes(selectedValue)
        ? selectedValues.filter((v) => v !== selectedValue)
        : [...selectedValues, selectedValue]
      onChange?.(newValues)
    } else {
      onChange?.(selectedValue)
      setOpen(false)
    }
  }

  const handleRemove = (valueToRemove: string) => {
    if (multiSelect) {
      onChange?.(selectedValues.filter((v) => v !== valueToRemove))
    }
  }

  const getDisplayText = () => {
    if (selectedValues.length === 0) return placeholder
    if (!multiSelect) {
      return options.find((opt) => opt.value === selectedValues[0])?.label || placeholder
    }
    return `${selectedValues.length} selected`
  }

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={selectId} className="text-sm font-medium">
          {label}
          {isRequired && (
            <span className="text-destructive ml-1" aria-label="required">
              *
            </span>
          )}
        </Label>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            id={selectId}
            variant="outline"
            role="combobox"
            aria-expanded={open}
            aria-invalid={!!error}
            disabled={disabled || isLoading}
            className={cn(
              "w-full justify-between",
              error && "border-destructive",
              !selectedValues.length && "text-muted-foreground",
            )}
          >
            <span className="truncate">{getDisplayText()}</span>
            {isLoading ? (
              <Loader2 className="ml-2 h-4 w-4 shrink-0 animate-spin" />
            ) : (
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0" align="start">
          <Command>
            {searchable && <CommandInput placeholder="Search..." />}
            <CommandList>
              <CommandEmpty>No option found.</CommandEmpty>
              <CommandGroup>
                {options.map((option) => (
                  <CommandItem
                    key={option.value}
                    value={option.value}
                    onSelect={() => handleSelect(option.value)}
                    disabled={option.disabled}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedValues.includes(option.value) ? "opacity-100" : "opacity-0",
                      )}
                    />
                    {option.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {multiSelect && selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedValues.map((val) => {
            const option = options.find((opt) => opt.value === val)
            return (
              <Badge key={val} variant="secondary" className="gap-1">
                {option?.label}
                <button
                  type="button"
                  onClick={() => handleRemove(val)}
                  className="ml-1 hover:bg-secondary-foreground/20 rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
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
