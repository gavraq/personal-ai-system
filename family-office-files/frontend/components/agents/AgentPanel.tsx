'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { AgentChat } from './AgentChat'
import { AgentType, AgentRun, DealFile } from '@/lib/api'

interface AgentPanelProps {
  dealId: string
  dealTitle: string
  files?: DealFile[]
  onAgentRunComplete?: (run: AgentRun) => void
  onAnalyzeFile?: (fileId: string, fileName: string) => void
}

// Agent tab configuration
const AGENT_TABS: {
  type: AgentType
  label: string
  icon: string
  shortLabel: string
}[] = [
  { type: 'market_research', label: 'Market Research', icon: '📊', shortLabel: 'Market' },
  { type: 'document_analysis', label: 'Document Analysis', icon: '📄', shortLabel: 'Docs' },
  { type: 'due_diligence', label: 'Due Diligence', icon: '🔍', shortLabel: 'DD' },
  { type: 'news_alerts', label: 'News & Alerts', icon: '📰', shortLabel: 'News' },
]

export function AgentPanel({
  dealId,
  dealTitle,
  files = [],
  onAgentRunComplete,
}: AgentPanelProps) {
  const [activeTab, setActiveTab] = useState<AgentType>('market_research')
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null)
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null)

  // Handle file analysis request
  const handleAnalyzeFile = useCallback((fileId: string, fileName: string) => {
    setActiveTab('document_analysis')
    setSelectedFileId(fileId)
    setSelectedFileName(fileName)
  }, [])

  // Clear file selection when switching away from document analysis
  const handleTabChange = (value: string) => {
    setActiveTab(value as AgentType)
    if (value !== 'document_analysis') {
      setSelectedFileId(null)
      setSelectedFileName(null)
    }
  }

  // Handle agent run completion
  const handleRunComplete = (run: AgentRun) => {
    // Clear file selection after document analysis completes
    if (run.agent_type === 'document_analysis') {
      setSelectedFileId(null)
      setSelectedFileName(null)
    }
    if (onAgentRunComplete) {
      onAgentRunComplete(run)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <span>🤖</span>
            AI Agents
          </CardTitle>
          {files.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {files.length} file{files.length !== 1 ? 's' : ''} available
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <Tabs value={activeTab} onValueChange={handleTabChange}>
          <TabsList className="w-full grid grid-cols-4 mb-4">
            {AGENT_TABS.map((tab) => (
              <TabsTrigger key={tab.type} value={tab.type} className="text-xs sm:text-sm">
                <span className="hidden sm:inline mr-1">{tab.icon}</span>
                <span className="sm:hidden">{tab.shortLabel}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          {AGENT_TABS.map((tab) => (
            <TabsContent key={tab.type} value={tab.type}>
              <AgentChat
                dealId={dealId}
                dealTitle={dealTitle}
                initialAgentType={tab.type}
                onAgentRunComplete={handleRunComplete}
                fileId={tab.type === 'document_analysis' ? selectedFileId : undefined}
                fileName={tab.type === 'document_analysis' ? selectedFileName : undefined}
              />
            </TabsContent>
          ))}
        </Tabs>

        {/* File quick actions - only show for document analysis tab */}
        {activeTab === 'document_analysis' && files.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm font-medium mb-2">Quick analyze a file:</p>
            <div className="flex flex-wrap gap-2">
              {files.slice(0, 5).map((file) => (
                <button
                  key={file.id}
                  onClick={() => handleAnalyzeFile(file.id, file.name)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    selectedFileId === file.id
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border bg-background hover:bg-muted'
                  }`}
                >
                  📄 {file.name.length > 20 ? file.name.slice(0, 17) + '...' : file.name}
                </button>
              ))}
              {files.length > 5 && (
                <span className="text-xs text-muted-foreground self-center">
                  +{files.length - 5} more
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default AgentPanel

// Export a hook for use by file list items
export function useAgentAnalyze() {
  const [analyzeFile, setAnalyzeFile] = useState<{ fileId: string; fileName: string } | null>(null)

  const requestAnalysis = (fileId: string, fileName: string) => {
    setAnalyzeFile({ fileId, fileName })
  }

  const clearAnalysis = () => {
    setAnalyzeFile(null)
  }

  return {
    analyzeFile,
    requestAnalysis,
    clearAnalysis,
  }
}
