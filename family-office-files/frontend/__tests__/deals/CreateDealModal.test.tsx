import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CreateDealModal } from '@/components/deals/CreateDealModal'
import { Deal } from '@/lib/api'

// Create a mock for dealsApi that will be hoisted
const mockCreate = vi.fn()

vi.mock('@/lib/api', () => ({
  dealsApi: {
    get create() { return mockCreate },
  },
}))

describe('CreateDealModal', () => {
  const mockDeal: Deal = {
    id: 'new-deal-123',
    title: 'New Test Deal',
    description: 'Test description',
    status: 'draft',
    created_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: null,
  }

  const mockOnDealCreated = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockCreate.mockReset()
  })

  it('renders create deal button', () => {
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)
    expect(screen.getByRole('button', { name: 'Create Deal' })).toBeInTheDocument()
  })

  it('opens modal when clicking create button', async () => {
    const user = userEvent.setup()
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByText('Create New Deal')).toBeInTheDocument()
    })
    expect(screen.getByLabelText('Title')).toBeInTheDocument()
    expect(screen.getByLabelText('Description (optional)')).toBeInTheDocument()
  })

  it('shows modal header and description', async () => {
    const user = userEvent.setup()
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByText('Create New Deal')).toBeInTheDocument()
    })
    expect(screen.getByText(/Create a new deal to organize files/)).toBeInTheDocument()
  })

  it('submit button is disabled when title is empty', async () => {
    const user = userEvent.setup()
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByText('Create New Deal')).toBeInTheDocument()
    })

    // Find submit button by type within the form
    const form = document.querySelector('form')
    const submitButton = form?.querySelector('button[type="submit"]')
    expect(submitButton).toBeDisabled()
  })

  it('submit button is enabled when title is filled', async () => {
    const user = userEvent.setup()
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByLabelText('Title')).toBeInTheDocument()
    })

    await user.type(screen.getByLabelText('Title'), 'New Test Deal')

    // Find submit button by type within the form
    const form = document.querySelector('form')
    const submitButton = form?.querySelector('button[type="submit"]')
    expect(submitButton).toBeEnabled()
  })

  it('renders Cancel button in modal', async () => {
    const user = userEvent.setup()
    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
    })
  })

  it('title input is interactive', async () => {
    const user = userEvent.setup()

    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByLabelText('Title')).toBeInTheDocument()
    })

    const titleInput = screen.getByLabelText('Title')
    await user.type(titleInput, 'Test Title')
    expect(titleInput).toHaveValue('Test Title')
  })

  it('description input is interactive', async () => {
    const user = userEvent.setup()

    render(<CreateDealModal onDealCreated={mockOnDealCreated} />)

    await user.click(screen.getByRole('button', { name: 'Create Deal' }))

    await waitFor(() => {
      expect(screen.getByLabelText('Description (optional)')).toBeInTheDocument()
    })

    const descriptionInput = screen.getByLabelText('Description (optional)')
    await user.type(descriptionInput, 'Test Description')
    expect(descriptionInput).toHaveValue('Test Description')
  })
})
