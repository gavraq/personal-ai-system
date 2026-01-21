import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EditDealModal } from '@/components/deals/EditDealModal'
import { dealsApi, Deal } from '@/lib/api'

// Mock the deals API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    dealsApi: {
      update: vi.fn(),
    },
  }
})

describe('EditDealModal', () => {
  const mockDraftDeal: Deal = {
    id: 'deal-123',
    title: 'Original Title',
    description: 'Original description',
    status: 'draft',
    created_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: null,
  }

  const mockActiveDeal: Deal = {
    ...mockDraftDeal,
    status: 'active',
  }

  const mockClosedDeal: Deal = {
    ...mockDraftDeal,
    status: 'closed',
  }

  const mockOnDealUpdated = vi.fn()
  const mockOnOpenChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with deal title pre-filled', () => {
    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByLabelText('Title')).toHaveValue('Original Title')
  })

  it('renders with deal description pre-filled', () => {
    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByLabelText('Description')).toHaveValue('Original description')
  })

  it('updates title in real-time as user types', async () => {
    const user = userEvent.setup()

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    const titleInput = screen.getByLabelText('Title')
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    expect(titleInput).toHaveValue('Updated Title')
  })

  it('updates description in real-time as user types', async () => {
    const user = userEvent.setup()

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    const descriptionInput = screen.getByLabelText('Description')
    await user.clear(descriptionInput)
    await user.type(descriptionInput, 'Updated description')

    expect(descriptionInput).toHaveValue('Updated description')
  })

  it('calls API with updated values on save', async () => {
    const user = userEvent.setup()
    const updatedDeal: Deal = {
      ...mockDraftDeal,
      title: 'Updated Title',
      description: 'Updated description',
    }
    vi.mocked(dealsApi.update).mockResolvedValueOnce(updatedDeal)

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    const titleInput = screen.getByLabelText('Title')
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    const descriptionInput = screen.getByLabelText('Description')
    await user.clear(descriptionInput)
    await user.type(descriptionInput, 'Updated description')

    await user.click(screen.getByRole('button', { name: 'Save Changes' }))

    await waitFor(() => {
      expect(dealsApi.update).toHaveBeenCalledWith('deal-123', {
        title: 'Updated Title',
        description: 'Updated description',
        status: undefined, // Status didn't change
      })
    })

    await waitFor(() => {
      expect(mockOnDealUpdated).toHaveBeenCalledWith(updatedDeal)
    })
  })

  it('displays save button text as Saving during API call', async () => {
    const user = userEvent.setup()
    // Create a promise that won't resolve immediately
    let resolveUpdate: (value: Deal) => void
    vi.mocked(dealsApi.update).mockReturnValueOnce(
      new Promise((resolve) => {
        resolveUpdate = resolve
      })
    )

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Save Changes' }))

    expect(screen.getByRole('button', { name: 'Saving...' })).toBeInTheDocument()

    // Cleanup: resolve the promise
    resolveUpdate!(mockDraftDeal)
  })

  it('displays error message on API failure', async () => {
    const user = userEvent.setup()
    vi.mocked(dealsApi.update).mockRejectedValueOnce({
      response: { data: { detail: 'Update failed' } },
    })

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Save Changes' }))

    await waitFor(() => {
      expect(screen.getByText('Update failed')).toBeInTheDocument()
    })
  })

  it('disables all inputs for closed deals', () => {
    render(
      <EditDealModal
        deal={mockClosedDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByLabelText('Title')).toBeDisabled()
    expect(screen.getByLabelText('Description')).toBeDisabled()
    expect(screen.queryByRole('button', { name: 'Save Changes' })).not.toBeInTheDocument()
  })

  it('shows message that closed deal cannot be edited', () => {
    render(
      <EditDealModal
        deal={mockClosedDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByText('This deal is closed and cannot be edited.')).toBeInTheDocument()
  })

  it('allows draft to transition to active', () => {
    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    // Status selector should be present
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    // Should show status transition hint
    expect(screen.getByText(/Status can only transition forward/)).toBeInTheDocument()
  })

  it('closes modal on cancel', async () => {
    const user = userEvent.setup()

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(mockOnOpenChange).toHaveBeenCalledWith(false)
  })

  it('closes modal after successful save', async () => {
    const user = userEvent.setup()
    vi.mocked(dealsApi.update).mockResolvedValueOnce(mockDraftDeal)

    render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Save Changes' }))

    await waitFor(() => {
      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })
  })

  it('updates form when deal prop changes', () => {
    const { rerender } = render(
      <EditDealModal
        deal={mockDraftDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByLabelText('Title')).toHaveValue('Original Title')

    // Update with new deal
    const newDeal: Deal = { ...mockDraftDeal, title: 'New Title', description: 'New description' }
    rerender(
      <EditDealModal
        deal={newDeal}
        open={true}
        onOpenChange={mockOnOpenChange}
        onDealUpdated={mockOnDealUpdated}
      />
    )

    expect(screen.getByLabelText('Title')).toHaveValue('New Title')
    expect(screen.getByLabelText('Description')).toHaveValue('New description')
  })
})
