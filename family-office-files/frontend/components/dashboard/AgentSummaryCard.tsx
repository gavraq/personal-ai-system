'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { agentsApi, AgentSummary, AgentRun, AgentType, AgentStatus } from '@/lib/api'

interface AgentSummaryCardProps {
  limit?: number
  autoRefresh?: boolean
  refreshInterval?: number
  onRerun?: (runId: string, agentType: AgentType, dealId: string) => void
}

function formatRelativeTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffSeconds < 60) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
  })
}

function getAgentTypeIcon(agentType: AgentType): string {
  switch (agentType) {
    case 'market_research':
      return '📊'
    case 'document_analysis':
      return '📄'
    case 'due_diligence':
      return '🔍'
    case 'news_alerts':
      return '📰'
    default:
      return '🤖'
  }
}

function getAgentTypeLabel(agentType: AgentType): string {
  switch (agentType) {
    case 'market_research':
      return 'Market Research'
    case 'document_analysis':
      return 'Document Analysis'
    case 'due_diligence':
      return 'Due Diligence'
    case 'news_alerts':
      return 'News Alerts'
    default:
      return 'Agent'
  }
}

function getStatusColor(status: AgentStatus): string {
  switch (status) {
    case 'completed':
      return 'text-green-600 bg-green-100'
    case 'failed':
      return 'text-red-600 bg-red-100'
    case 'running':
      return 'text-blue-600 bg-blue-100'
    case 'pending':
      return 'text-gray-600 bg-gray-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}

function StatusBadge({ status }: { status: AgentStatus }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(status)}`}>
      {status}
    </span>
  )
}

function AgentOutputModal({
  runId,
  agentType,
  dealTitle,
  onRerun,
}: {
  runId: string
  agentType: AgentType
  dealTitle: string
  onRerun?: () => void
}) {
  const [run, setRun] = useState<AgentRun | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchRun = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await agentsApi.getRun(runId)
      setRun(data)
    } catch (err) {
      setError('Failed to load agent output')
      console.error('Error fetching agent run:', err)
    } finally {
      setLoading(false)
    }
  }, [runId])

  useEffect(() => {
    fetchRun()
  }, [fetchRun])

  return (
    <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <span>{getAgentTypeIcon(agentType)}</span>
          <span>{getAgentTypeLabel(agentType)}</span>
          {run && <StatusBadge status={run.status} />}
        </DialogTitle>
        <DialogDescription>
          {dealTitle} - {run && formatRelativeTime(run.started_at)}
        </DialogDescription>
      </DialogHeader>

      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-5/6" />
          </div>
        )}

        {error && (
          <div className="p-4 text-red-500 text-sm">{error}</div>
        )}

        {run && !loading && (
          <div className="space-y-4 p-4">
            {run.error_message && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="text-sm font-medium text-red-800 mb-1">Error</h4>
                <p className="text-sm text-red-600">{run.error_message}</p>
              </div>
            )}

            {run.input && Object.keys(run.input).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Input</h4>
                <pre className="bg-gray-50 p-3 rounded-lg text-xs overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(run.input, null, 2)}
                </pre>
              </div>
            )}

            {run.output && Object.keys(run.output).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Output</h4>
                <pre className="bg-gray-50 p-3 rounded-lg text-xs overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(run.output, null, 2)}
                </pre>
              </div>
            )}

            {run.completed_at && (
              <div className="text-xs text-muted-foreground">
                Completed: {new Date(run.completed_at).toLocaleString('en-GB')}
              </div>
            )}
          </div>
        )}
      </div>

      {onRerun && run && (
        <div className="pt-4 border-t flex justify-end">
          <Button size="sm" onClick={onRerun}>
            Re-run Agent
          </Button>
        </div>
      )}
    </DialogContent>
  )
}

function SummaryItem({
  summary,
  onRerun,
}: {
  summary: AgentSummary
  onRerun?: (runId: string, agentType: AgentType, dealId: string) => void
}) {
  const handleRerun = () => {
    onRerun?.(summary.id, summary.agent_type, summary.deal_id)
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
          <div className="text-xl flex-shrink-0">{getAgentTypeIcon(summary.agent_type)}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium truncate">{getAgentTypeLabel(summary.agent_type)}</span>
              <StatusBadge status={summary.status} />
            </div>
            <p className="text-xs text-muted-foreground truncate mb-1">
              {summary.deal_title}
            </p>
            {summary.summary_excerpt && (
              <p className="text-xs text-gray-600 line-clamp-2">
                {summary.summary_excerpt}
              </p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              {formatRelativeTime(summary.started_at)}
            </p>
          </div>
        </div>
      </DialogTrigger>
      <AgentOutputModal
        runId={summary.id}
        agentType={summary.agent_type}
        dealTitle={summary.deal_title}
        onRerun={onRerun ? handleRerun : undefined}
      />
    </Dialog>
  )
}

export function AgentSummaryCard({
  limit = 5,
  autoRefresh = false,
  refreshInterval = 60000,
  onRerun,
}: AgentSummaryCardProps) {
  const [summaries, setSummaries] = useState<AgentSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSummaries = useCallback(async () => {
    try {
      const response = await agentsApi.listSummaries(limit)
      setSummaries(response.summaries)
      setError(null)
    } catch (err) {
      setError('Failed to load agent summaries')
      console.error('Error fetching agent summaries:', err)
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    fetchSummaries()

    if (autoRefresh) {
      const interval = setInterval(fetchSummaries, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchSummaries, autoRefresh, refreshInterval])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Agent Outputs</CardTitle>
          <CardDescription>Latest AI agent results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-3 animate-pulse">
                <div className="w-8 h-8 rounded bg-gray-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Agent Outputs</CardTitle>
          <CardDescription>Latest AI agent results</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (summaries.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Agent Outputs</CardTitle>
          <CardDescription>Latest AI agent results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🤖</div>
            <p className="text-sm text-muted-foreground">No agent runs yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Run an agent on a deal to see results here
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Agent Outputs</CardTitle>
        <CardDescription>Latest AI agent results</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {summaries.map((summary) => (
            <SummaryItem
              key={summary.id}
              summary={summary}
              onRerun={onRerun}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
