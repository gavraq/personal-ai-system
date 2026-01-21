import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AgentPanel } from '@/components/agents/AgentPanel'
import { agentsApi, DealFile, AgentRun } from '@/lib/api'

// Mock the agents API
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return {
    ...actual,
    agentsApi: {
      listDealRuns: vi.fn(),
      getMessages: vi.fn(),
      startRun: vi.fn(),
      getRun: vi.fn(),
    },
  }
})

describe('AgentPanel', () => {
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

  beforeEach(() => {
    vi.clearAllMocks()
    // Default mocks - empty history
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

  it('renders all four agent type tabs', async () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Check all tabs are present
    expect(screen.getByRole('tab', { name: /market/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /doc/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /due diligence|dd/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /news/i })).toBeInTheDocument()
  })

  it('shows AI Agents header', () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} />)

    expect(screen.getByText('AI Agents')).toBeInTheDocument()
  })

  it('displays file count when files are provided', () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

    expect(screen.getByText('2 files available')).toBeInTheDocument()
  })

  it('shows singular "file" when only one file', () => {
    render(
      <AgentPanel
        dealId={mockDealId}
        dealTitle={mockDealTitle}
        files={[mockFiles[0]]}
      />
    )

    expect(screen.getByText('1 file available')).toBeInTheDocument()
  })

  it('switches tabs when clicked', async () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Click on Due Diligence tab
    const ddTab = screen.getByRole('tab', { name: /due diligence|dd/i })
    await userEvent.click(ddTab)

    // Tab should be selected
    expect(ddTab).toHaveAttribute('aria-selected', 'true')
  })

  it('shows file quick actions when Document Analysis tab is active and files exist', async () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

    // Click on Document Analysis tab
    const docsTab = screen.getByRole('tab', { name: /doc/i })
    await userEvent.click(docsTab)

    // Quick actions should be visible
    await waitFor(() => {
      expect(screen.getByText('Quick analyze a file:')).toBeInTheDocument()
      expect(screen.getByText(/quarterly-report.pdf/)).toBeInTheDocument()
      expect(screen.getByText(/financials.xlsx/)).toBeInTheDocument()
    })
  })

  it('does not show file quick actions on other tabs', async () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

    // Should be on Market Research by default
    expect(screen.queryByText('Quick analyze a file:')).not.toBeInTheDocument()
  })

  it('highlights selected file in quick actions', async () => {
    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={mockFiles} />)

    // Click on Document Analysis tab
    const docsTab = screen.getByRole('tab', { name: /doc/i })
    await userEvent.click(docsTab)

    // Wait for quick actions to appear
    await waitFor(() => {
      expect(screen.getByText('Quick analyze a file:')).toBeInTheDocument()
    })

    // Get all buttons with the file name (there may be multiple in different sections)
    const fileButtons = screen.getAllByText(/quarterly-report.pdf/)
    const quickActionButton = fileButtons.find(
      (el) => el.closest('button')?.closest('.mt-4.pt-4.border-t')
    )?.closest('button')

    expect(quickActionButton).toBeInTheDocument()

    // Click on the file button
    if (quickActionButton) {
      await userEvent.click(quickActionButton)

      // File should be highlighted (has primary class)
      expect(quickActionButton).toHaveClass('bg-primary')
    }
  })

  it('calls onAgentRunComplete when agent run completes', async () => {
    const onComplete = vi.fn()
    const mockRun: AgentRun = {
      id: 'run-1',
      deal_id: mockDealId,
      user_id: 'user-1',
      user_email: 'test@example.com',
      agent_type: 'market_research',
      status: 'completed',
      input: { query: 'Test query' },
      output: { summary: 'Test output' },
      error_message: null,
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    }

    vi.mocked(agentsApi.startRun).mockResolvedValue({
      run_id: 'run-1',
      status: 'pending',
      message: 'Agent run started',
    })
    vi.mocked(agentsApi.getRun).mockResolvedValue(mockRun)
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: [
        { id: 'msg-1', role: 'assistant', content: 'Result', created_at: new Date().toISOString() },
      ],
      total: 1,
    })

    render(
      <AgentPanel
        dealId={mockDealId}
        dealTitle={mockDealTitle}
        onAgentRunComplete={onComplete}
      />
    )

    // Type and send a message
    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test query')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Wait for completion callback
    await waitFor(
      () => {
        expect(onComplete).toHaveBeenCalledWith(expect.objectContaining({ id: 'run-1' }))
      },
      { timeout: 10000 }
    )
  })

  it('truncates long file names in quick actions', async () => {
    const longFileName = 'this-is-a-very-long-file-name-that-should-be-truncated.pdf'
    const fileWithLongName: DealFile = {
      ...mockFiles[0],
      name: longFileName,
    }

    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={[fileWithLongName]} />)

    // Click on Document Analysis tab
    const docsTab = screen.getByRole('tab', { name: /doc/i })
    await userEvent.click(docsTab)

    // File name should be truncated (17 chars + ...)
    await waitFor(() => {
      expect(screen.getByText(/this-is-a-very-lo\.\.\./)).toBeInTheDocument()
    })
  })

  it('shows "+N more" when there are more than 5 files', async () => {
    const manyFiles: DealFile[] = Array.from({ length: 8 }, (_, i) => ({
      ...mockFiles[0],
      id: `file-${i}`,
      name: `file-${i}.pdf`,
    }))

    render(<AgentPanel dealId={mockDealId} dealTitle={mockDealTitle} files={manyFiles} />)

    // Click on Document Analysis tab
    const docsTab = screen.getByRole('tab', { name: /doc/i })
    await userEvent.click(docsTab)

    // Should show "+3 more"
    await waitFor(() => {
      expect(screen.getByText('+3 more')).toBeInTheDocument()
    })
  })
})
