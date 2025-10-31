/**
 * Knowledge Details Modal Component
 * Full article view with content and related articles
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  XMarkIcon,
  ClockIcon,
  TagIcon,
  BookmarkIcon as BookmarkIconOutline,
  EyeIcon,
  UserIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/react/24/solid';
import { KnowledgeArticle } from './KnowledgeCard';
import { DocumentMetadata } from './DocumentMetadata';

export interface KnowledgeDetailsProps {
  article: KnowledgeArticle | null;
  isOpen: boolean;
  onClose: () => void;
  onToggleBookmark?: (articleId: string) => void;
  onViewRelated?: (articleId: string) => void;
  className?: string;
}

/**
 * Format last updated date
 */
function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  }).format(date);
}

/**
 * Get category color based on Risk Taxonomy Framework
 */
function getCategoryColor(category: string): string {
  // Risk Taxonomy Framework - 11 inventory components
  const colors: Record<string, string> = {
    // Core Framework Layers
    'Policies': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'Governance': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    'Processes & Procedures': 'bg-green-500/10 text-green-400 border-green-500/20',
    'Controls': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',

    // Operational Components
    'Products': 'bg-pink-500/10 text-pink-400 border-pink-500/20',
    'Reports': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    'Feeds': 'bg-orange-500/10 text-orange-400 border-orange-500/20',

    // Technical Components
    'Data': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    'Methodologies & Models': 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    'Systems': 'bg-teal-500/10 text-teal-400 border-teal-500/20',

    // Risk Types
    'Risks': 'bg-red-500/10 text-red-400 border-red-500/20'
  };

  return colors[category] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

/**
 * Knowledge Details Modal Component
 */
export function KnowledgeDetails({
  article,
  isOpen,
  onClose,
  onToggleBookmark,
  onViewRelated,
  className = ''
}: KnowledgeDetailsProps) {
  if (!isOpen || !article) return null;

  const {
    id,
    title,
    summary,
    content,
    category,
    tags = [],
    lastUpdated,
    readTime,
    views,
    isBookmarked = false,
    author,
    relatedArticles = []
  } = article;

  const categoryColor = getCategoryColor(category);

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <Card
          variant="glass"
          className={`w-full max-w-4xl my-8 ${className}`}
        >
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-slate-700/50">
            <div className="flex-1 pr-4">
              {/* Category Badge */}
              <span className={`inline-block px-3 py-1 rounded-md text-xs font-semibold border ${categoryColor} mb-3`}>
                {category}
              </span>

              {/* Title */}
              <h2 className="text-2xl font-heading font-bold text-slate-200 mb-2">
                {title}
              </h2>

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
                {author && (
                  <div className="flex items-center gap-1">
                    <UserIcon className="w-4 h-4" />
                    <span>{author}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>{formatDate(lastUpdated)}</span>
                </div>
                {readTime && (
                  <div className="flex items-center gap-1">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>{readTime} min read</span>
                  </div>
                )}
                {views !== undefined && (
                  <div className="flex items-center gap-1">
                    <EyeIcon className="w-4 h-4" />
                    <span>{views.toLocaleString()} views</span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleBookmark?.(id);
                }}
                className="p-2 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800/50 transition-colors"
                aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
              >
                {isBookmarked ? (
                  <BookmarkIconSolid className="w-5 h-5 text-blue-400" />
                ) : (
                  <BookmarkIconOutline className="w-5 h-5" />
                )}
              </button>

              <button
                onClick={onClose}
                className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors"
                aria-label="Close"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
            {/* Summary */}
            <div>
              <h3 className="text-lg font-heading font-semibold text-slate-200 mb-2">
                Summary
              </h3>
              <p className="text-slate-300 leading-relaxed">
                {summary}
              </p>
            </div>

            {/* Document Metadata (YAML frontmatter) */}
            <DocumentMetadata article={article} />

            {/* Full Content */}
            {content && (
              <div>
                <h3 className="text-lg font-heading font-semibold text-slate-200 mb-2">
                  Content
                </h3>
                <div className="text-slate-300 leading-relaxed space-y-4 prose prose-invert max-w-none">
                  {content.split('\n\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {tags.length > 0 && (
              <div>
                <h3 className="text-lg font-heading font-semibold text-slate-200 mb-2">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 text-sm rounded-md bg-slate-800/50 text-slate-400 border border-slate-700/50"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Related Articles */}
            {relatedArticles.length > 0 && (
              <div>
                <h3 className="text-lg font-heading font-semibold text-slate-200 mb-3">
                  Related Articles
                </h3>
                <div className="space-y-2">
                  {relatedArticles.map((relatedId, index) => (
                    <button
                      key={index}
                      onClick={() => onViewRelated?.(relatedId)}
                      className="w-full text-left px-4 py-3 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 border border-slate-700/50 hover:border-slate-600/50 transition-all group"
                    >
                      <div className="flex items-center gap-2">
                        <DocumentTextIcon className="w-4 h-4 text-slate-400 group-hover:text-slate-300" />
                        <span className="text-sm text-slate-300 group-hover:text-slate-200">
                          Related Article {index + 1}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-700/50">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </Card>
      </div>
    </>
  );
}
