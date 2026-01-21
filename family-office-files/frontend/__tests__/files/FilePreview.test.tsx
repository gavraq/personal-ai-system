import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FilePreview } from '@/components/files/FilePreview'
import { filesApi, DealFile } from '@/lib/api'

// Mock the files API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    filesApi: {
      getDownloadUrl: vi.fn(),
    },
  }
})

describe('FilePreview', () => {
  const mockPdfFile: DealFile = {
    id: 'file-123',
    deal_id: 'deal-456',
    name: 'document.pdf',
    source: 'gcs',
    source_id: 'gcs-path/document.pdf',
    mime_type: 'application/pdf',
    size_bytes: 1024000,
    uploaded_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
  }

  const mockImageFile: DealFile = {
    id: 'file-124',
    deal_id: 'deal-456',
    name: 'photo.jpg',
    source: 'gcs',
    source_id: 'gcs-path/photo.jpg',
    mime_type: 'image/jpeg',
    size_bytes: 512000,
    uploaded_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
  }

  const mockDriveFile: DealFile = {
    id: 'file-125',
    deal_id: 'deal-456',
    name: 'spreadsheet.xlsx',
    source: 'drive',
    source_id: 'drive-file-id-abc',
    mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    size_bytes: 256000,
    uploaded_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
  }

  const mockUnsupportedFile: DealFile = {
    id: 'file-126',
    deal_id: 'deal-456',
    name: 'archive.zip',
    source: 'gcs',
    source_id: 'gcs-path/archive.zip',
    mime_type: 'application/zip',
    size_bytes: 2048000,
    uploaded_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
  }

  const mockOnOpenChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders PDF in modal with iframe', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValueOnce({
      id: mockPdfFile.id,
      name: mockPdfFile.name,
      download_url: 'https://storage.example.com/signed-url/document.pdf',
      expires_in_minutes: 60,
    })

    render(
      <FilePreview
        file={mockPdfFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    // Should show file name in title
    expect(screen.getByText('document.pdf')).toBeInTheDocument()

    // Should show loading initially
    expect(screen.getByText('Loading preview...')).toBeInTheDocument()

    // Wait for iframe to appear
    await waitFor(() => {
      const iframe = screen.getByTitle('Preview of document.pdf')
      expect(iframe).toBeInTheDocument()
      expect(iframe).toHaveAttribute('src', 'https://storage.example.com/signed-url/document.pdf')
    })
  })

  it('renders image preview correctly', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValueOnce({
      id: mockImageFile.id,
      name: mockImageFile.name,
      download_url: 'https://storage.example.com/signed-url/photo.jpg',
      expires_in_minutes: 60,
    })

    render(
      <FilePreview
        file={mockImageFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    expect(screen.getByText('photo.jpg')).toBeInTheDocument()

    await waitFor(() => {
      const img = screen.getByAltText('photo.jpg')
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src', 'https://storage.example.com/signed-url/photo.jpg')
    })
  })

  it('renders Drive file with Google Drive preview URL', async () => {
    render(
      <FilePreview
        file={mockDriveFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    expect(screen.getByText('spreadsheet.xlsx')).toBeInTheDocument()

    // Drive files don't call getDownloadUrl for preview - they use drive URL directly
    await waitFor(() => {
      const iframe = screen.getByTitle('Preview of spreadsheet.xlsx')
      expect(iframe).toBeInTheDocument()
      expect(iframe).toHaveAttribute('src', 'https://drive.google.com/file/d/drive-file-id-abc/preview')
    })
  })

  it('shows fallback message for unsupported file types', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValueOnce({
      id: mockUnsupportedFile.id,
      name: mockUnsupportedFile.name,
      download_url: 'https://storage.example.com/signed-url/archive.zip',
      expires_in_minutes: 60,
    })

    render(
      <FilePreview
        file={mockUnsupportedFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Preview not available for this file type')).toBeInTheDocument()
      expect(screen.getByText('Archive')).toBeInTheDocument()
    })
  })

  it('provides download button', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValue({
      id: mockPdfFile.id,
      name: mockPdfFile.name,
      download_url: 'https://storage.example.com/signed-url/document.pdf',
      expires_in_minutes: 60,
    })

    render(
      <FilePreview
        file={mockPdfFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Download/i })).toBeInTheDocument()
    })
  })

  it('calls download API when download button clicked', async () => {
    const user = userEvent.setup()
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValue({
      id: mockUnsupportedFile.id,
      name: mockUnsupportedFile.name,
      download_url: 'https://storage.example.com/signed-url/archive.zip',
      expires_in_minutes: 60,
    })

    // Mock window.open
    const mockOpen = vi.fn()
    window.open = mockOpen

    render(
      <FilePreview
        file={mockUnsupportedFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Download/i })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /Download/i }))

    await waitFor(() => {
      expect(filesApi.getDownloadUrl).toHaveBeenCalledWith(mockUnsupportedFile.id)
      expect(mockOpen).toHaveBeenCalledWith('https://storage.example.com/signed-url/archive.zip', '_blank')
    })
  })

  it('shows error message when preview fails to load', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockRejectedValueOnce(new Error('Network error'))

    render(
      <FilePreview
        file={mockPdfFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Failed to load preview')).toBeInTheDocument()
    })
  })

  it('displays file size in description', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValueOnce({
      id: mockPdfFile.id,
      name: mockPdfFile.name,
      download_url: 'https://storage.example.com/signed-url/document.pdf',
      expires_in_minutes: 60,
    })

    render(
      <FilePreview
        file={mockPdfFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    // PDF file is 1024000 bytes = 1000 KB
    await waitFor(() => {
      expect(screen.getByText(/1000 KB/)).toBeInTheDocument()
    })
  })

  it('renders nothing when file is null', () => {
    const { container } = render(
      <FilePreview
        file={null}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    // Should render nothing
    expect(container.firstChild).toBeNull()
  })

  it('closes modal when open changes to false', async () => {
    vi.mocked(filesApi.getDownloadUrl).mockResolvedValueOnce({
      id: mockPdfFile.id,
      name: mockPdfFile.name,
      download_url: 'https://storage.example.com/signed-url/document.pdf',
      expires_in_minutes: 60,
    })

    const { rerender } = render(
      <FilePreview
        file={mockPdfFile}
        open={true}
        onOpenChange={mockOnOpenChange}
      />
    )

    expect(screen.getByText('document.pdf')).toBeInTheDocument()

    rerender(
      <FilePreview
        file={mockPdfFile}
        open={false}
        onOpenChange={mockOnOpenChange}
      />
    )

    await waitFor(() => {
      expect(screen.queryByText('document.pdf')).not.toBeInTheDocument()
    })
  })
})
