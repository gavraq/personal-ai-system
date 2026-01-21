'use client'

import { useState, useEffect, useCallback } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { filesApi, DealFile, FileSource, FileSortBy, SortOrder, FileListOptions } from '@/lib/api'
import { useAuthStore } from '@/lib/auth'
import { FilePreview } from './FilePreview'

// Icons
const DriveIcon = () => (
  <svg className="w-4 h-4 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
    <path d="M4.433 22.396l4-6.928H24l-4 6.928H4.433zM15.653 15.468l-4-6.928 4-6.929 4 6.929-4 6.928zM1.545 15.468L5.545 8.54l4 6.928H1.545z" />
  </svg>
)

const UploadIcon = () => (
  <svg className="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
)

const SortAscIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12l7-7 7 7" />
  </svg>
)

const SortDescIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12l7 7 7-7" />
  </svg>
)

const SearchIcon = () => (
  <svg className="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8" />
    <path d="M21 21l-4.35-4.35" />
  </svg>
)

const DownloadIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
)

const EyeIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)

const TrashIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <line x1="10" y1="11" x2="10" y2="17" />
    <line x1="14" y1="11" x2="14" y2="17" />
  </svg>
)

interface FileListProps {
  dealId: string
  onFileCountChange?: (count: number) => void
  refreshTrigger?: number
  userRole?: string  // Current user's role for the deal (admin, partner, viewer)
}

