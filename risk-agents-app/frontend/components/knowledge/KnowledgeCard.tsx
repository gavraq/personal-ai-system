/**
 * Knowledge Card Component
 * Displays individual knowledge articles with metadata
 */

'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  DocumentTextIcon,
  ClockIcon,
  TagIcon,
  BookmarkIcon as BookmarkIconOutline,
  ArrowTopRightOnSquareIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/react/24/solid';

/**
 * Knowledge Article Interface
 * Enhanced with YAML frontmatter metadata fields
 */
export interface KnowledgeArticle {
  id: string;
  title: string;
  summary: string;
  category: string;
  content?: string;
  tags?: string[];
  lastUpdated: Date;
  readTime?: number;
  views?: number;
  isBookmarked?: boolean;
  author?: string;
  relatedArticles?: string[];

  // YAML frontmatter fields (from backend)
  slug?: string;
  description?: string;
  artefact_type?: string;       // policy, framework, methodology, model, etc.
  risk_domain?: string;          // Market Risk, Model Risk, etc.
  owner?: string;
  approval_date?: string;
  version?: string;
  related_artefacts?: Record<string, string[]>;  // { methodologies: [...], models: [...], ... }
  related_skills?: string[];
  difficulty?: string;          // Beginner, Intermediate, Advanced
  reading_time?: string;        // "30 min", "15 min", etc.
}

export interface KnowledgeCardProps {
  article: KnowledgeArticle;
  onViewDetails?: (article: KnowledgeArticle) => void;
  onToggleBookmark?: (articleId: string) => void;
  className?: string;
}

/**
 * Format last updated timestamp to relative time
 */
function formatLastUpdated(date: Date): string {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
  return `${Math.floor(diffInDays / 365)} years ago`;
}

/**
 * Get category color classes based on Risk Taxonomy Framework
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
 * Knowledge Card Component
 */
export function KnowledgeCard({
  article,
  onViewDetails,
  onToggleBookmark,
  className = ''
}: KnowledgeCardProps) {
  const {
    title,
    summary,
    category,
    tags = [],
    lastUpdated,
    readTime,
    views,
    isBookmarked = false
  } = article;

  const categoryColor = getCategoryColor(category);
  const visibleTags = tags.slice(0, 3);
  const remainingTags = tags.length - 3;

  return (
    <Card variant="glass" className={`p-4 group transition-all duration-300 hover:border-slate-600/50 ${className}`}>
      {/* Header with Category and Bookmark */}
      <div className="flex items-start justify-between mb-3">
        <span className={`px-3 py-1 rounded-md text-xs font-semibold border ${categoryColor}`}>
          {category}
        </span>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleBookmark?.(article.id);
          }}
          className="text-slate-400 hover:text-blue-400 transition-colors"
          aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
        >
          {isBookmarked ? (
            <BookmarkIconSolid className="w-5 h-5 text-blue-400" />
          ) : (
            <BookmarkIconOutline className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Title */}
      <h3 className="text-lg font-heading font-semibold text-slate-200 mb-2 group-hover:text-slate-100 line-clamp-2">
        {title}
      </h3>

      {/* Summary */}
      <p className="text-sm text-slate-400 mb-4 line-clamp-3">
        {summary}
      </p>

      {/* Metadata */}
      <div className="flex flex-wrap items-center gap-4 mb-4 text-xs text-slate-500">
        {/* Last Updated */}
        <div className="flex items-center gap-1">
          <ClockIcon className="w-4 h-4" />
          <span>{formatLastUpdated(lastUpdated)}</span>
        </div>

        {/* Read Time */}
        {readTime && (
          <div className="flex items-center gap-1">
            <DocumentTextIcon className="w-4 h-4" />
            <span>{readTime} min read</span>
          </div>
        )}

        {/* Views */}
        {views !== undefined && (
          <div className="flex items-center gap-1">
            <EyeIcon className="w-4 h-4" />
            <span>{views.toLocaleString()} views</span>
          </div>
        )}
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {visibleTags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs rounded-md bg-slate-800/50 text-slate-400 border border-slate-700/50"
            >
              {tag}
            </span>
          ))}
          {remainingTags > 0 && (
            <span className="px-2 py-1 text-xs rounded-md bg-slate-800/50 text-slate-500 border border-slate-700/50">
              +{remainingTags} more
            </span>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 pt-4 border-t border-slate-700/50">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onViewDetails?.(article)}
          className="flex-1"
        >
          <ArrowTopRightOnSquareIcon className="w-4 h-4 mr-1" />
          Read More
        </Button>
      </div>
    </Card>
  );
}

/**
 * Knowledge Grid Component
 */
export interface KnowledgeGridProps {
  articles: KnowledgeArticle[];
  onViewDetails?: (article: KnowledgeArticle) => void;
  onToggleBookmark?: (articleId: string) => void;
  emptyMessage?: string;
  className?: string;
}

export function KnowledgeGrid({
  articles,
  onViewDetails,
  onToggleBookmark,
  emptyMessage = 'No articles found',
  className = ''
}: KnowledgeGridProps) {
  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <p className="text-slate-400 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
      {articles.map((article) => (
        <KnowledgeCard
          key={article.id}
          article={article}
          onViewDetails={onViewDetails}
          onToggleBookmark={onToggleBookmark}
        />
      ))}
    </div>
  );
}
