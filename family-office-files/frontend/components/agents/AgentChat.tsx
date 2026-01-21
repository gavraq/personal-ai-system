'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { agentsApi, AgentType, AgentStatus, AgentRun, AgentMessage } from '@/lib/api'

interface AgentChatProps {
  dealId: string
  dealTitle?: string
  initialAgentType?: AgentType
  onAgentRunComplete?: (run: AgentRun) => void
  fileId?: string | null
  fileName?: string | null
}

// Agent type configuration
const AGENT_CONFIGS: Record<AgentType, {
  label: string
  icon: string
  description: string
  placeholder: string
  quickPrompts: string[]
}> = {
  market_research: {
    label: 'Market Research',
    icon: '\ud83d\udcca',
    description: 'Analyze market trends, competitors, and opportunities',
    placeholder: 'e.g., Analyze tech sector trends in 2024',
    quickPrompts: [
      'Analyze market trends in this sector',
      'Identify key competitors',
      'What are the growth opportunities?',
      'Summarize market risks',
    ],
  },
  document_analysis: {
    label: 'Document Analysis',
    icon: '\ud83d\udcc4',
    description: 'Extract insights from uploaded documents',
    placeholder: 'e.g., Summarize the key points from this document',
    quickPrompts: [
      'Extract key points',
      'Identify risk factors',
      'Summarize financial data',
      'List action items',
    ],
  },
  due_diligence: {
    label: 'Due Diligence',
    icon: '\ud83d\udd0d',
    description: 'Comprehensive background and risk analysis',
    placeholder: 'e.g., Perform due diligence on Company XYZ',
    quickPrompts: [
      'Run full due diligence check',
      'Identify red flags',
      'Analyze company leadership',
      'Check regulatory compliance',
    ],
  },
  news_alerts: {
    label: 'News & Alerts',
    icon: '\ud83d\udcf0',
    description: 'Monitor news and set up alerts',
    placeholder: 'e.g., Find recent news about renewable energy investments',
    quickPrompts: [
      'Find recent news on this topic',
      'What are the latest developments?',
      'Monitor for regulatory changes',
      'Track competitor announcements',
    ],
  },
}

