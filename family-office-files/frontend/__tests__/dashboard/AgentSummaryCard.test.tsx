import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { AgentSummaryCard } from '@/components/dashboard/AgentSummaryCard'
import { agentsApi, AgentSummary, AgentRun } from '@/lib/api'

// Mock the agents API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    agentsApi: {
      listSummaries: vi.fn(),
      getRun: vi.fn(),
    },
  }
})

describe('AgentSummaryCard', () => {
  const mockSummaries: AgentSummary[] = [
    {
      id: 'run-1',
      deal_id: 'deal-1',
      deal_title: 'Test Deal Alpha',
      agent_type: 'market_research',
      status: 'completed',
      summary_excerpt: 'Market analysis shows strong growth potential in the tech sector...',
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    },
    {
      id: 'run-2',
      deal_id: 'deal-2',
      deal_title: 'Test Deal Beta',
      agent_type: 'document_analysis',
      status: 'completed',
      summary_excerpt: 'Document review complete. Key findings include...',
      started_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      completed_at: new Date(Date.now() - 3500000).toISOString(),
    },
    {
      id: 'run-3',
      deal_id: 'deal-3',
      deal_title: 'Test Deal Gamma',
      agent_type: 'due_diligence',
      status: 'failed',
      summary_excerpt: null,
      started_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      completed_at: new Date(Date.now() - 86300000).toISOString(),
    },
  ]

  const mockAgentRun: AgentRun = {
    id: 'run-1',
    deal_id: 'deal-1',
    user_id: 'user-1',
    user_email: 'admin@test.com',
    agent_type: 'market_research',
    status: 'completed',
    input: { query: 'tech sector analysis' },
    output: { summary: 'Detailed market analysis...', findings: ['Growth trend 1', 'Growth trend 2'] },
    error_message: null,
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(agentsApi.listSummaries).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    render(<AgentSummaryCard autoRefresh={false} />)
    expect(screen.getByText('Agent Outputs')).toBeInTheDocument()
    expect(screen.getByText('Latest AI agent results')).toBeInTheDocument()
  })

  it('renders agent summaries after loading', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries,
      total: 3,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Test Deal Alpha')).toBeInTheDocument()
      expect(screen.getByText('Test Deal Beta')).toBeInTheDocument()
    })
  })

  it('displays correct agent type labels', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries,
      total: 3,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Market Research')).toBeInTheDocument()
      expect(screen.getByText('Document Analysis')).toBeInTheDocument()
      expect(screen.getByText('Due Diligence')).toBeInTheDocument()
    })
  })

  it('displays status badges with correct colors', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries,
      total: 3,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      const completedBadges = screen.getAllByText('completed')
      expect(completedBadges.length).toBe(2)
      const failedBadge = screen.getByText('failed')
      expect(failedBadge).toBeInTheDocument()
    })
  })

  it('displays summary excerpts', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries,
      total: 3,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText(/Market analysis shows strong growth/)).toBeInTheDocument()
      expect(screen.getByText(/Document review complete/)).toBeInTheDocument()
    })
  })

  it('renders empty state when no agent summaries', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: [],
      total: 0,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('No agent runs yet')).toBeInTheDocument()
      expect(screen.getByText(/Run an agent on a deal/)).toBeInTheDocument()
    })
  })

  it('renders error state on API failure', async () => {
    vi.mocked(agentsApi.listSummaries).mockRejectedValue(new Error('API Error'))

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load agent summaries')).toBeInTheDocument()
    })
  })

  it('opens modal when clicking on a summary', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: [mockSummaries[0]],
      total: 1,
    })
    vi.mocked(agentsApi.getRun).mockResolvedValue(mockAgentRun)

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Test Deal Alpha')).toBeInTheDocument()
    })

    // Click on the summary item
    const summaryItem = screen.getByText('Market Research')
    fireEvent.click(summaryItem)

    // Modal should open and show full output
    await waitFor(() => {
      expect(agentsApi.getRun).toHaveBeenCalledWith('run-1')
    })
  })

  it('displays relative timestamps', async () => {
    const recentSummary: AgentSummary = {
      id: 'run-recent',
      deal_id: 'deal-1',
      deal_title: 'Recent Deal',
      agent_type: 'news_alerts',
      status: 'completed',
      summary_excerpt: 'Latest news...',
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    }

    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: [recentSummary],
      total: 1,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('just now')).toBeInTheDocument()
    })
  })

  it('displays agent type icons', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries,
      total: 3,
    })

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      // Market research icon
      expect(screen.getByText('Market Research').closest('div')?.parentElement?.textContent).toContain('Market Research')
    })
  })

  it('calls onRerun callback when re-run button is clicked', async () => {
    const onRerun = vi.fn()
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: [mockSummaries[0]],
      total: 1,
    })
    vi.mocked(agentsApi.getRun).mockResolvedValue(mockAgentRun)

    render(<AgentSummaryCard autoRefresh={false} onRerun={onRerun} />)

    await waitFor(() => {
      expect(screen.getByText('Test Deal Alpha')).toBeInTheDocument()
    })

    // Click on the summary item to open modal
    fireEvent.click(screen.getByText('Market Research'))

    // Wait for modal to load
    await waitFor(() => {
      expect(screen.getByText('Re-run Agent')).toBeInTheDocument()
    })

    // Click re-run button
    fireEvent.click(screen.getByText('Re-run Agent'))

    expect(onRerun).toHaveBeenCalledWith('run-1', 'market_research', 'deal-1')
  })

  it('respects limit prop', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: mockSummaries.slice(0, 2),
      total: 2,
    })

    render(<AgentSummaryCard limit={2} autoRefresh={false} />)

    await waitFor(() => {
      expect(agentsApi.listSummaries).toHaveBeenCalledWith(2)
    })
  })

  it('shows full output in modal when expanded', async () => {
    vi.mocked(agentsApi.listSummaries).mockResolvedValue({
      summaries: [mockSummaries[0]],
      total: 1,
    })
    vi.mocked(agentsApi.getRun).mockResolvedValue(mockAgentRun)

    render(<AgentSummaryCard autoRefresh={false} />)

    await waitFor(() => {
      expect(screen.getByText('Test Deal Alpha')).toBeInTheDocument()
    })

    // Click to open modal
    fireEvent.click(screen.getByText('Market Research'))

    // Wait for modal content to load
    await waitFor(() => {
      // Should show input and output sections
      expect(screen.getByText('Input')).toBeInTheDocument()
      expect(screen.getByText('Output')).toBeInTheDocument()
    })
  })
})
