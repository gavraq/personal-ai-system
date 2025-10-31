/**
 * Category Filter Component
 * Filter and search controls for knowledge articles
 */

'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
  BookmarkIcon
} from '@heroicons/react/24/outline';

export interface FilterState {
  search: string;
  category: string | null;
  sortBy: 'recent' | 'popular' | 'title';
  showBookmarksOnly: boolean;
}

export interface CategoryFilterProps {
  categories: string[];
  filter: FilterState;
  onFilterChange: (filter: FilterState) => void;
  className?: string;
}

/**
 * Category Filter Component
 */
export function CategoryFilter({
  categories,
  filter,
  onFilterChange,
  className = ''
}: CategoryFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSearchChange = (value: string) => {
    onFilterChange({ ...filter, search: value });
  };

  const handleCategoryChange = (category: string | null) => {
    onFilterChange({ ...filter, category });
  };

  const handleSortChange = (sortBy: 'recent' | 'popular' | 'title') => {
    onFilterChange({ ...filter, sortBy });
  };

  const handleBookmarksToggle = () => {
    onFilterChange({ ...filter, showBookmarksOnly: !filter.showBookmarksOnly });
  };

  const handleClearFilters = () => {
    onFilterChange({
      search: '',
      category: null,
      sortBy: 'recent',
      showBookmarksOnly: false
    });
    setIsExpanded(false);
  };

  const hasActiveFilters = filter.search || filter.category || filter.showBookmarksOnly;

  return (
    <div className={`rounded-lg transition-all duration-200 glass-card p-4 ${className}`}>
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search articles..."
            value={filter.search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter Toggle Button */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <FunnelIcon className="w-4 h-4" />
            <span>{isExpanded ? 'Hide Filters' : 'Show Filters'}</span>
          </button>

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              <XMarkIcon className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          )}
        </div>

        {/* Expandable Filters */}
        {isExpanded && (
          <div className="space-y-4 pt-2 border-t border-slate-700/50">
            {/* Category Filters */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">
                Category
              </label>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={filter.category === null ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => handleCategoryChange(null)}
                >
                  All Categories
                </Button>
                {categories.map((category) => (
                  <Button
                    key={category}
                    variant={filter.category === category ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleCategoryChange(category)}
                  >
                    {category}
                  </Button>
                ))}
              </div>
            </div>

            {/* Sort Options */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">
                Sort By
              </label>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={filter.sortBy === 'recent' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => handleSortChange('recent')}
                >
                  Most Recent
                </Button>
                <Button
                  variant={filter.sortBy === 'popular' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => handleSortChange('popular')}
                >
                  Most Popular
                </Button>
                <Button
                  variant={filter.sortBy === 'title' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => handleSortChange('title')}
                >
                  Title (A-Z)
                </Button>
              </div>
            </div>

            {/* Bookmarks Filter */}
            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showBookmarksOnly}
                  onChange={handleBookmarksToggle}
                  className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:ring-offset-0"
                />
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <BookmarkIcon className="w-4 h-4" />
                  <span>Show bookmarked articles only</span>
                </div>
              </label>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
