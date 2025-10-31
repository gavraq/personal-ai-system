/**
 * DomainFilter Component
 * Filter and search controls for skills
 */

'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/utils';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

export interface FilterState {
  search: string;
  domain: string | null;
  sortBy: 'name' | 'popularity' | 'recent';
  showFavoritesOnly: boolean;
}

export interface DomainFilterProps {
  domains: string[];
  filter: FilterState;
  onFilterChange: (filter: FilterState) => void;
  skillCount?: number;
  className?: string;
}

/**
 * DomainFilter Component
 *
 * Provides filtering and searching capabilities:
 * - Search by name/description
 * - Filter by domain
 * - Sort options
 * - Favorites filter
 *
 * @example
 * ```tsx
 * <DomainFilter
 *   domains={['Project Management', 'Risk Analysis']}
 *   filter={filterState}
 *   onFilterChange={setFilterState}
 *   skillCount={45}
 * />
 * ```
 */
export function DomainFilter({
  domains,
  filter,
  onFilterChange,
  skillCount,
  className
}: DomainFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSearchChange = (value: string) => {
    onFilterChange({ ...filter, search: value });
  };

  const handleDomainChange = (domain: string | null) => {
    onFilterChange({ ...filter, domain });
  };

  const handleSortChange = (sortBy: FilterState['sortBy']) => {
    onFilterChange({ ...filter, sortBy });
  };

  const toggleFavorites = () => {
    onFilterChange({ ...filter, showFavoritesOnly: !filter.showFavoritesOnly });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      domain: null,
      sortBy: 'name',
      showFavoritesOnly: false
    });
  };

  const hasActiveFilters =
    filter.search ||
    filter.domain ||
    filter.sortBy !== 'name' ||
    filter.showFavoritesOnly;

  return (
    <Card variant="glass" className={className}>
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search skills..."
            value={filter.search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter Toggle */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <FunnelIcon className="w-4 h-4" />
            <span>Filters</span>
            {hasActiveFilters && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-blue-500/20 text-blue-400">
                Active
              </span>
            )}
          </button>

          {skillCount !== undefined && (
            <span className="text-sm text-slate-500">
              {skillCount} skill{skillCount !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {/* Expanded Filters */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t border-slate-700/50">
            {/* Domain Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Domain
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleDomainChange(null)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                    filter.domain === null
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  )}
                >
                  All
                </button>
                {domains.map((domain) => (
                  <button
                    key={domain}
                    onClick={() => handleDomainChange(domain)}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                      filter.domain === domain
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    )}
                  >
                    {domain}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Sort By
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => handleSortChange('name')}
                  className={cn(
                    'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    filter.sortBy === 'name'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  )}
                >
                  Name
                </button>
                <button
                  onClick={() => handleSortChange('popularity')}
                  className={cn(
                    'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    filter.sortBy === 'popularity'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  )}
                >
                  Popularity
                </button>
                <button
                  onClick={() => handleSortChange('recent')}
                  className={cn(
                    'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    filter.sortBy === 'recent'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  )}
                >
                  Recent
                </button>
              </div>
            </div>

            {/* Favorites Toggle */}
            <div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showFavoritesOnly}
                  onChange={toggleFavorites}
                  className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900"
                />
                <span className="text-sm text-slate-300">
                  Show favorites only
                </span>
              </label>
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
              >
                <XMarkIcon className="w-4 h-4" />
                <span>Clear all filters</span>
              </button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
