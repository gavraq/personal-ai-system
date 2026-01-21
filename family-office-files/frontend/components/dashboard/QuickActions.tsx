'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { dealsApi, Deal, AgentType } from '@/lib/api'
import { CreateDealModal } from '@/components/deals'
import { FileUploader, UploadedFile } from '@/components/files/FileUploader'

export type UserRole = 'admin' | 'partner' | 'viewer'

interface QuickActionsProps {
  userRole: UserRole
  onDealCreated?: (deal: Deal) => void
  onFileUploaded?: (file: UploadedFile, dealId: string) => void
  onRunAgent?: (agentType: AgentType, dealId: string) => void
}

const AGENT_TYPES: { value: AgentType; label: string; icon: string }[] = [
  { value: 'market_research', label: 'Market Research', icon: '📊' },
  { value: 'document_analysis', label: 'Document Analysis', icon: '📄' },
  { value: 'due_diligence', label: 'Due Diligence', icon: '🔍' },
  { value: 'news_alerts', label: 'News Alerts', icon: '📰' },
]

export function QuickActions({
  userRole,
  onDealCreated,
  onFileUploaded,
  onRunAgent,
}: QuickActionsProps) {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false)
  const [deals, setDeals] = useState<Deal[]>([])
  const [selectedDealId, setSelectedDealId] = useState<string>('')
  const [selectedAgentType, setSelectedAgentType] = useState<AgentType | ''>('')
  const [isLoadingDeals, setIsLoadingDeals] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Refs for keyboard shortcut handling
  const createDealRef = useRef<HTMLButtonElement>(null)

  const canCreateDeal = userRole === 'admin' || userRole === 'partner'
  const canUploadFile = userRole === 'admin' || userRole === 'partner'

  // Load deals for selection
  const loadDeals = useCallback(async () => {
    setIsLoadingDeals(true)
    setError(null)
    try {
      const response = await dealsApi.list(1, 100, 'active')
      setDeals(response.deals)
    } catch (err) {
      console.error('Failed to load deals:', err)
      setError('Failed to load deals')
    } finally {
      setIsLoadingDeals(false)
    }
  }, [])

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Cmd (Mac) or Ctrl (Windows/Linux)
      const isMod = e.metaKey || e.ctrlKey

      if (isMod && e.key === 'n' && canCreateDeal) {
        e.preventDefault()
        createDealRef.current?.click()
      }

      if (isMod && e.key === 'u' && canUploadFile) {
        e.preventDefault()
        loadDeals()
        setIsUploadModalOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [canCreateDeal, canUploadFile, loadDeals])

  const handleOpenUploadModal = () => {
    loadDeals()
    setSelectedDealId('')
    setIsUploadModalOpen(true)
  }

  const handleOpenAgentModal = () => {
    loadDeals()
    setSelectedDealId('')
    setSelectedAgentType('')
    setIsAgentModalOpen(true)
  }

  const handleFileUploaded = (file: UploadedFile) => {
    if (selectedDealId) {
      onFileUploaded?.(file, selectedDealId)
      setIsUploadModalOpen(false)
      setSelectedDealId('')
    }
  }

  const handleRunAgent = () => {
    if (selectedDealId && selectedAgentType) {
      onRunAgent?.(selectedAgentType, selectedDealId)
      setIsAgentModalOpen(false)
      setSelectedDealId('')
      setSelectedAgentType('')
    }
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Create Deal Button - Admin/Partner only */}
      {canCreateDeal && (
        <CreateDealModal
          onDealCreated={(deal) => onDealCreated?.(deal)}
          trigger={
            <Button ref={createDealRef} data-testid="create-deal-button">
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Create Deal
              <span className="ml-2 text-xs text-muted-foreground/70">⌘N</span>
            </Button>
          }
        />
      )}

      {/* Upload File Button - Admin/Partner only */}
      {canUploadFile && (
        <Button
          variant="outline"
          onClick={handleOpenUploadModal}
          data-testid="upload-file-button"
        >
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
            />
          </svg>
          Upload File
          <span className="ml-2 text-xs text-muted-foreground/70">⌘U</span>
        </Button>
      )}

      {/* Run Agent Dropdown - All roles */}
      <Button
        variant="outline"
        onClick={handleOpenAgentModal}
        data-testid="run-agent-button"
      >
        <span className="mr-2">🤖</span>
        Run Agent
      </Button>

      {/* Upload File Modal */}
      <Dialog open={isUploadModalOpen} onOpenChange={setIsUploadModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Upload File</DialogTitle>
            <DialogDescription>
              Select a deal and upload a file to it.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="deal-select">Select Deal</Label>
              <Select
                value={selectedDealId}
                onValueChange={setSelectedDealId}
                disabled={isLoadingDeals}
              >
                <SelectTrigger id="deal-select" data-testid="deal-selector">
                  <SelectValue placeholder={isLoadingDeals ? 'Loading deals...' : 'Choose a deal'} />
                </SelectTrigger>
                <SelectContent>
                  {deals.map((deal) => (
                    <SelectItem key={deal.id} value={deal.id}>
                      {deal.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>

            {selectedDealId && (
              <FileUploader
                dealId={selectedDealId}
                onFileUploaded={handleFileUploaded}
              />
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Run Agent Modal */}
      <Dialog open={isAgentModalOpen} onOpenChange={setIsAgentModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Run Agent</DialogTitle>
            <DialogDescription>
              Select a deal and agent type to run.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="agent-deal-select">Select Deal</Label>
              <Select
                value={selectedDealId}
                onValueChange={setSelectedDealId}
                disabled={isLoadingDeals}
              >
                <SelectTrigger id="agent-deal-select" data-testid="agent-deal-selector">
                  <SelectValue placeholder={isLoadingDeals ? 'Loading deals...' : 'Choose a deal'} />
                </SelectTrigger>
                <SelectContent>
                  {deals.map((deal) => (
                    <SelectItem key={deal.id} value={deal.id}>
                      {deal.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="agent-type-select">Agent Type</Label>
              <Select
                value={selectedAgentType}
                onValueChange={(value) => setSelectedAgentType(value as AgentType)}
              >
                <SelectTrigger id="agent-type-select" data-testid="agent-type-selector">
                  <SelectValue placeholder="Choose an agent" />
                </SelectTrigger>
                <SelectContent>
                  {AGENT_TYPES.map((agent) => (
                    <SelectItem key={agent.value} value={agent.value}>
                      <span className="flex items-center gap-2">
                        <span>{agent.icon}</span>
                        <span>{agent.label}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsAgentModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRunAgent}
              disabled={!selectedDealId || !selectedAgentType}
              data-testid="run-agent-submit"
            >
              Run Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default QuickActions
