/**
 * SkillCard Component
 * Displays an individual skill with metadata and actions
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import {
  ClockIcon,
  CubeIcon,
  StarIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

export interface Skill {
  id: string;
  name: string;
  description: string;
  domain: string;
  estimatedDuration?: string; // e.g., "2-3 minutes"
  parameters?: number;
  successRate?: number; // 0-100
  isFavorite?: boolean;
  tags?: string[];
}

export interface SkillCardProps {
  skill: Skill;
  onViewDetails?: (skill: Skill) => void;
  onExecute?: (skill: Skill) => void;
  onToggleFavorite?: (skillId: string) => void;
  className?: string;
}

/**
 * Gets color scheme for domain badge
 */
function getDomainColor(domain: string): string {
  const colors: Record<string, string> = {
    'Project Management': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'Change Agent': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    'Risk Analysis': 'bg-red-500/10 text-red-400 border-red-500/20',
    'Requirements': 'bg-green-500/10 text-green-400 border-green-500/20',
    'Document Generation': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  };

  return colors[domain] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

/**
 * SkillCard Component
 *
 * Displays a skill card with:
 * - Skill name and description
 * - Domain badge
 * - Metadata (duration, parameters, success rate)
 * - Favorite toggle
 * - View details and execute actions
 *
 * @example
 * ```tsx
 * <SkillCard
 *   skill={{
 *     id: '1',
 *     name: 'Create Project Charter',
 *     description: 'Generate comprehensive project charter...',
 *     domain: 'Project Management',
 *     estimatedDuration: '2-3 minutes',
 *     parameters: 5,
 *     successRate: 95,
 *     isFavorite: false
 *   }}
 *   onViewDetails={(skill) => console.log('View', skill)}
 *   onExecute={(skill) => console.log('Execute', skill)}
 *   onToggleFavorite={(id) => console.log('Toggle favorite', id)}
 * />
 * ```
 */
export function SkillCard({
  skill,
  onViewDetails,
  onExecute,
  onToggleFavorite,
  className
}: SkillCardProps) {
  const domainColor = getDomainColor(skill.domain);

  return (
    <Card
      variant="glass"
      className={cn(
        'group transition-all duration-300',
        'hover:border-slate-600/50',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        {/* Domain Badge */}
        <span
          className={cn(
            'px-3 py-1 rounded-md text-xs font-semibold border',
            domainColor
          )}
        >
          {skill.domain}
        </span>

        {/* Favorite Toggle */}
        <button
          onClick={() => onToggleFavorite?.(skill.id)}
          className="text-slate-400 hover:text-yellow-400 transition-colors"
          aria-label={skill.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {skill.isFavorite ? (
            <StarIconSolid className="w-5 h-5 text-yellow-400" />
          ) : (
            <StarIcon className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Skill Name */}
      <h3 className="text-lg font-heading font-semibold text-slate-200 mb-2 group-hover:text-slate-100">
        {skill.name}
      </h3>

      {/* Description */}
      <p className="text-sm text-slate-400 mb-4 line-clamp-3">
        {skill.description}
      </p>

      {/* Metadata */}
      <div className="flex flex-wrap items-center gap-4 mb-4 text-xs text-slate-500">
        {skill.estimatedDuration && (
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4" />
            <span>{skill.estimatedDuration}</span>
          </div>
        )}

        {skill.parameters !== undefined && (
          <div className="flex items-center gap-1">
            <CubeIcon className="w-4 h-4" />
            <span>{skill.parameters} parameter{skill.parameters !== 1 ? 's' : ''}</span>
          </div>
        )}

        {skill.successRate !== undefined && (
          <div className="flex items-center gap-1">
            <span className={cn(
              'font-semibold',
              skill.successRate >= 90 ? 'text-green-400' :
              skill.successRate >= 70 ? 'text-yellow-400' :
              'text-red-400'
            )}>
              {skill.successRate}% success
            </span>
          </div>
        )}
      </div>

      {/* Tags */}
      {skill.tags && skill.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {skill.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs rounded-md bg-slate-800/50 text-slate-400 border border-slate-700/50"
            >
              {tag}
            </span>
          ))}
          {skill.tags.length > 3 && (
            <span className="px-2 py-1 text-xs rounded-md bg-slate-800/50 text-slate-400">
              +{skill.tags.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 pt-4 border-t border-slate-700/50">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewDetails?.(skill)}
          className="flex-1"
        >
          View Details
        </Button>
        <Button
          variant="gradient"
          size="sm"
          onClick={() => onExecute?.(skill)}
          className="flex-1"
        >
          <PlayIcon className="w-4 h-4 mr-1" />
          Execute
        </Button>
      </div>
    </Card>
  );
}

/**
 * SkillGrid Component
 * Grid layout for multiple skill cards
 */
export interface SkillGridProps {
  skills: Skill[];
  onViewDetails?: (skill: Skill) => void;
  onExecute?: (skill: Skill) => void;
  onToggleFavorite?: (skillId: string) => void;
  className?: string;
}

export function SkillGrid({
  skills,
  onViewDetails,
  onExecute,
  onToggleFavorite,
  className
}: SkillGridProps) {
  if (skills.length === 0) {
    return (
      <div className="text-center py-12">
        <CubeIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <p className="text-slate-400 text-lg mb-2">No skills found</p>
        <p className="text-slate-500 text-sm">
          Try adjusting your filters or search criteria
        </p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
        className
      )}
    >
      {skills.map((skill) => (
        <SkillCard
          key={skill.id}
          skill={skill}
          onViewDetails={onViewDetails}
          onExecute={onExecute}
          onToggleFavorite={onToggleFavorite}
        />
      ))}
    </div>
  );
}
