import React, { useRef, useState } from 'react'
import { UploadCloud, FileText, CheckCircle2, X, AlertCircle } from 'lucide-react'

interface DropzoneProps {
  id: string
  label: string
  badgeLabel?: string
  badgeColor?: 'indigo' | 'amber' | 'emerald'
  file: File | null
  onFileSelect: (file: File | null) => void
  disabled?: boolean
}

export const Dropzone: React.FC<DropzoneProps> = ({
  id,
  label,
  badgeLabel,
  badgeColor = 'indigo',
  file,
  onFileSelect,
  disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const [dragError, setDragError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (disabled) return
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    if (disabled) return

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === 'application/pdf' || droppedFile.name.toLowerCase().endsWith('.pdf')) {
        setDragError(null)
        onFileSelect(droppedFile)
      } else {
        setDragError('Only text-based PDF documents are accepted.')
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0]
      if (selected.type === 'application/pdf' || selected.name.toLowerCase().endsWith('.pdf')) {
        setDragError(null)
        onFileSelect(selected)
      } else {
        setDragError('Only text-based PDF documents are accepted.')
      }
    }
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (inputRef.current) {
      inputRef.current.value = ''
    }
    setDragError(null)
    onFileSelect(null)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const badgeClasses = {
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  }[badgeColor]

  return (
    <div className="flex-1 flex flex-col">
      {/* Label Header */}
      <div className="flex items-center justify-between mb-2">
        <label htmlFor={id} className="text-sm font-semibold text-slate-800 flex items-center gap-2">
          {label}
        </label>
        {badgeLabel && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeClasses}`}>
            {badgeLabel}
          </span>
        )}
      </div>

      {/* Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-6 transition-all cursor-pointer flex flex-col items-center justify-center min-h-[170px] ${
          disabled
            ? 'bg-slate-50 border-slate-200 opacity-60 cursor-not-allowed'
            : isDragOver
            ? 'border-indigo-500 bg-indigo-50/60 ring-2 ring-indigo-200'
            : file
            ? 'border-emerald-300 bg-emerald-50/30 hover:border-emerald-400'
            : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-slate-50/80'
        }`}
      >
        <input
          ref={inputRef}
          id={id}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
          disabled={disabled}
          className="hidden"
        />

        {file ? (
          <div className="w-full flex items-center justify-between px-2">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="p-3 bg-emerald-100 text-emerald-700 rounded-lg shrink-0">
                <FileText className="w-6 h-6" />
              </div>
              <div className="truncate text-left">
                <div className="flex items-center space-x-1.5">
                  <p className="text-sm font-semibold text-slate-800 truncate" title={file.name}>
                    {file.name}
                  </p>
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                </div>
                <p className="text-xs text-slate-500 font-mono">
                  {formatFileSize(file.size)} &bull; Ready
                </p>
              </div>
            </div>
            {!disabled && (
              <button
                type="button"
                onClick={handleClear}
                className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors shrink-0 ml-2"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center text-center">
            <div className="w-10 h-10 mb-2 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 group-hover:text-indigo-600 transition-colors">
              <UploadCloud className="w-5 h-5 text-slate-500" />
            </div>
            <p className="text-sm font-medium text-slate-700">
              <span className="text-indigo-600 font-semibold hover:underline">Click to browse</span> or drag and drop
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Text-based PDF document (up to 3 pages)
            </p>
          </div>
        )}

        {dragError && (
          <div className="mt-3 flex items-center text-xs font-medium text-rose-600 bg-rose-50 px-2.5 py-1 rounded-md border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5 mr-1.5 shrink-0" />
            {dragError}
          </div>
        )}
      </div>
    </div>
  )
}
