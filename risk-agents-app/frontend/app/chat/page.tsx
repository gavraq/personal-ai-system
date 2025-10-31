/**
 * Chat Page
 * Natural language query interface for Risk Agents
 */

'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';
import { PageContainer, PageHeader } from '@/components/ui/Layout';

export default function ChatPage() {
  return (
    <PageContainer maxWidth="2xl">
      <PageHeader
        title="Chat with Risk Agent"
        description="Ask questions, get insights, and execute risk management tasks using natural language"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Chat' },
        ]}
      />

      {/* Chat Interface */}
      <div className="h-[calc(100vh-16rem)]">
        <ChatInterface />
      </div>

      {/* Helper Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="glass-card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
            <span>💡</span>
            Example Questions
          </h3>
          <ul className="text-xs text-slate-400 space-y-1">
            <li>• What is risk management?</li>
            <li>• Help me create a risk register</li>
            <li>• Analyze project risks for me</li>
          </ul>
        </div>

        <div className="glass-card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
            <span>🎯</span>
            Skills Available
          </h3>
          <ul className="text-xs text-slate-400 space-y-1">
            <li>• Risk identification</li>
            <li>• Impact assessment</li>
            <li>• Mitigation planning</li>
          </ul>
        </div>

        <div className="glass-card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
            <span>⚡</span>
            Quick Actions
          </h3>
          <ul className="text-xs text-slate-400 space-y-1">
            <li>• Generate risk report</li>
            <li>• Create action items</li>
            <li>• Export to CSV/PDF</li>
          </ul>
        </div>
      </div>
    </PageContainer>
  );
}
