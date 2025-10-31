/**
 * Dashboard Page
 * Main landing page after login with metrics, recent activity, and quick actions
 */

'use client';

import { useState, useEffect } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { PageContainer, PageHeader, Breadcrumbs } from '@/components/ui/Layout';
import { MetricsGrid, MetricData } from '@/components/dashboard/MetricsWidget';
import { RecentQueries, QueryHistoryItem } from '@/components/dashboard/RecentQueries';
import { QuickActions, SystemStatus } from '@/components/dashboard/QuickActions';
import { ActivityChart, DomainActivity } from '@/components/dashboard/ActivityChart';
import { Card } from '@/components/ui/Card';
import {
  ChartBarIcon,
  RectangleStackIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

/**
 * Dashboard Page Component
 *
 * Displays:
 * - User welcome message
 * - System metrics (queries, skills, success rate, response time)
 * - Recent query history
 * - Quick action buttons
 * - Activity charts
 * - Domain breakdown
 * - System status
 */
export default function DashboardPage() {
  const { user, isAuthenticated } = useSession();
  const { status: websocketStatus } = useWebSocketContext();

  // Mock data - in real app, fetch from backend API
  const [metrics, setMetrics] = useState<MetricData[]>([
    {
      label: 'Total Queries',
      value: 1234,
      change: 12.5,
      changeLabel: 'vs last week',
      icon: <ChartBarIcon className="w-6 h-6" />,
      color: 'blue',
      format: 'number'
    },
    {
      label: 'Skills Used',
      value: 28,
      change: 5.2,
      changeLabel: 'vs last week',
      icon: <RectangleStackIcon className="w-6 h-6" />,
      color: 'purple',
      format: 'number'
    },
    {
      label: 'Success Rate',
      value: 94.8,
      change: 2.1,
      changeLabel: 'vs last week',
      icon: <CheckCircleIcon className="w-6 h-6" />,
      color: 'green',
      format: 'percentage'
    },
    {
      label: 'Avg Response',
      value: 1250,
      change: -8.3,
      changeLabel: 'vs last week',
      icon: <ClockIcon className="w-6 h-6" />,
      color: 'yellow',
      format: 'duration'
    }
  ]);

  const [recentQueries, setRecentQueries] = useState<QueryHistoryItem[]>([
    {
      id: '1',
      query: 'Help me create a comprehensive project charter for our new digital transformation initiative',
      status: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 mins ago
      responseTime: 2340,
      skillsUsed: ['Project Setup', 'Document Generation']
    },
    {
      id: '2',
      query: 'Analyze the risk profile for the Q4 product launch',
      status: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      responseTime: 1890,
      skillsUsed: ['Risk Analysis', 'Report Generation']
    },
    {
      id: '3',
      query: 'Generate status report for the stakeholder meeting',
      status: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
      responseTime: 1560,
      skillsUsed: ['Status Tracking', 'Document Generation']
    },
    {
      id: '4',
      query: 'What are the key requirements for implementing change management?',
      status: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // Yesterday
      responseTime: 980,
      skillsUsed: ['Requirements Analysis']
    }
  ]);

  const [weeklyActivity, setWeeklyActivity] = useState([
    { label: 'Mon', value: 12, color: 'blue' as const },
    { label: 'Tue', value: 19, color: 'blue' as const },
    { label: 'Wed', value: 15, color: 'blue' as const },
    { label: 'Thu', value: 22, color: 'blue' as const },
    { label: 'Fri', value: 18, color: 'blue' as const },
    { label: 'Sat', value: 8, color: 'blue' as const },
    { label: 'Sun', value: 5, color: 'blue' as const }
  ]);

  const [domainActivity, setDomainActivity] = useState([
    { name: 'Project Management', count: 45, percentage: 42, color: 'blue' as const },
    { name: 'Risk Analysis', count: 32, percentage: 30, color: 'purple' as const },
    { name: 'Requirements', count: 18, percentage: 17, color: 'green' as const },
    { name: 'Change Management', count: 12, percentage: 11, color: 'yellow' as const }
  ]);

  // Determine system statuses
  const backendStatus = 'online'; // In real app, ping backend
  const authStatus = isAuthenticated ? 'authenticated' : 'unauthenticated';

  return (
    <PageContainer>
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard' }
        ]}
      />

      {/* Page Header */}
      <PageHeader
        title={`Welcome back, ${user?.email?.split('@')[0] || 'User'}!`}
        description="Here's what's happening with your Risk Agent today"
      />

      {/* Main Content */}
      <div className="space-y-6">
        {/* Metrics Grid */}
        <MetricsGrid metrics={metrics} />

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column (2/3 width) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Recent Queries */}
            <RecentQueries
              queries={recentQueries}
              maxItems={5}
              onQueryClick={(query) => console.log('Clicked query:', query)}
            />

            {/* Weekly Activity Chart */}
            <ActivityChart
              data={weeklyActivity}
              title="Weekly Activity"
              description="Queries executed per day"
            />
          </div>

          {/* Right Column (1/3 width) */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <QuickActions />

            {/* System Status */}
            <SystemStatus
              backendStatus={backendStatus}
              websocketStatus={websocketStatus}
              authStatus={authStatus}
            />

            {/* Domain Activity */}
            <DomainActivity domains={domainActivity} />
          </div>
        </div>

        {/* Welcome Card (for first-time users with no data) */}
        {recentQueries.length === 0 && (
          <Card variant="gradient" className="text-center py-12">
            <h3 className="text-2xl font-heading font-bold text-white mb-3">
              Welcome to Risk Agents!
            </h3>
            <p className="text-slate-200 mb-6 max-w-2xl mx-auto">
              You're all set up! Start by exploring our skills, browsing the knowledge base,
              or jumping straight into a conversation with the Risk Agent.
            </p>
            <div className="flex items-center justify-center gap-4">
              <a href="/chat">
                <button className="px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-slate-100 transition-colors">
                  Start Chatting
                </button>
              </a>
              <a href="/skills">
                <button className="px-6 py-3 bg-transparent border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-colors">
                  Browse Skills
                </button>
              </a>
            </div>
          </Card>
        )}
      </div>
    </PageContainer>
  );
}