function formatTime(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function MessageBubble({ message }: { message: AgentMessage }) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <span className="text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
          {message.content}
        </span>
      </div>
    )
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        <p className={`text-xs mt-1 ${isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
          {formatTime(message.created_at)}
        </p>
      </div>
    </div>
  )
}

function StreamingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-muted">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-sm text-muted-foreground">Analyzing...</span>
        </div>
      </div>
    </div>
  )
}

function QuickPromptChips({
  prompts,
  onSelect,
  disabled,
}: {
  prompts: string[]
  onSelect: (prompt: string) => void
  disabled: boolean
}) {
  return (
    <div className="flex flex-wrap gap-2 mb-3">
      {prompts.map((prompt, index) => (
        <button
          key={index}
          onClick={() => onSelect(prompt)}
          disabled={disabled}
          className="text-xs px-3 py-1.5 rounded-full border border-border bg-background hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {prompt}
        </button>
      ))}
    </div>
  )
}

function StatusBadge({ status }: { status: AgentStatus }) {
  const colors: Record<AgentStatus, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }

  return (
    <Badge className={`${colors[status]} border-0`}>
      {status}
    </Badge>
  )
}

export function AgentChat({
  dealId,
  dealTitle = 'Deal',
  initialAgentType = 'market_research',
  onAgentRunComplete,
  fileId,
  fileName,
}: AgentChatProps) {
  const [agentType, setAgentType] = useState<AgentType>(initialAgentType)
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [runStatus, setRunStatus] = useState<AgentStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const config = AGENT_CONFIGS[agentType]

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isStreaming])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])

  // Load message history for current agent type and deal
  const loadMessageHistory = useCallback(async () => {
    try {
      // Get recent runs for this deal and agent type
      const response = await agentsApi.listDealRuns(dealId, 1, 10, agentType)

      // Load messages from the most recent runs
      const allMessages: AgentMessage[] = []
      for (const run of response.runs.slice(0, 5)) {
        const messagesResponse = await agentsApi.getMessages(run.id)
        allMessages.push(...messagesResponse.messages)
      }

      // Sort by created_at
      allMessages.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      )

      setMessages(allMessages)
    } catch (err) {
      console.error('Error loading message history:', err)
      // Don't show error for empty history
    }
  }, [dealId, agentType])

  // Load history when agent type changes
  useEffect(() => {
    loadMessageHistory()
  }, [loadMessageHistory])

  // Poll for run status
  const pollRunStatus = useCallback(async (runId: string) => {
    try {
      const run = await agentsApi.getRun(runId)
      setRunStatus(run.status)

      if (run.status === 'completed' || run.status === 'failed') {
        // Stop polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
        setIsLoading(false)
        setIsStreaming(false)

        // Load final messages
        const messagesResponse = await agentsApi.getMessages(runId)
        const newMessages = messagesResponse.messages.filter(
          (m: AgentMessage) => !messages.some(existing => existing.id === m.id)
        )
        if (newMessages.length > 0) {
          setMessages(prev => [...prev, ...newMessages])
        }

        // Notify parent
        if (onAgentRunComplete) {
          onAgentRunComplete(run)
        }

        if (run.status === 'failed') {
          setError(run.error_message || 'Agent run failed')
        }
      }
    } catch (err) {
      console.error('Error polling run status:', err)
    }
  }, [messages, onAgentRunComplete])

  // Start an agent run
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: AgentMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      created_at: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)
    setIsStreaming(true)
    setError(null)

    try {
      const response = await agentsApi.startRun(agentType, dealId, {
        query: userMessage.content,
        file_id: agentType === 'document_analysis' && fileId ? fileId : undefined,
      })

      const { run_id, status } = response
      setCurrentRunId(run_id)
      setRunStatus(status)

      // Start polling for status
      pollingIntervalRef.current = setInterval(() => {
        pollRunStatus(run_id)
      }, 2000)

    } catch (err: unknown) {
      setIsLoading(false)
      setIsStreaming(false)
      const errorMessage = err instanceof Error ? err.message : 'Failed to start agent'
      setError(errorMessage)
      console.error('Error starting agent run:', err)
    }
  }

  // Handle quick prompt selection
  const handleQuickPrompt = (prompt: string) => {
    setInputValue(prompt)
  }

  // Copy results to clipboard
  const copyResults = async () => {
    const assistantMessages = messages.filter(m => m.role === 'assistant')
    if (assistantMessages.length === 0) return

    const content = assistantMessages.map(m => m.content).join('\n\n---\n\n')
    await navigator.clipboard.writeText(content)
  }

  // Export results as text file
  const exportResults = () => {
    const content = messages
      .map(m => `[${m.role.toUpperCase()}] ${formatTime(m.created_at)}\n${m.content}`)
      .join('\n\n')

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${agentType}-${dealId}-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="border-b pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <span className="text-xl">{config.icon}</span>
              Agent Chat
            </CardTitle>
            {runStatus && <StatusBadge status={runStatus} />}
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={agentType}
              onValueChange={(value: AgentType) => {
                setAgentType(value)
                setMessages([])
                setError(null)
                setRunStatus(null)
              }}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select agent" />
              </SelectTrigger>
              <SelectContent>
                {(Object.keys(AGENT_CONFIGS) as AgentType[]).map((type) => (
                  <SelectItem key={type} value={type}>
                    <span className="flex items-center gap-2">
                      <span>{AGENT_CONFIGS[type].icon}</span>
                      {AGENT_CONFIGS[type].label}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {messages.some(m => m.role === 'assistant') && (
              <div className="flex gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyResults}
                  title="Copy results"
                >
                  Copy
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={exportResults}
                  title="Export results"
                >
                  Export
                </Button>
              </div>
            )}
          </div>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          {config.description} - {dealTitle}
        </p>
        {agentType === 'document_analysis' && fileName && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
              📄 Analyzing: {fileName}
            </span>
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && !isStreaming ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="text-4xl mb-4">{config.icon}</div>
            <h3 className="text-lg font-medium mb-2">{config.label}</h3>
            <p className="text-sm text-muted-foreground max-w-md mb-4">
              {config.description}. Start by typing a message or select a quick prompt below.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isStreaming && <StreamingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg mt-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}
      </CardContent>

      <div className="border-t p-4">
        <QuickPromptChips
          prompts={config.quickPrompts}
          onSelect={handleQuickPrompt}
          disabled={isLoading}
        />
        <div className="flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              agentType === 'document_analysis' && fileName
                ? `Ask about "${fileName}"...`
                : config.placeholder
            }
            disabled={isLoading}
            className="min-h-[44px] max-h-[120px] resize-none"
            rows={1}
          />
          <Button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="self-end"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Sending</span>
              </span>
            ) : (
              'Send'
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </Card>
  )
}

export default AgentChat
