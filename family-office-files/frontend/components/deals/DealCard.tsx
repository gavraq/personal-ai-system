'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Deal } from '@/lib/api'
import { StatusBadge } from './StatusBadge'

interface DealCardProps {
  deal: Deal
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function DealCard({ deal }: DealCardProps) {
  return (
    <Link href={`/deals/${deal.id}`}>
      <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg line-clamp-1">{deal.title}</CardTitle>
            <StatusBadge status={deal.status} />
          </div>
          <CardDescription className="text-xs">
            Created {formatDate(deal.created_at)}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {deal.description ? (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {deal.description}
            </p>
          ) : (
            <p className="text-sm text-muted-foreground italic">No description</p>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}