function formatFileSize(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function getFileTypeLabel(mimeType: string | null): string {
  if (!mimeType) return 'File'
  if (mimeType.includes('pdf')) return 'PDF'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'Document'
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'Spreadsheet'
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'Presentation'
  if (mimeType.startsWith('image/')) return 'Image'
  if (mimeType.includes('text/')) return 'Text'
  if (mimeType.includes('csv')) return 'CSV'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'Archive'
  return 'File'
}

export function FileList({ dealId, onFileCountChange, refreshTrigger, userRole }: FileListProps) {
  const [files, setFiles] = useState<DealFile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deletingFileId, setDeletingFileId] = useState<string | null>(null)

  // Get current user from auth store as fallback
  const { user } = useAuthStore()

  // Use provided userRole or fall back to user's global role
  const effectiveRole = userRole || user?.role || 'viewer'

  // Permission checks
  const canDelete = effectiveRole === 'admin'

  // Filter and sort state
  const [search, setSearch] = useState('')
  const [sourceFilter, setSourceFilter] = useState<FileSource | undefined>(undefined)
  const [sortBy, setSortBy] = useState<FileSortBy>('date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  // Preview state
  const [previewFile, setPreviewFile] = useState<DealFile | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  const loadFiles = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const options: FileListOptions = {
        sortBy,
        sortOrder,
      }
      if (sourceFilter) {
        options.source = sourceFilter
      }
      if (debouncedSearch) {
        options.search = debouncedSearch
      }
      const response = await filesApi.list(dealId, options)
      setFiles(response.files)
      onFileCountChange?.(response.total)
    } catch (err) {
      setError('Failed to load files')
      console.error('Error loading files:', err)
    } finally {
      setIsLoading(false)
    }
  }, [dealId, sourceFilter, debouncedSearch, sortBy, sortOrder, onFileCountChange])

  useEffect(() => {
    loadFiles()
  }, [loadFiles, refreshTrigger])

  const handleDownload = async (file: DealFile) => {
    try {
      const response = await filesApi.getDownloadUrl(file.id)
      window.open(response.download_url, '_blank')
    } catch (err) {
      console.error('Error getting download URL:', err)
    }
  }

  const handlePreview = (file: DealFile) => {
    setPreviewFile(file)
    setPreviewOpen(true)
  }

  const handleDelete = async (file: DealFile) => {
    if (!confirm(`Are you sure you want to delete "${file.name}"? This action cannot be undone.`)) {
      return
    }

    setDeletingFileId(file.id)
    try {
      await filesApi.delete(file.id)
      // Reload files after deletion
      loadFiles()
    } catch (err) {
      console.error('Error deleting file:', err)
      setError('Failed to delete file')
    } finally {
      setDeletingFileId(null)
    }
  }

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  }

  const handleSortByChange = (newSortBy: FileSortBy) => {
    if (sortBy === newSortBy) {
      toggleSortOrder()
    } else {
      setSortBy(newSortBy)
      setSortOrder('asc')
    }
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <SearchIcon />
          </div>
          <Input
            type="text"
            placeholder="Search files..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Source filter */}
        <div className="flex gap-1">
          <Button
            variant={sourceFilter === undefined ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSourceFilter(undefined)}
          >
            All
          </Button>
          <Button
            variant={sourceFilter === 'drive' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSourceFilter(sourceFilter === 'drive' ? undefined : 'drive')}
          >
            <DriveIcon />
            <span className="ml-1">Drive</span>
          </Button>
          <Button
            variant={sourceFilter === 'gcs' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSourceFilter(sourceFilter === 'gcs' ? undefined : 'gcs')}
          >
            <UploadIcon />
            <span className="ml-1">Upload</span>
          </Button>
        </div>
      </div>

      {/* Sort controls */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span>Sort by:</span>
        <Button
          variant={sortBy === 'name' ? 'secondary' : 'ghost'}
          size="sm"
          onClick={() => handleSortByChange('name')}
          className="h-7 px-2"
        >
          Name
          {sortBy === 'name' && (sortOrder === 'asc' ? <SortAscIcon /> : <SortDescIcon />)}
        </Button>
        <Button
          variant={sortBy === 'date' ? 'secondary' : 'ghost'}
          size="sm"
          onClick={() => handleSortByChange('date')}
          className="h-7 px-2"
        >
          Date
          {sortBy === 'date' && (sortOrder === 'asc' ? <SortAscIcon /> : <SortDescIcon />)}
        </Button>
        <Button
          variant={sortBy === 'type' ? 'secondary' : 'ghost'}
          size="sm"
          onClick={() => handleSortByChange('type')}
          className="h-7 px-2"
        >
          Type
          {sortBy === 'type' && (sortOrder === 'asc' ? <SortAscIcon /> : <SortDescIcon />)}
        </Button>
      </div>

      {/* File list */}
      {isLoading ? (
        <div className="py-8 text-center text-muted-foreground">
          Loading files...
        </div>
      ) : error ? (
        <div className="py-8 text-center text-destructive">
          {error}
        </div>
      ) : files.length === 0 ? (
        <div className="py-8 text-center text-muted-foreground">
          {debouncedSearch || sourceFilter ? 'No files match your filters.' : 'No files attached yet.'}
        </div>
      ) : (
        <ul className="divide-y divide-gray-100 rounded-lg border">
          {files.map((file) => (
            <li key={file.id} className="flex items-center justify-between p-3 hover:bg-gray-50">
              <div className="flex items-center gap-3 min-w-0">
                {/* Source icon */}
                {file.source === 'drive' ? <DriveIcon /> : <UploadIcon />}

                {/* File info */}
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{getFileTypeLabel(file.mime_type)}</span>
                    {file.size_bytes && (
                      <>
                        <span>•</span>
                        <span>{formatFileSize(file.size_bytes)}</span>
                      </>
                    )}
                    <span>•</span>
                    <span>{formatDate(file.created_at)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-1 shrink-0">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handlePreview(file)}
                  title="Preview"
                >
                  <EyeIcon />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDownload(file)}
                  title="Download"
                >
                  <DownloadIcon />
                </Button>
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(file)}
                    title="Delete"
                    disabled={deletingFileId === file.id}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <TrashIcon />
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* File count */}
      {!isLoading && !error && files.length > 0 && (
        <p className="text-xs text-muted-foreground text-right">
          {files.length} file{files.length !== 1 ? 's' : ''}
        </p>
      )}

      {/* File preview modal */}
      <FilePreview
        file={previewFile}
        open={previewOpen}
        onOpenChange={setPreviewOpen}
      />
    </div>
  )
}

export type { FileListProps }
