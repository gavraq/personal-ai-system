'use client'

import { useState, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { getAccessToken } from '@/lib/auth'

interface FileUploaderProps {
  dealId: string
  onFileUploaded?: (file: UploadedFile) => void
  disabled?: boolean
}

export interface UploadedFile {
  id: string
  name: string
  mime_type: string | null
  size_bytes: number
  source: 'gcs'
  source_id: string
}

// Maximum file size: 100MB
const MAX_FILE_SIZE = 100 * 1024 * 1024

// Allowed MIME types
const ALLOWED_MIME_TYPES = new Set([
  // Documents
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/csv',
  // Images
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',
  // Archives
  'application/zip',
  'application/x-rar-compressed',
  'application/gzip',
])

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function FileUploader({ dealId, onFileUploaded, disabled }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File "${file.name}" exceeds maximum size of 100MB`
    }

    // Check MIME type
    if (!ALLOWED_MIME_TYPES.has(file.type)) {
      return `File type "${file.type || 'unknown'}" is not allowed`
    }

    return null
  }, [])

  const uploadFile = useCallback(async (file: File) => {
    // Validate file first
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    setIsUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const token = getAccessToken()

      // Create XMLHttpRequest for progress tracking
      const xhr = new XMLHttpRequest()

      const uploadPromise = new Promise<UploadedFile>((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100)
            setUploadProgress(progress)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status === 201) {
            try {
              const response = JSON.parse(xhr.responseText)
              resolve(response)
            } catch {
              reject(new Error('Invalid response from server'))
            }
          } else if (xhr.status === 413) {
            reject(new Error('File size exceeds maximum allowed'))
          } else if (xhr.status === 415) {
            reject(new Error('File type is not allowed'))
          } else {
            try {
              const errorResponse = JSON.parse(xhr.responseText)
              reject(new Error(errorResponse.detail || 'Upload failed'))
            } catch {
              reject(new Error(`Upload failed with status ${xhr.status}`))
            }
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Network error during upload'))
        })

        xhr.addEventListener('abort', () => {
          reject(new Error('Upload was cancelled'))
        })

        xhr.open('POST', `${API_BASE_URL}/api/deals/${dealId}/files/upload`)
        if (token) {
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        }
        xhr.send(formData)
      })

      const uploadedFile = await uploadPromise
      onFileUploaded?.(uploadedFile)
      setUploadProgress(100)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload file'
      setError(errorMessage)
    } finally {
      setIsUploading(false)
      // Reset progress after a short delay to show completion
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }, [dealId, onFileUploaded, validateFile])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled && !isUploading) {
      setIsDragging(true)
    }
  }, [disabled, isUploading])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    if (disabled || isUploading) return

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      // Upload first file (single file upload)
      uploadFile(files[0])
    }
  }, [disabled, isUploading, uploadFile])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      uploadFile(files[0])
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }, [uploadFile])

  const handleButtonClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  return (
    <div className="space-y-2">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileSelect}
        disabled={disabled || isUploading}
        accept={Array.from(ALLOWED_MIME_TYPES).join(',')}
      />

      {/* Drop zone */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${isDragging
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50'
          }
          ${disabled || isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        {isUploading ? (
          <div className="space-y-3">
            <div className="flex items-center justify-center">
              <svg
                className="w-8 h-8 text-primary animate-pulse"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">Uploading...</p>
            <Progress value={uploadProgress} className="w-full max-w-xs mx-auto" />
            <p className="text-xs text-muted-foreground">{uploadProgress}%</p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center justify-center">
              <svg
                className="w-8 h-8 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">
              {isDragging ? 'Drop file here' : 'Drag and drop a file, or click to select'}
            </p>
            <p className="text-xs text-muted-foreground">
              Max 100MB. PDF, Word, Excel, images, and more.
            </p>
          </div>
        )}
      </div>

      {/* Alternative button */}
      <Button
        onClick={handleButtonClick}
        disabled={disabled || isUploading}
        variant="outline"
        className="w-full"
      >
        {isUploading ? (
          'Uploading...'
        ) : (
          <>
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
              />
            </svg>
            Upload File
          </>
        )}
      </Button>

      {/* Error message */}
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </div>
  )
}

export default FileUploader
