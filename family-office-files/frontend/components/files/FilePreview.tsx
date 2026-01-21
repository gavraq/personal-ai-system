'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { filesApi, DealFile } from '@/lib/api'

// Icons
const DownloadIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
)

const LoadingSpinner = () => (
  <svg className="w-8 h-8 animate-spin text-primary" viewBox="0 0 24 24" fill="none">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
)

const FileIcon = () => (
  <svg className="w-16 h-16 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
)

interface FilePreviewProps {
  file: DealFile | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

// MIME types that can be previewed
const PREVIEWABLE_IMAGES = new Set([
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',
])

const PREVIEWABLE_PDFS = new Set([
  'application/pdf',
])

// Google Drive file types that work with Google Docs Viewer
const GOOGLE_DOCS_PREVIEWABLE = new Set([
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/csv',
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
])

// Google Drive MIME types
const GOOGLE_DRIVE_MIME_TYPES = new Set([
  'application/vnd.google-apps.document',
  'application/vnd.google-apps.spreadsheet',
  'application/vnd.google-apps.presentation',
  'application/vnd.google-apps.drawing',
])

function isPreviewableImage(mimeType: string | null): boolean {
  return mimeType !== null && PREVIEWABLE_IMAGES.has(mimeType)
}

function isPreviewablePdf(mimeType: string | null): boolean {
  return mimeType !== null && PREVIEWABLE_PDFS.has(mimeType)
}

function isGoogleDocsPreviewable(mimeType: string | null): boolean {
  return mimeType !== null && (GOOGLE_DOCS_PREVIEWABLE.has(mimeType) || GOOGLE_DRIVE_MIME_TYPES.has(mimeType))
}

function isGoogleNativeFile(mimeType: string | null): boolean {
  return mimeType !== null && GOOGLE_DRIVE_MIME_TYPES.has(mimeType)
}

function canPreview(file: DealFile): boolean {
  if (file.source === 'drive') {
    // Drive files can use Google Docs Viewer for many types
    return isGoogleDocsPreviewable(file.mime_type) || isGoogleNativeFile(file.mime_type)
  }
  // GCS files can preview images and PDFs
  return isPreviewableImage(file.mime_type) || isPreviewablePdf(file.mime_type)
}

function getFileTypeLabel(mimeType: string | null): string {
  if (!mimeType) return 'File'
  if (mimeType.includes('pdf')) return 'PDF Document'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'Word Document'
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'Spreadsheet'
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'Presentation'
  if (mimeType.startsWith('image/')) return 'Image'
  if (mimeType.includes('text/')) return 'Text File'
  if (mimeType.includes('csv')) return 'CSV File'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'Archive'
  return 'File'
}

export function FilePreview({ file, open, onOpenChange }: FilePreviewProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPreviewUrl = useCallback(async () => {
    if (!file) return

    setIsLoading(true)
    setError(null)
    setPreviewUrl(null)

    try {
      if (file.source === 'drive') {
        // For Drive files, use Google Docs Viewer with the drive file ID
        // Native Google files (Docs, Sheets, Slides) use direct embed
        if (isGoogleNativeFile(file.mime_type)) {
          // Google native files have their own embed URLs
          const viewerUrl = `https://docs.google.com/viewer?srcid=${file.source_id}&pid=explorer&efh=false&a=v&chrome=false&embedded=true`
          setPreviewUrl(viewerUrl)
        } else {
          // Other Drive files use Google Docs Viewer
          // Construct Google Drive preview URL
          const drivePreviewUrl = `https://drive.google.com/file/d/${file.source_id}/preview`
          setPreviewUrl(drivePreviewUrl)
        }
      } else {
        // For GCS files, get a signed URL
        const response = await filesApi.getDownloadUrl(file.id)
        setPreviewUrl(response.download_url)
      }
    } catch (err) {
      console.error('Error loading preview URL:', err)
      setError('Failed to load preview')
    } finally {
      setIsLoading(false)
    }
  }, [file])

  useEffect(() => {
    if (open && file) {
      loadPreviewUrl()
    } else {
      // Reset state when modal closes
      setPreviewUrl(null)
      setError(null)
    }
  }, [open, file, loadPreviewUrl])

  const handleDownload = async () => {
    if (!file) return

    try {
      const response = await filesApi.getDownloadUrl(file.id)
      window.open(response.download_url, '_blank')
    } catch (err) {
      console.error('Error getting download URL:', err)
    }
  }

  const handleOpenInNewTab = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank')
    }
  }

  if (!file) return null

  const isPreviewable = canPreview(file)
  const isImage = isPreviewableImage(file.mime_type)
  const isPdf = isPreviewablePdf(file.mime_type)
  const isDriveFile = file.source === 'drive'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={`${isPreviewable ? 'max-w-4xl h-[85vh]' : 'max-w-md'} flex flex-col`}
        aria-describedby="file-preview-description"
      >
        <DialogHeader>
          <DialogTitle className="truncate pr-8">{file.name}</DialogTitle>
          <DialogDescription id="file-preview-description">
            {getFileTypeLabel(file.mime_type)}
            {file.size_bytes && ` • ${formatFileSize(file.size_bytes)}`}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 min-h-0 flex flex-col">
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <LoadingSpinner />
                <p className="text-sm text-muted-foreground">Loading preview...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <p className="text-destructive">{error}</p>
                <Button onClick={handleDownload}>
                  <DownloadIcon />
                  <span className="ml-2">Download Instead</span>
                </Button>
              </div>
            </div>
          ) : isPreviewable && previewUrl ? (
            // Render preview based on file type
            <div className="flex-1 min-h-0 relative bg-gray-100 rounded-lg overflow-hidden">
              {isImage && !isDriveFile ? (
                // Native image preview for GCS files
                <div className="absolute inset-0 flex items-center justify-center p-4">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={previewUrl}
                    alt={file.name}
                    className="max-w-full max-h-full object-contain"
                    onError={() => setError('Failed to load image')}
                  />
                </div>
              ) : isPdf && !isDriveFile ? (
                // PDF preview using iframe for GCS files
                <iframe
                  src={previewUrl}
                  className="absolute inset-0 w-full h-full border-0"
                  title={`Preview of ${file.name}`}
                />
              ) : isDriveFile ? (
                // Google Drive preview using iframe
                <iframe
                  src={previewUrl}
                  className="absolute inset-0 w-full h-full border-0"
                  title={`Preview of ${file.name}`}
                  sandbox="allow-scripts allow-same-origin allow-popups"
                />
              ) : null}
            </div>
          ) : (
            // Fallback for non-previewable files
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4 py-8">
                <FileIcon />
                <div className="space-y-2">
                  <p className="text-muted-foreground">
                    Preview not available for this file type
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {getFileTypeLabel(file.mime_type)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          {previewUrl && isPreviewable && (
            <Button variant="outline" onClick={handleOpenInNewTab}>
              Open in New Tab
            </Button>
          )}
          <Button onClick={handleDownload}>
            <DownloadIcon />
            <span className="ml-2">Download</span>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

function formatFileSize(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export type { FilePreviewProps }
