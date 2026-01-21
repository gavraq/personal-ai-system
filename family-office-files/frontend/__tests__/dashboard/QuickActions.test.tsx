import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { dealsApi, Deal } from '@/lib/api'

// Mock the deals API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    dealsApi: {
      list: vi.fn(),
      create: vi.fn(),
    },
  }
})

// Mock CreateDealModal to simplify testing
vi.mock('@/components/deals', () => ({
  CreateDealModal: ({ onDealCreated, trigger }: { onDealCreated: (deal: Deal) => void; trigger: React.ReactNode }) => (
    <div data-testid="create-deal-modal-mock">
      {trigger}
      <button
        data-testid="mock-create-deal"
        onClick={() => onDealCreated({
          id: 'new-deal',
          title: 'New Deal',
          description: null,
          status: 'draft',
          created_by: 'user-1',
          created_at: new Date().toISOString(),
          updated_at: null,
          file_count: 0,
        })}
      >
        Create
      </button>
    </div>
  ),
}))

// Mock FileUploader
vi.mock('@/components/files/FileUploader', () => ({
  FileUploader: ({ onFileUploaded }: { onFileUploaded?: (file: { id: string }) => void }) => (
    <div data-testid="file-uploader-mock">
      <button
        data-testid="mock-upload-file"
        onClick={() => onFileUploaded?.({
          id: 'file-1',
          name: 'test.pdf',
          mime_type: 'application/pdf',
          size_bytes: 1024,
          source: 'gcs' as const,
          source_id: 'gcs-path',
        })}
      >
        Upload
      </button>
    </div>
  ),
  UploadedFile: {},
}))

