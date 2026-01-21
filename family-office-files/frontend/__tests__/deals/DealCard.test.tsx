import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DealCard } from '@/components/deals/DealCard'
import { Deal } from '@/lib/api'

describe('DealCard', () => {
  const mockDeal: Deal = {
    id: 'test-deal-123',
    title: 'Test Deal Title',
    description: 'This is a test deal description',
    status: 'draft',
    created_by: 'user-123',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: null,
  }

  it('renders deal title', () => {
    render(<DealCard deal={mockDeal} />)
    expect(screen.getByText('Test Deal Title')).toBeInTheDocument()
  })

  it('renders deal description', () => {
    render(<DealCard deal={mockDeal} />)
    expect(screen.getByText('This is a test deal description')).toBeInTheDocument()
  })

  it('renders status badge with draft status', () => {
    render(<DealCard deal={mockDeal} />)
    expect(screen.getByText('Draft')).toBeInTheDocument()
  })

  it('renders status badge with active status', () => {
    const activeDeal: Deal = { ...mockDeal, status: 'active' }
    render(<DealCard deal={activeDeal} />)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('renders status badge with closed status', () => {
    const closedDeal: Deal = { ...mockDeal, status: 'closed' }
    render(<DealCard deal={closedDeal} />)
    expect(screen.getByText('Closed')).toBeInTheDocument()
  })

  it('renders formatted creation date', () => {
    render(<DealCard deal={mockDeal} />)
    // Date format: '15 Jan 2024'
    expect(screen.getByText(/Created.*15 Jan 2024/)).toBeInTheDocument()
  })

  it('links to deal detail page', () => {
    render(<DealCard deal={mockDeal} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/deals/test-deal-123')
  })

  it('shows placeholder text when description is null', () => {
    const dealWithoutDescription: Deal = { ...mockDeal, description: null }
    render(<DealCard deal={dealWithoutDescription} />)
    expect(screen.getByText('No description')).toBeInTheDocument()
  })
})
