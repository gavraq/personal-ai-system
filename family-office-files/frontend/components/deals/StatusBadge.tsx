'use client'

import { Badge } from '@/components/ui/badge'
import { DealStatus } from '@/lib/api'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: DealStatus
  className?: string
}

const statusConfig: Record<DealStatus, { label: string; className: string }> = {
  draft: {
    label: 'Draft',
    className: 'bg-gray-100 text-gray-700 hover:bg-gray-100',
  },
  active: {
    label: 'Active',
    className: 'bg-green-100 text-green-700 hover:bg-green-100',
  },
  closed: {
    label: 'Closed',
    className: 'bg-blue-100 text-blue-700 hover:bg-blue-100',
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge variant="secondary" className={cn(config.className, className)}>
      {config.label}
    </Badge>
  )
}