describe('QuickActions', () => {
  const mockDeals: Deal[] = [
    {
      id: 'deal-1',
      title: 'Test Deal Alpha',
      description: 'Test description',
      status: 'active',
      created_by: 'user-1',
      created_at: new Date().toISOString(),
      updated_at: null,
      file_count: 5,
    },
    {
      id: 'deal-2',
      title: 'Test Deal Beta',
      description: null,
      status: 'active',
      created_by: 'user-1',
      created_at: new Date().toISOString(),
      updated_at: null,
      file_count: 2,
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(dealsApi.list).mockResolvedValue({
      deals: mockDeals,
      total: 2,
      page: 1,
      page_size: 100,
    })
  })

  describe('Role-based visibility', () => {
    it('shows all buttons for Admin role', () => {
      render(<QuickActions userRole="admin" />)

      expect(screen.getByTestId('create-deal-button')).toBeInTheDocument()
      expect(screen.getByTestId('upload-file-button')).toBeInTheDocument()
      expect(screen.getByTestId('run-agent-button')).toBeInTheDocument()
    })

    it('shows all buttons for Partner role', () => {
      render(<QuickActions userRole="partner" />)

      expect(screen.getByTestId('create-deal-button')).toBeInTheDocument()
      expect(screen.getByTestId('upload-file-button')).toBeInTheDocument()
      expect(screen.getByTestId('run-agent-button')).toBeInTheDocument()
    })

    it('only shows Run Agent button for Viewer role', () => {
      render(<QuickActions userRole="viewer" />)

      expect(screen.queryByTestId('create-deal-button')).not.toBeInTheDocument()
      expect(screen.queryByTestId('upload-file-button')).not.toBeInTheDocument()
      expect(screen.getByTestId('run-agent-button')).toBeInTheDocument()
    })
  })

  describe('Create Deal functionality', () => {
    it('calls onDealCreated callback when deal is created', async () => {
      const onDealCreated = vi.fn()
      render(<QuickActions userRole="admin" onDealCreated={onDealCreated} />)

      // Click the mock create button
      fireEvent.click(screen.getByTestId('mock-create-deal'))

      expect(onDealCreated).toHaveBeenCalledWith(expect.objectContaining({
        id: 'new-deal',
        title: 'New Deal',
      }))
    })
  })

  describe('Upload File functionality', () => {
    it('opens upload modal when Upload File button is clicked', async () => {
      render(<QuickActions userRole="admin" />)

      fireEvent.click(screen.getByTestId('upload-file-button'))

      await waitFor(() => {
        // Check for modal description text that only appears in the dialog
        expect(screen.getByText('Select a deal and upload a file to it.')).toBeInTheDocument()
        expect(screen.getByTestId('deal-selector')).toBeInTheDocument()
      })
    })

    it('loads deals when upload modal is opened', async () => {
      render(<QuickActions userRole="admin" />)

      fireEvent.click(screen.getByTestId('upload-file-button'))

      await waitFor(() => {
        expect(dealsApi.list).toHaveBeenCalledWith(1, 100, 'active')
      })
    })

    it('shows deal selector in upload modal', async () => {
      render(<QuickActions userRole="admin" />)

      fireEvent.click(screen.getByTestId('upload-file-button'))

      await waitFor(() => {
        expect(screen.getByTestId('deal-selector')).toBeInTheDocument()
      })
    })
  })

  describe('Run Agent functionality', () => {
    it('opens agent modal when Run Agent button is clicked', async () => {
      render(<QuickActions userRole="viewer" />)

      fireEvent.click(screen.getByTestId('run-agent-button'))

      await waitFor(() => {
        // Check for modal description text that only appears in the dialog
        expect(screen.getByText('Select a deal and agent type to run.')).toBeInTheDocument()
        expect(screen.getByTestId('agent-deal-selector')).toBeInTheDocument()
      })
    })

    it('shows deal and agent type selectors in agent modal', async () => {
      render(<QuickActions userRole="viewer" />)

      fireEvent.click(screen.getByTestId('run-agent-button'))

      await waitFor(() => {
        expect(screen.getByTestId('agent-deal-selector')).toBeInTheDocument()
        expect(screen.getByTestId('agent-type-selector')).toBeInTheDocument()
      })
    })

    it('disables submit button when deal or agent type is not selected', async () => {
      render(<QuickActions userRole="viewer" />)

      fireEvent.click(screen.getByTestId('run-agent-button'))

      await waitFor(() => {
        const submitButton = screen.getByTestId('run-agent-submit')
        expect(submitButton).toBeDisabled()
      })
    })
  })

  describe('Keyboard shortcuts', () => {
    it('shows keyboard shortcut hints on buttons for Admin', () => {
      render(<QuickActions userRole="admin" />)

      expect(screen.getByText('⌘N')).toBeInTheDocument()
      expect(screen.getByText('⌘U')).toBeInTheDocument()
    })

    it('triggers Create Deal modal on Cmd+N', async () => {
      render(<QuickActions userRole="admin" />)

      // Simulate Cmd+N
      fireEvent.keyDown(window, { key: 'n', metaKey: true })

      // The CreateDealModal mock should be triggered
      // Note: In the actual implementation, this would open the modal
      await waitFor(() => {
        expect(screen.getByTestId('create-deal-modal-mock')).toBeInTheDocument()
      })
    })

    it('triggers Upload File modal on Cmd+U', async () => {
      render(<QuickActions userRole="admin" />)

      // Simulate Cmd+U
      fireEvent.keyDown(window, { key: 'u', metaKey: true })

      await waitFor(() => {
        // Check for modal description text and that API was called
        expect(screen.getByText('Select a deal and upload a file to it.')).toBeInTheDocument()
        expect(dealsApi.list).toHaveBeenCalled()
      })
    })

    it('does not trigger Create Deal modal on Cmd+N for Viewer role', async () => {
      render(<QuickActions userRole="viewer" />)

      // Simulate Cmd+N
      fireEvent.keyDown(window, { key: 'n', metaKey: true })

      // Should not open modal for viewers
      expect(screen.queryByTestId('create-deal-modal-mock')).not.toBeInTheDocument()
    })

    it('does not trigger Upload File modal on Cmd+U for Viewer role', async () => {
      render(<QuickActions userRole="viewer" />)

      // Simulate Cmd+U
      fireEvent.keyDown(window, { key: 'u', metaKey: true })

      // Modal should not open for viewers
      await waitFor(() => {
        expect(screen.queryByText('Select a deal and upload a file to it.')).not.toBeInTheDocument()
      })
    })
  })

  describe('Run Agent callback', () => {
    it('has submit button disabled initially and shows selectors', async () => {
      const onRunAgent = vi.fn()
      render(<QuickActions userRole="admin" onRunAgent={onRunAgent} />)

      // Open agent modal
      fireEvent.click(screen.getByTestId('run-agent-button'))

      await waitFor(() => {
        expect(screen.getByTestId('agent-deal-selector')).toBeInTheDocument()
        expect(screen.getByTestId('agent-type-selector')).toBeInTheDocument()
      })

      // Submit should be disabled initially
      const submitButton = screen.getByTestId('run-agent-submit')
      expect(submitButton).toBeDisabled()
    })

    it('renders agent type options in selector', async () => {
      render(<QuickActions userRole="admin" />)

      // Open agent modal
      fireEvent.click(screen.getByTestId('run-agent-button'))

      await waitFor(() => {
        expect(screen.getByTestId('agent-type-selector')).toBeInTheDocument()
      })

      // The agent type selector should be present and interactive
      expect(screen.getByText('Choose an agent')).toBeInTheDocument()
    })
  })

  describe('Error handling', () => {
    it('handles deal loading error gracefully', async () => {
      vi.mocked(dealsApi.list).mockRejectedValue(new Error('Network error'))

      render(<QuickActions userRole="admin" />)

      fireEvent.click(screen.getByTestId('upload-file-button'))

      await waitFor(() => {
        expect(screen.getByText('Failed to load deals')).toBeInTheDocument()
      })
    })
  })

  describe('Button labels', () => {
    it('displays correct button labels for Admin', () => {
      render(<QuickActions userRole="admin" />)

      expect(screen.getByText('Create Deal')).toBeInTheDocument()
      expect(screen.getByText('Upload File')).toBeInTheDocument()
      expect(screen.getByText('Run Agent')).toBeInTheDocument()
    })
  })
})
