import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AgentChat } from '@/components/agents/AgentChat'
import { agentsApi, AgentRun, AgentMessage, AgentRunStartResponse } from '@/lib/api'

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

describe('AgentChat', () => {
  const mockDealId = 'deal-123'
  const mockDealTitle = 'Test Deal'

  const mockMessages: AgentMessage[] = [
    {
      id: 'msg-1',
      role: 'user',
      content: 'Analyze tech sector trends',
      created_at: new Date(Date.now() - 60000).toISOString(),
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content: 'The tech sector shows strong growth in AI and cloud computing...',
      created_at: new Date(Date.now() - 30000).toISOString(),
    },
  ]

  const mockCompletedRun: AgentRun = {
    id: 'run-1',
    deal_id: mockDealId,
    user_id: 'user-1',
    user_email: 'test@example.com',
    agent_type: 'market_research',
    status: 'completed',
    input: { query: 'Analyze tech sector trends' },
    output: { summary: 'Tech sector analysis complete' },
    error_message: null,
    started_at: new Date(Date.now() - 60000).toISOString(),
    completed_at: new Date(Date.now() - 30000).toISOString(),
  }

  const mockRunStartResponse: AgentRunStartResponse = {
    run_id: 'run-new-1',
    status: 'pending',
    message: 'Agent run started',
  }

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

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('renders agent type selector with all agent types', async () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Find the select trigger
    const trigger = screen.getByRole('combobox')
    expect(trigger).toBeInTheDocument()

    // Open the select
    await userEvent.click(trigger)

    // Check all agent types are available in the dropdown options
    await waitFor(() => {
      expect(screen.getAllByText('Market Research').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Document Analysis').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Due Diligence').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('News & Alerts').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('displays quick prompt suggestions for selected agent type', async () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      // Market research quick prompts should be visible by default
      expect(screen.getByText('Analyze market trends in this sector')).toBeInTheDocument()
      expect(screen.getByText('Identify key competitors')).toBeInTheDocument()
    })
  })

  it('changes quick prompts when agent type changes', async () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Open agent type selector
    const trigger = screen.getByRole('combobox')
    await userEvent.click(trigger)

    // Select Due Diligence
    await waitFor(() => {
      const dueDiligenceOption = screen.getByText('Due Diligence')
      expect(dueDiligenceOption).toBeInTheDocument()
    })
    await userEvent.click(screen.getByText('Due Diligence'))

    // Check due diligence quick prompts are shown
    await waitFor(() => {
      expect(screen.getByText('Run full due diligence check')).toBeInTheDocument()
      expect(screen.getByText('Identify red flags')).toBeInTheDocument()
    })
  })

  it('populates input when clicking quick prompt', async () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(screen.getByText('Analyze market trends in this sector')).toBeInTheDocument()
    })

    // Click a quick prompt
    await userEvent.click(screen.getByText('Analyze market trends in this sector'))

    // Check input is populated
    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    expect(textarea).toHaveValue('Analyze market trends in this sector')
  })

  it('loads message history on mount', async () => {
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(agentsApi.listDealRuns).toHaveBeenCalledWith(mockDealId, 1, 10, 'market_research')
    })

    await waitFor(() => {
      expect(screen.getByText('Analyze tech sector trends')).toBeInTheDocument()
      expect(screen.getByText(/The tech sector shows strong growth/)).toBeInTheDocument()
    })
  })

  it('sends message and displays loading indicator', async () => {
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockResolvedValue({
      ...mockCompletedRun,
      id: 'run-new-1',
      status: 'running',
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Type a message
    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'What are the market trends?')

    // Click send
    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Check loading indicator appears
    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    })

    // Check API was called
    expect(agentsApi.startRun).toHaveBeenCalledWith('market_research', mockDealId, {
      query: 'What are the market trends?',
    })
  })

  it('sends message on Enter key press', async () => {
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockResolvedValue({
      ...mockCompletedRun,
      id: 'run-new-1',
      status: 'running',
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message{enter}')

    await waitFor(() => {
      expect(agentsApi.startRun).toHaveBeenCalled()
    })
  })

  it('does not send message on Shift+Enter', async () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Line 1{shift>}{enter}{/shift}Line 2')

    expect(agentsApi.startRun).not.toHaveBeenCalled()
    expect(textarea).toHaveValue('Line 1\nLine 2')
  })

  it('displays messages persisted after refresh (message history)', async () => {
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    // First render
    const { unmount } = render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(screen.getByText('Analyze tech sector trends')).toBeInTheDocument()
    })

    // Unmount and remount (simulating refresh)
    unmount()

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Messages should still be loaded
    await waitFor(() => {
      expect(screen.getByText('Analyze tech sector trends')).toBeInTheDocument()
      expect(screen.getByText(/The tech sector shows strong growth/)).toBeInTheDocument()
    })
  })

  it('displays streaming indicator during agent processing', async () => {
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockResolvedValue({
      ...mockCompletedRun,
      id: 'run-new-1',
      status: 'running',
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Analyze this')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Streaming indicator should appear
    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    })
  })

  it('displays error message on API failure', async () => {
    vi.mocked(agentsApi.startRun).mockRejectedValue(new Error('API Error'))

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument()
    })
  })

  it('displays failed run error message', async () => {
    const failedRun: AgentRun = {
      ...mockCompletedRun,
      id: 'run-failed-1',
      status: 'failed',
      error_message: 'Agent encountered an error during processing',
    }

    vi.mocked(agentsApi.startRun).mockResolvedValue({
      run_id: 'run-failed-1',
      status: 'pending',
      message: 'Agent run started',
    })
    vi.mocked(agentsApi.getRun).mockResolvedValue(failedRun)
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: [mockMessages[0]],
      total: 1,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Agent encountered an error during processing')).toBeInTheDocument()
    }, { timeout: 10000 })
  })

  it('has copy button when assistant messages exist', async () => {
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(screen.getByText(/The tech sector shows strong growth/)).toBeInTheDocument()
    }, { timeout: 10000 })

    // Copy button should be visible
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
    })
  })

  it('has export button when assistant messages exist', async () => {
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(screen.getByText(/The tech sector shows strong growth/)).toBeInTheDocument()
    }, { timeout: 10000 })

    // Export button should be visible
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
    })
  })

  it('copies results to clipboard when copy button clicked', async () => {
    // Mock clipboard
    const mockClipboard = {
      writeText: vi.fn().mockResolvedValue(undefined),
    }
    Object.assign(navigator, { clipboard: mockClipboard })

    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    await waitFor(() => {
      expect(screen.getByText(/The tech sector shows strong growth/)).toBeInTheDocument()
    }, { timeout: 10000 })

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /copy/i }))

    expect(mockClipboard.writeText).toHaveBeenCalledWith(
      'The tech sector shows strong growth in AI and cloud computing...'
    )
  })

  it('disables send button when input is empty', () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const sendButton = screen.getByRole('button', { name: /send/i })
    expect(sendButton).toBeDisabled()
  })

  it('disables send button while loading', async () => {
    // Make getRun return running status forever to keep loading state
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockImplementation(() =>
      new Promise(() => {}) // Never resolves to keep loading
    )

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Wait for loading state to be set
    await waitFor(() => {
      expect(screen.getByText('Sending')).toBeInTheDocument()
    })
  })

  it('disables quick prompts while loading', async () => {
    // Make getRun never resolve to keep loading state
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockImplementation(() =>
      new Promise(() => {}) // Never resolves to keep loading
    )

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    await waitFor(() => {
      const quickPromptButton = screen.getByText('Analyze market trends in this sector')
      expect(quickPromptButton).toBeDisabled()
    })
  })

  it('shows empty state when no messages', () => {
    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    expect(screen.getByText(/Start by typing a message/)).toBeInTheDocument()
  })

  it('calls onAgentRunComplete callback when run completes', async () => {
    const onComplete = vi.fn()

    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockResolvedValue({
      ...mockCompletedRun,
      id: 'run-new-1',
      status: 'completed',
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(
      <AgentChat
        dealId={mockDealId}
        dealTitle={mockDealTitle}
        onAgentRunComplete={onComplete}
      />
    )

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled()
    }, { timeout: 10000 })
  })

  it('displays status badge during processing', async () => {
    vi.mocked(agentsApi.startRun).mockResolvedValue(mockRunStartResponse)
    vi.mocked(agentsApi.getRun).mockImplementation(() =>
      new Promise(() => {}) // Never resolves
    )

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    const textarea = screen.getByPlaceholderText(/Analyze tech sector trends/i)
    await userEvent.type(textarea, 'Test message')

    const sendButton = screen.getByRole('button', { name: /send/i })
    await userEvent.click(sendButton)

    // Status should show pending immediately after submit
    await waitFor(() => {
      expect(screen.getByText('pending')).toBeInTheDocument()
    })
  })

  it('displays correct agent icon and description', async () => {
    render(
      <AgentChat
        dealId={mockDealId}
        dealTitle={mockDealTitle}
        initialAgentType="due_diligence"
      />
    )

    // Find elements containing the due diligence description
    const descriptions = screen.getAllByText(/Comprehensive background and risk analysis/i)
    expect(descriptions.length).toBeGreaterThan(0)
  })

  it('clears messages when agent type changes', async () => {
    vi.mocked(agentsApi.listDealRuns).mockResolvedValue({
      runs: [mockCompletedRun],
      total: 1,
      page: 1,
      page_size: 10,
    })
    vi.mocked(agentsApi.getMessages).mockResolvedValue({
      messages: mockMessages,
      total: 2,
    })

    render(<AgentChat dealId={mockDealId} dealTitle={mockDealTitle} />)

    // Wait for messages to load
    await waitFor(() => {
      expect(screen.getByText('Analyze tech sector trends')).toBeInTheDocument()
    }, { timeout: 10000 })

    // Reset mock to return empty for different agent type
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

    // Change agent type - click on the currently selected value
    const trigger = screen.getByRole('combobox')
    await userEvent.click(trigger)

    // Wait for dropdown to be visible and click on Document Analysis
    await waitFor(() => {
      const options = screen.getAllByText('Document Analysis')
      expect(options.length).toBeGreaterThan(0)
    })

    const docAnalysisOptions = screen.getAllByText('Document Analysis')
    // Click the one that's in the dropdown (has role option)
    const option = docAnalysisOptions.find(el =>
      el.closest('[role="option"]') || el.closest('[data-radix-collection-item]')
    ) || docAnalysisOptions[docAnalysisOptions.length - 1]
    await userEvent.click(option)

    // Messages should be cleared and empty state shown
    await waitFor(() => {
      expect(screen.queryByText('Analyze tech sector trends')).not.toBeInTheDocument()
    }, { timeout: 10000 })
  })
})
