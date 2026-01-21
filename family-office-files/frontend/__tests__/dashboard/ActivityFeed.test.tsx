import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { activityApi, Activity } from '@/lib/api'

// Mock the activity API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    activityApi: {
      list: vi.fn(),
      listForDeal: vi.fn(),
    },
  }
})

describe('ActivityFeed', () => {
  const mockActivities: Activity[] = [
    {
      id: 'act-1',
      deal_id: 'deal-1',
      actor_id: 'user-1',
      actor_email: 'admin@test.com',
      action: 'deal_create',
      details: { title: 'Test Deal' },
      created_at: new Date().toISOString(),
    },
    {
      id: 'act-2',
      deal_id: 'deal-1',
      actor_id: 'user-1',
      actor_email: 'admin@test.com',
      action: 'file_upload',
      details: { file_name: 'document.pdf' },
      created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    },
    {
      id: 'act-3',
      deal_id: 'deal-1',
      actor_id: 'user-2',
      actor_email: 'partner@test.com',
      action: 'member_add',
      details: { user_email: 'viewer@test.com' },
      created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(activityApi.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    render(<ActivityFeed autoRefresh={false} />)
    // Loading skeleton should be visible
    expect(screen.getByText('Recent Activity')).toBeInTheDocument()
  })

  it('renders activities after loading', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: mockActivities,
      total: 3,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText(/admin@test.com created this deal/)).toBeInTheDocument()
    })
  })

  it('displays actor email in activity description', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: mockActivities,
      total: 3,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      // Check for actor email in descriptions
      expect(screen.getByText(/admin@test.com/)).toBeInTheDocument()
    })
  })

  it('renders file upload activity correctly', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: mockActivities,
      total: 3,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText(/uploaded "document.pdf"/)).toBeInTheDocument()
    })
  })

  it('renders member add activity correctly', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: mockActivities,
      total: 3,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText(/added viewer@test.com/)).toBeInTheDocument()
    })
  })

  it('renders empty state when no activities', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: [],
      total: 0,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('No activity yet')).toBeInTheDocument()
    })
  })

  it('renders error state on API failure', async () => {
    vi.mocked(activityApi.list).mockRejectedValue(new Error('API Error'))

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load activities')).toBeInTheDocument()
    })
  })

  it('uses listForDeal when dealId is provided', async () => {
    vi.mocked(activityApi.listForDeal).mockResolvedValue({
      activities: mockActivities,
      total: 3,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed dealId="deal-123" autoRefresh={false} />)

    await waitFor(() => {
      expect(activityApi.listForDeal).toHaveBeenCalledWith('deal-123', 1, 10)
    })
  })

  it('displays relative timestamps', async () => {
    const recentActivity: Activity = {
      id: 'act-recent',
      deal_id: 'deal-1',
      actor_id: 'user-1',
      actor_email: 'admin@test.com',
      action: 'deal_create',
      details: null,
      created_at: new Date().toISOString(), // Just now
    }

    vi.mocked(activityApi.list).mockResolvedValue({
      activities: [recentActivity],
      total: 1,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('just now')).toBeInTheDocument()
    })
  })

  it('renders avatar with first letter of email', async () => {
    vi.mocked(activityApi.list).mockResolvedValue({
      activities: mockActivities.slice(0, 1),
      total: 1,
      page: 1,
      page_size: 10,
    })

    render(<ActivityFeed autoRefresh={false} />)

    await waitFor(() => {
      // Avatar should show 'A' for admin@test.com
      expect(screen.getByTitle('admin@test.com')).toBeInTheDocument()
      expect(screen.getByText('A')).toBeInTheDocument()
    })
  })
})
