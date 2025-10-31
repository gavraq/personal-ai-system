/**
 * Skills Browser Page
 * Browse, filter, and execute available skills
 */

'use client';

import { useState, useMemo, useEffect } from 'react';
import { PageContainer } from '@/components/ui/Layout';
import { PageHeader } from '@/components/ui/Layout';
import { Breadcrumbs } from '@/components/ui/Layout';
import { DomainFilter, FilterState } from '@/components/skills/DomainFilter';
import { SkillGrid, Skill } from '@/components/skills/SkillCard';
import { SkillDetails } from '@/components/skills/SkillDetails';
import { SkillExecutor } from '@/components/skills/SkillExecutor';
import { api } from '@/lib/api';
import { mapSkillMetadataToSkill, loadFavorites, toggleFavorite as toggleFavoriteUtil, getSkillPathFromSkill } from '@/lib/skills-utils';


/**
 * Extract unique domains from skills
 */
function getUniqueDomains(skills: Skill[]): string[] {
  const domains = new Set(skills.map(skill => skill.domain));
  return Array.from(domains).sort();
}

/**
 * Filter and sort skills based on current filter state
 */
function filterSkills(skills: Skill[], filter: FilterState): Skill[] {
  let filtered = [...skills];

  // Apply search filter
  if (filter.search) {
    const searchLower = filter.search.toLowerCase();
    filtered = filtered.filter(skill =>
      skill.name.toLowerCase().includes(searchLower) ||
      skill.description.toLowerCase().includes(searchLower) ||
      skill.tags?.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }

  // Apply domain filter
  if (filter.domain) {
    filtered = filtered.filter(skill => skill.domain === filter.domain);
  }

  // Apply favorites filter
  if (filter.showFavoritesOnly) {
    filtered = filtered.filter(skill => skill.isFavorite);
  }

  // Apply sorting
  filtered.sort((a, b) => {
    switch (filter.sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'popularity':
        return (b.successRate || 0) - (a.successRate || 0);
      case 'recent':
        // Mock recent order - in production would use lastUsed timestamp
        return 0;
      default:
        return 0;
    }
  });

  return filtered;
}

/**
 * Skills Browser Page Component
 */
export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterState>({
    search: '',
    domain: null,
    sortBy: 'name',
    showFavoritesOnly: false
  });
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isExecutorOpen, setIsExecutorOpen] = useState(false);

  const domains = useMemo(() => getUniqueDomains(skills), [skills]);
  const filteredSkills = useMemo(() => filterSkills(skills, filter), [skills, filter]);

  // Load skills from API on mount
  useEffect(() => {
    async function loadSkills() {
      try {
        setLoading(true);
        setError(null);

        // Fetch all skills metadata from backend
        const skillsMetadata = await api.getSkills();

        // Load favorites from localStorage
        const favorites = loadFavorites();

        // Fetch metrics for each skill and map to frontend format
        const skillsPromises = skillsMetadata.map(async (metadata) => {
          const skillPath = `${metadata.domain}/${metadata.name}`;
          let metrics;

          try {
            metrics = await api.getSkillMetrics(skillPath);
          } catch (metricsError) {
            console.warn(`Could not fetch metrics for ${skillPath}:`, metricsError);
            // Continue without metrics
          }

          // Map backend format to frontend format
          const skill = mapSkillMetadataToSkill(metadata, metrics);
          skill.isFavorite = favorites.has(skill.id);
          return skill;
        });

        const loadedSkills = await Promise.all(skillsPromises);
        setSkills(loadedSkills);
      } catch (err) {
        console.error('Error loading skills:', err);
        setError(err instanceof Error ? err.message : 'Failed to load skills');
      } finally {
        setLoading(false);
      }
    }

    loadSkills();
  }, []);

  const handleFilterChange = (newFilter: FilterState) => {
    setFilter(newFilter);
  };

  const handleViewDetails = (skill: Skill) => {
    setSelectedSkill(skill);
    setIsDetailsOpen(true);
  };

  const handleExecute = (skill: Skill) => {
    setSelectedSkill(skill);
    setIsExecutorOpen(true);
  };

  const handleToggleFavorite = (skillId: string) => {
    // Update favorites in localStorage
    toggleFavoriteUtil(skillId);

    // Update skills state
    setSkills(prevSkills =>
      prevSkills.map(skill =>
        skill.id === skillId
          ? { ...skill, isFavorite: !skill.isFavorite }
          : skill
      )
    );
  };

  const handleExecuteSkill = async (skillId: string, parameters: Record<string, any>) => {
    try {
      // Find the skill to get its path
      const skill = skills.find(s => s.id === skillId);
      if (!skill) {
        throw new Error(`Skill not found: ${skillId}`);
      }

      // Get the skill path (e.g., "change-agent/meeting-minutes-capture")
      const skillPath = getSkillPathFromSkill(skill);

      // Execute the skill via backend API
      const result = await api.executeSkill(skillPath, parameters);

      console.log('Skill execution result:', result);
      return result;
    } catch (error) {
      console.error('Error executing skill:', error);
      throw error;
    }
  };

  const handleDetailsExecute = (skill: Skill) => {
    setIsDetailsOpen(false);
    setIsExecutorOpen(true);
  };

  const handleRetry = () => {
    setError(null);
    setLoading(true);
    window.location.reload();
  };

  // Loading state
  if (loading) {
    return (
      <PageContainer>
        <Breadcrumbs
          items={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Skills', href: '/skills' }
          ]}
        />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-slate-400">Loading skills...</p>
          </div>
        </div>
      </PageContainer>
    );
  }

  // Error state
  if (error) {
    return (
      <PageContainer>
        <Breadcrumbs
          items={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Skills', href: '/skills' }
          ]}
        />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center max-w-md">
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6 mb-4">
              <p className="text-red-400 mb-4">{error}</p>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Skills', href: '/skills' }
        ]}
      />

      {/* Page Header */}
      <PageHeader
        title="Skills Browser"
        description="Browse and execute available Risk Agent skills"
        actions={
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span className="font-semibold text-slate-300">
              {filteredSkills.length}
            </span>
            <span>
              {filteredSkills.length === 1 ? 'skill' : 'skills'} available
            </span>
          </div>
        }
      />

      {/* Filters */}
      <div className="mb-6">
        <DomainFilter
          domains={domains}
          filter={filter}
          onFilterChange={handleFilterChange}
        />
      </div>

      {/* Skills Grid */}
      <SkillGrid
        skills={filteredSkills}
        onViewDetails={handleViewDetails}
        onExecute={handleExecute}
        onToggleFavorite={handleToggleFavorite}
        emptyMessage={
          filter.search || filter.domain || filter.showFavoritesOnly
            ? 'No skills match your current filters'
            : 'No skills available'
        }
      />

      {/* Skill Details Modal */}
      <SkillDetails
        skill={selectedSkill}
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        onExecute={handleDetailsExecute}
      />

      {/* Skill Executor Modal */}
      <SkillExecutor
        skill={selectedSkill}
        isOpen={isExecutorOpen}
        onClose={() => setIsExecutorOpen(false)}
        onExecute={handleExecuteSkill}
      />
    </PageContainer>
  );
}
