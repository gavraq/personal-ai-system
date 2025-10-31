/**
 * SkillDetails Component
 * Modal dialog for viewing detailed skill information
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import {
  XMarkIcon,
  ClockIcon,
  CubeIcon,
  PlayIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import type { Skill } from './SkillCard';

export interface SkillDetailsProps {
  skill: Skill | null;
  isOpen: boolean;
  onClose: () => void;
  onExecute?: (skill: Skill) => void;
  className?: string;
}

/**
 * SkillDetails Component
 *
 * Modal dialog displaying:
 * - Full skill description
 * - Parameters with types
 * - Expected output format
 * - Usage examples
 * - Execute action
 *
 * @example
 * ```tsx
 * <SkillDetails
 *   skill={selectedSkill}
 *   isOpen={isModalOpen}
 *   onClose={() => setIsModalOpen(false)}
 *   onExecute={(skill) => console.log('Execute', skill)}
 * />
 * ```
 */
export function SkillDetails({
  skill,
  isOpen,
  onClose,
  onExecute,
  className
}: SkillDetailsProps) {
  if (!isOpen || !skill) return null;

  const handleExecute = () => {
    onExecute?.(skill);
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <Card
          variant="glass"
          className={cn(
            'max-w-3xl w-full max-h-[90vh] overflow-y-auto',
            className
          )}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-6 pb-4 border-b border-slate-700/50">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="px-3 py-1 rounded-md text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  {skill.domain}
                </span>
              </div>
              <h2 className="text-2xl font-heading font-bold text-slate-200">
                {skill.name}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-200 transition-colors"
              aria-label="Close"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Metadata */}
          <div className="flex flex-wrap items-center gap-6 mb-6 text-sm">
            {skill.estimatedDuration && (
              <div className="flex items-center gap-2 text-slate-400">
                <ClockIcon className="w-5 h-5" />
                <span>{skill.estimatedDuration}</span>
              </div>
            )}

            {skill.parameters !== undefined && (
              <div className="flex items-center gap-2 text-slate-400">
                <CubeIcon className="w-5 h-5" />
                <span>{skill.parameters} parameter{skill.parameters !== 1 ? 's' : ''}</span>
              </div>
            )}

            {skill.successRate !== undefined && (
              <div className="flex items-center gap-2">
                <span className={cn(
                  'font-semibold',
                  skill.successRate >= 90 ? 'text-green-400' :
                  skill.successRate >= 70 ? 'text-yellow-400' :
                  'text-red-400'
                )}>
                  {skill.successRate}% success rate
                </span>
              </div>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
              Description
            </h3>
            <p className="text-slate-400 leading-relaxed">
              {skill.description}
            </p>
          </div>

          {/* Parameters (mock data) */}
          {skill.parameters && skill.parameters > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
                Parameters
              </h3>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/50">
                  <div className="flex items-start justify-between mb-1">
                    <code className="text-sm font-mono text-purple-400">projectName</code>
                    <span className="text-xs text-slate-500">Required</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    The name of the project for which the charter will be created
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/50">
                  <div className="flex items-start justify-between mb-1">
                    <code className="text-sm font-mono text-purple-400">scope</code>
                    <span className="text-xs text-slate-500">Optional</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    High-level description of the project scope and objectives
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Expected Output */}
          <div className="mb-6">
            <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
              Expected Output
            </h3>
            <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2">
                <DocumentTextIcon className="w-5 h-5 text-slate-400" />
                <span className="text-sm font-medium text-slate-300">
                  Structured document
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Returns a comprehensive document with sections including executive summary,
                objectives, scope, stakeholders, timeline, and success criteria.
              </p>
            </div>
          </div>

          {/* Usage Example */}
          <div className="mb-6">
            <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
              Usage Example
            </h3>
            <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-700/50">
              <pre className="text-xs text-slate-300 font-mono overflow-x-auto">
{`// Execute skill with parameters
executeSkill('${skill.id}', {
  projectName: 'Digital Transformation',
  scope: 'Modernize legacy systems...'
})`}
              </pre>
            </div>
          </div>

          {/* Tags */}
          {skill.tags && skill.tags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {skill.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 text-sm rounded-md bg-slate-800/50 text-slate-300 border border-slate-700/50"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-6 border-t border-slate-700/50">
            <Button
              variant="ghost"
              onClick={onClose}
              className="flex-1"
            >
              Close
            </Button>
            <Button
              variant="gradient"
              onClick={handleExecute}
              className="flex-1"
            >
              <PlayIcon className="w-4 h-4 mr-2" />
              Execute Skill
            </Button>
          </div>
        </Card>
      </div>
    </>
  );
}
