/**
 * Document Metadata Component
 * Displays YAML frontmatter metadata for knowledge documents
 */

'use client';

import {
  ShieldCheckIcon,
  CalendarIcon,
  CodeBracketSquareIcon,
  BeakerIcon,
  LinkIcon,
  DocumentTextIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import { KnowledgeArticle } from './KnowledgeCard';

export interface DocumentMetadataProps {
  article: KnowledgeArticle;
  className?: string;
}

/**
 * Get difficulty color
 */
function getDifficultyColor(difficulty?: string): string {
  const colors: Record<string, string> = {
    'Beginner': 'bg-green-500/10 text-green-400 border-green-500/20',
    'Intermediate': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    'Advanced': 'bg-red-500/10 text-red-400 border-red-500/20'
  };
  return colors[difficulty || ''] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

/**
 * Get artefact type color and icon
 */
function getArtefactTypeStyle(type?: string): { color: string; icon: string } {
  const styles: Record<string, { color: string; icon: string }> = {
    'policy': { color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', icon: 'shield' },
    'framework': { color: 'bg-purple-500/10 text-purple-400 border-purple-500/20', icon: 'grid' },
    'methodology': { color: 'bg-violet-500/10 text-violet-400 border-violet-500/20', icon: 'beaker' },
    'model': { color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20', icon: 'code' },
    'data': { color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20', icon: 'database' },
    'process': { color: 'bg-green-500/10 text-green-400 border-green-500/20', icon: 'cog' }
  };
  return styles[type || ''] || { color: 'bg-slate-500/10 text-slate-400 border-slate-500/20', icon: 'document' };
}

/**
 * Format artefact type name
 */
function formatArtefactType(type?: string): string {
  if (!type) return 'Document';
  return type.charAt(0).toUpperCase() + type.slice(1);
}

/**
 * Document Metadata Component
 */
export function DocumentMetadata({ article, className = '' }: DocumentMetadataProps) {
  const {
    artefact_type,
    risk_domain,
    owner,
    approval_date,
    version,
    difficulty,
    reading_time,
    related_artefacts,
    related_skills
  } = article;

  // If no YAML metadata, don't render anything
  const hasMetadata = artefact_type || risk_domain || owner || approval_date || version ||
                      difficulty || related_artefacts || related_skills;

  if (!hasMetadata) return null;

  const artefactStyle = getArtefactTypeStyle(artefact_type);
  const difficultyColor = getDifficultyColor(difficulty);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Document Type & Risk Domain */}
      <div className="flex flex-wrap gap-2">
        {artefact_type && (
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border ${artefactStyle.color}`}>
            <ShieldCheckIcon className="w-3.5 h-3.5" />
            {formatArtefactType(artefact_type)}
          </span>
        )}
        {risk_domain && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border bg-slate-700/30 text-slate-300 border-slate-600/50">
            <TagIcon className="w-3.5 h-3.5" />
            {risk_domain}
          </span>
        )}
        {difficulty && (
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border ${difficultyColor}`}>
            <BeakerIcon className="w-3.5 h-3.5" />
            {difficulty}
          </span>
        )}
      </div>

      {/* Governance Info */}
      {(owner || approval_date || version) && (
        <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 space-y-2">
          <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <DocumentTextIcon className="w-4 h-4" />
            Document Information
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            {owner && (
              <div>
                <span className="text-slate-500">Owner:</span>
                <span className="ml-2 text-slate-300">{owner}</span>
              </div>
            )}
            {approval_date && (
              <div>
                <span className="text-slate-500">Approved:</span>
                <span className="ml-2 text-slate-300">{approval_date}</span>
              </div>
            )}
            {version && (
              <div>
                <span className="text-slate-500">Version:</span>
                <span className="ml-2 text-slate-300">{version}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Related Artefacts */}
      {related_artefacts && Object.keys(related_artefacts).length > 0 && (
        <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 space-y-3">
          <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <LinkIcon className="w-4 h-4" />
            Related Artefacts
          </h4>
          <div className="space-y-2">
            {Object.entries(related_artefacts).map(([type, items]) => (
              <div key={type}>
                <div className="text-xs font-medium text-slate-400 mb-1 capitalize">
                  {type.replace(/_/g, ' ')}:
                </div>
                <div className="flex flex-wrap gap-1">
                  {items.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs rounded bg-slate-700/40 text-slate-300 border border-slate-600/30 hover:border-slate-500/50 transition-colors cursor-pointer"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Skills */}
      {related_skills && related_skills.length > 0 && (
        <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 space-y-3">
          <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <CodeBracketSquareIcon className="w-4 h-4" />
            Used by Skills
          </h4>
          <div className="flex flex-wrap gap-2">
            {related_skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 text-sm rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 transition-colors cursor-pointer"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
