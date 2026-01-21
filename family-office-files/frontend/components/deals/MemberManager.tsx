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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { dealsApi, DealMember, Deal } from '@/lib/api'

interface MemberManagerProps {
  deal: Deal
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function MemberManager({ deal, open, onOpenChange }: MemberManagerProps) {
  const [members, setMembers] = useState<DealMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newUserId, setNewUserId] = useState('')
  const [roleOverride, setRoleOverride] = useState<string>('')
  const [isAdding, setIsAdding] = useState(false)

  const isClosed = deal.status === 'closed'

  useEffect(() => {
    if (open) {
      loadMembers()
    }
  }, [open, deal.id])

  const loadMembers = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await dealsApi.listMembers(deal.id)
      setMembers(response.members)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to load members')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUserId.trim()) return

    setIsAdding(true)
    setError(null)

    try {
      await dealsApi.addMember(deal.id, {
        user_id: newUserId.trim(),
        role_override: roleOverride || undefined,
      })
      setNewUserId('')
      setRoleOverride('')
      await loadMembers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to add member')
    } finally {
      setIsAdding(false)
    }
  }

  const handleRemoveMember = async (userId: string) => {
    try {
      await dealsApi.removeMember(deal.id, userId)
      await loadMembers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to remove member')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Manage Members</DialogTitle>
          <DialogDescription>
            {isClosed
              ? 'This deal is closed. Members cannot be modified.'
              : 'Add or remove members who can access this deal.'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Add member form */}
          {!isClosed && (
            <form onSubmit={handleAddMember} className="space-y-3 p-3 border rounded-lg bg-muted/30">
              <div className="grid gap-2">
                <Label htmlFor="user-id">User ID</Label>
                <Input
                  id="user-id"
                  placeholder="Enter user UUID"
                  value={newUserId}
                  onChange={(e) => setNewUserId(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="role-override">Role Override (optional)</Label>
                <Select value={roleOverride} onValueChange={setRoleOverride}>
                  <SelectTrigger id="role-override">
                    <SelectValue placeholder="Use default role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Use default role</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="partner">Partner</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" size="sm" disabled={isAdding || !newUserId.trim()}>
                {isAdding ? 'Adding...' : 'Add Member'}
              </Button>
            </form>
          )}

          {/* Error message */}
          {error && (
            <p className="text-sm text-destructive p-2 bg-destructive/10 rounded">{error}</p>
          )}

          {/* Members list */}
          <div className="space-y-2">
            <Label>Current Members ({members.length})</Label>
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading members...</p>
            ) : members.length === 0 ? (
              <p className="text-sm text-muted-foreground">No members found</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {members.map((member) => (
                  <div
                    key={member.user_id}
                    className="flex items-center justify-between p-2 border rounded bg-background"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {member.user_email || member.user_id}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {member.role_override
                          ? `Role: ${member.role_override}`
                          : 'Using default role'}
                        {member.user_id === deal.created_by && ' • Creator'}
                      </p>
                    </div>
                    {!isClosed && member.user_id !== deal.created_by && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => handleRemoveMember(member.user_id)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
