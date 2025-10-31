/**
 * SkillExecutor Component
 * Interface for executing skills with parameter input
 */

'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/utils';
import {
  XMarkIcon,
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import type { Skill } from './SkillCard';

export interface SkillExecutorProps {
  skill: Skill | null;
  isOpen: boolean;
  onClose: () => void;
  onExecute?: (skillId: string, parameters: Record<string, any>) => Promise<void>;
  className?: string;
}

type ExecutionStatus = 'idle' | 'running' | 'success' | 'error';

/**
 * SkillExecutor Component
 *
 * Modal dialog for executing skills:
 * - Parameter input form
 * - Validation
 * - Real-time execution
 * - Result display
 *
 * @example
 * ```tsx
 * <SkillExecutor
 *   skill={selectedSkill}
 *   isOpen={isExecutorOpen}
 *   onClose={() => setIsExecutorOpen(false)}
 *   onExecute={async (skillId, params) => {
 *     await api.executeSkill(skillId, params);
 *   }}
 * />
 * ```
 */
export function SkillExecutor({
  skill,
  isOpen,
  onClose,
  onExecute,
  className
}: SkillExecutorProps) {
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<ExecutionStatus>('idle');
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string>('');

  if (!isOpen || !skill) return null;

  const handleParameterChange = (name: string, value: string) => {
    setParameters({ ...parameters, [name]: value });
  };

  const handleExecute = async () => {
    if (!onExecute) return;

    setStatus('running');
    setError('');
    setResult('');

    try {
      await onExecute(skill.id, parameters);
      setStatus('success');
      setResult('Skill executed successfully! Check the chat interface for the full response.');
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Execution failed');
    }
  };

  const handleClose = () => {
    setParameters({});
    setStatus('idle');
    setResult('');
    setError('');
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <Card
          variant="glass"
          className={cn(
            'max-w-2xl w-full max-h-[90vh] overflow-y-auto',
            className
          )}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-6 pb-4 border-b border-slate-700/50">
            <div className="flex-1">
              <h2 className="text-xl font-heading font-bold text-slate-200 mb-1">
                Execute Skill
              </h2>
              <p className="text-sm text-slate-400">{skill.name}</p>
            </div>
            <button
              onClick={handleClose}
              className="text-slate-400 hover:text-slate-200 transition-colors"
              aria-label="Close"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Parameter Form */}
          {status === 'idle' && (
            <div className="space-y-4 mb-6">
              <p className="text-sm text-slate-400">
                Provide the required parameters to execute this skill:
              </p>

              {/* Mock parameters - in real app, fetch from skill definition */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Project Name <span className="text-red-400">*</span>
                </label>
                <Input
                  type="text"
                  placeholder="Enter project name..."
                  value={parameters.projectName || ''}
                  onChange={(e) => handleParameterChange('projectName', e.target.value)}
                />
                <p className="mt-1 text-xs text-slate-500">
                  The name of the project for which the charter will be created
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Scope
                </label>
                <Input
                  type="text"
                  placeholder="Enter project scope (optional)..."
                  value={parameters.scope || ''}
                  onChange={(e) => handleParameterChange('scope', e.target.value)}
                />
                <p className="mt-1 text-xs text-slate-500">
                  High-level description of the project scope and objectives
                </p>
              </div>
            </div>
          )}

          {/* Running Status */}
          {status === 'running' && (
            <div className="text-center py-12">
              <ArrowPathIcon className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-spin" />
              <p className="text-lg font-semibold text-slate-200 mb-2">
                Executing skill...
              </p>
              <p className="text-sm text-slate-400">
                This may take a few moments
              </p>
            </div>
          )}

          {/* Success Status */}
          {status === 'success' && (
            <div className="text-center py-12">
              <CheckCircleIcon className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <p className="text-lg font-semibold text-slate-200 mb-2">
                Success!
              </p>
              <p className="text-sm text-slate-400 mb-6">
                {result}
              </p>
            </div>
          )}

          {/* Error Status */}
          {status === 'error' && (
            <div className="text-center py-12">
              <XCircleIcon className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <p className="text-lg font-semibold text-slate-200 mb-2">
                Execution Failed
              </p>
              <p className="text-sm text-red-400 mb-6">
                {error}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-6 border-t border-slate-700/50">
            {status === 'idle' && (
              <>
                <Button
                  variant="ghost"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="gradient"
                  onClick={handleExecute}
                  disabled={!parameters.projectName}
                  className="flex-1"
                >
                  <PlayIcon className="w-4 h-4 mr-2" />
                  Execute
                </Button>
              </>
            )}

            {status === 'running' && (
              <Button
                variant="ghost"
                onClick={handleClose}
                disabled
                className="flex-1"
              >
                Please wait...
              </Button>
            )}

            {(status === 'success' || status === 'error') && (
              <>
                <Button
                  variant="ghost"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Close
                </Button>
                {status === 'error' && (
                  <Button
                    variant="gradient"
                    onClick={() => {
                      setStatus('idle');
                      setError('');
                    }}
                    className="flex-1"
                  >
                    Try Again
                  </Button>
                )}
              </>
            )}
          </div>
        </Card>
      </div>
    </>
  );
}
