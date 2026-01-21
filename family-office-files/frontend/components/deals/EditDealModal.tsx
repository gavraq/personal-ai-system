'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { dealsApi, Deal, DealStatus } from '@/lib/api'

interface EditDealModalProps {
  deal: Deal
  open: boolean
  onOpenChange: (open: boolean) => void
  onDealUpdated: (deal: Deal) => void
}

const statusTransitions: Record<DealStatus, DealStatus[]> = {
  draft: ['draft', 'active'],
  active: ['active', 'closed'],
  closed: ['closed'],
}

export function EditDealModal({ deal, open, onOpenChange, onDealUpdated }: EditDealModalProps) {
  const [title, setTitle] = useState(deal.title)
  const [description, setDescription] = useState(deal.description || '')
  const [status, setStatus] = useState<DealStatus>(deal.status)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setTitle(deal.title)
    setDescription(deal.description || '')
    setStatus(deal.status)
  }, [deal])

  const allowedStatuses = statusTransitions[deal.status]
  const isClosed = deal.status === 'closed'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const updatedDeal = await dealsApi.update(deal.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        status: status !== deal.status ? status : undefined,
      })
      onDealUpdated(updatedDeal)
      onOpenChange(false)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to update deal')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Deal</DialogTitle>
            <DialogDescription>
              {isClosed
                ? 'This deal is closed and cannot be edited.'
                : 'Update deal details and status.'}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                placeholder="Enter deal title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isClosed}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                placeholder="Enter deal description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isClosed}
                rows={3}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-status">Status</Label>
              <Select
                value={status}
                onValueChange={(value) => setStatus(value as DealStatus)}
                disabled={isClosed}
              >
                <SelectTrigger id="edit-status">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {allowedStatuses.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {deal.status !== 'closed' && (
                <p className="text-xs text-muted-foreground">
                  Status can only transition forward: Draft → Active → Closed
                </p>
              )}
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            {!isClosed && (
              <Button type="submit" disabled={isLoading || !title.trim()}>
                {isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            )}
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
