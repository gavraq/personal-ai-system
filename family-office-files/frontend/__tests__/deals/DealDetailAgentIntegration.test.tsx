import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AgentPanel } from '@/components/agents/AgentPanel'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { agentsApi, activityApi, DealFile, Activity } from '@/lib/api'

// Mock the APIs
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    activityApi: {
      listForDeal: vi.fn(),
      list: vi.fn(),
    },
    agentsApi: {
      listDealRuns: vi.fn(),
      getMessages: vi.fn(),
      startRun: vi.fn(),
      getRun: vi.fn(),
    },
  }
})

describe('Deal Detail Page - Agent Integration', () => {
  const mockDealId = 'deal-123'
  const mockDealTitle = 'Test Deal'

  const mockFiles: DealFile[] = [
    {
      id: 'file-1',
      deal_id: mockDealId,
      name: 'quarterly-report.pdf',
      source: 'gcs',
      source_id: 'gcs-123',
      mime_type: 'application/pdf',
      size_bytes: 102400,
      uploaded_by: 'user-1',
      created_at: new Date().toISOString(),
    },
    {
      id: 'file-2',
      deal_id: mockDealId,
      name: 'financials.xlsx',
      source: 'drive',
      source_id: 'drive-456',
      mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      size_bytes: 51200,
      uploaded_by: 'user-1',
      created_at: new Date().toISOString(),
    },
  ]

  const mockActivities: Activity[] = [
    {
      id: 'act-1',
      deal_id: mockDealId,
      actor_id: 'user-1',
      actor_email: 'admin@test.com',
      action: 'deal_create',
      details: { title: 'Test Deal' },
      created_at: new Date().toISOString(),
    },
    {
      id: 'act-2',
      deal_id: mockDealId,
      actor_id: 'user-1',
      actor_email: 'admin@test.com',
      action: 'agent_run',
      details: { agent_type: 'market_research', query: 'Analyze market' },
      created_at: new Date().toISOString(),
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(activityApi.listForDeal).mockResolvedValue({
      activities: mockActivities,
      total: 2,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [],
      total: 0,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: [],
      total: 0,
    })
  })

  describe('AgentPanel integration', () => {
    it('renders agent panel with all tabs', async () => {
      render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

      expect(screen.getByText('AI Agents')).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /market/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /doc/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /due diligence|dd/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /news/i })).toBeInTheDocument()
    })

    it('displays file count', () => {
      render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)
      expect(screen.getByText('2 files available')).toBeInTheDocument()
    })

    it('shows quick file actions when on Document Analysis tab', async () => {
      render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

      const docsTab = screen.getByRole('tab', { name: /doc/i })
      await userEvent.click(docsTab)

      await waitFor(() => {
        expect(screen.getByText('Quick analyze a file:')).toBeInTheDocument()
        expect(screen.getByText(/quarterly-report.pdf/)).toBeInTheDocument()
      })
    })

    it('passes deal title as context to agent chat', async () => {
      render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

      // Deal title should appear in the description
      await waitFor(() => {
        expect(screen.getByText(/Test Deal/)).toBeInTheDocument()
      })
    })
  })

  describe('ActivityFeed integration', () => {
    it('renders activity feed for a specific deal', async () => {
      render(
        <ActivityFeed dealId={mockDealId} pageSize={10} autoRefresh={false} />
      )

      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      })
    })

    it('fetches activities for the specific deal', async () => {
      render(
        <ActivityFeed dealId={mockDealId} pageSize={10} autoRefresh={false} />
      )

      await waitFor(() => {
        expect(activityApi.listForDeal).toHaveBeenCalledWith(mockDealId, 1, 10)
      })
    })

    it('displays agent_run activities with correct icon', async () => {
      render(
        <ActivityFeed dealId={mockDealId} pageSize={10} autoRefresh={false} />
      )

      await waitFor(() => {
        // Agent run activity should show robot icon
        expect(screen.getByText('🤖')).toBeInTheDocument()
      })
    })

    it('shows deal create activity', async () => {
      render(
        <ActivityFeed dealId={mockDealId} pageSize={10} autoRefresh={false} />
      )

      await waitFor(() => {
        expect(screen.getByText(/admin@test.com created this deal/)).toBeInTheDocument()
      })
    })
  })

  describe('Integration between components', () => {
    it('agent panel can trigger document analysis on file click', async () => {
      render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

      // Go to document analysis tab
      const docsTab = screen.getByRole('tab', { name: /doc/i })
      await userEvent.click(docsTab)

      // Click on a file to analyze
      await waitFor(() => {
        expect(screen.getByText(/quarterly-report.pdf/)).toBeInTheDocument()
      })

      const fileButton = screen.getByText(/quarterly-report.pdf/).closest('button')
      if (fileButton) {
        await userEvent.click(fileButton)

        // File should be highlighted
        expect(fileButton).toHaveClass('bg-primary')
      }
    })

    it('activity feed shows agent runs when completed', async () => {
      // Simulate an agent run completion appearing in activity feed
      vi.mocked(activityApi.listForDeal).mockResolvedValue({
        activities: [
          {
            id: 'act-agent',
            deal_id: mockDealId,
            actor_id: 'user-1',
            actor_email: 'admin@test.com',
            action: 'agent_run',
            details: { agent_type: 'market_research', summary: 'Market analysis complete' },
            created_at: new Date().toISOString(),
          },
        ],
        total: 1,
        page: 1,
        page_size: 10,
      })

      render(
        <ActivityFeed dealId={mockDealId} pageSize={10} autoRefresh={false} />
      )

      await waitFor(() => {
        expect(screen.getByText(/ran an agent/)).toBeInTheDocument()
      })
    })
  })
})
