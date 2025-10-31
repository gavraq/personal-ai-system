/**
 * Knowledge Browser Page
 * Browse and search Risk Taxonomy Framework articles
 */

'use client';

import { useState, useMemo, useEffect } from 'react';
import { PageContainer } from '@/components/ui/Layout';
import { PageHeader } from '@/components/ui/Layout';
import { Breadcrumbs } from '@/components/ui/Layout';
import { CategoryFilter, FilterState } from '@/components/knowledge/CategoryFilter';
import { KnowledgeGrid, KnowledgeArticle } from '@/components/knowledge/KnowledgeCard';
import { KnowledgeDetails } from '@/components/knowledge/KnowledgeDetails';
import api, { KnowledgeDocument } from '@/lib/api';

/**
 * Transform API KnowledgeDocument to KnowledgeArticle format
 */
function transformToArticle(doc: KnowledgeDocument): KnowledgeArticle {
  // Extract summary from description or first 200 chars of content
  const summary = doc.description || doc.content.substring(0, 200) + '...';

  // Parse reading time to number (e.g., "30 min" -> 30)
  const readTime = doc.reading_time
    ? parseInt(doc.reading_time.replace(/\D/g, ''))
    : undefined;

  return {
    id: doc.slug || doc.filename.replace('.md', ''),
    title: doc.title,
    summary: summary,
    category: doc.category,
    content: doc.content,
    tags: doc.tags || [],
    lastUpdated: doc.approval_date ? new Date(doc.approval_date) : new Date(),
    readTime: readTime,
    views: undefined, // Not tracked yet
    isBookmarked: false, // Client-side state
    author: doc.owner,
    relatedArticles: [], // Will be populated from related_artefacts if needed
    // YAML frontmatter fields
    slug: doc.slug,
    description: doc.description,
    artefact_type: doc.artefact_type,
    risk_domain: doc.risk_domain,
    owner: doc.owner,
    approval_date: doc.approval_date,
    version: doc.version,
    related_artefacts: doc.related_artefacts,
    related_skills: doc.related_skills,
    difficulty: doc.difficulty,
    reading_time: doc.reading_time
  };
}

/**
 * Mock Knowledge Articles Data - Risk Taxonomy Framework
 * DEPRECATED: This mock data is kept for fallback only
 */
const MOCK_ARTICLES: KnowledgeArticle[] = [
  {
    id: 'kb-001',
    title: 'Credit Risk Policy Framework',
    summary: 'Comprehensive credit risk policy document covering risk appetite, governance structure, key controls, and RCSA processes for credit risk management across all business lines.',
    content: 'The Credit Risk Policy Framework provides the foundation for managing credit risk across ICBCS. This policy document establishes the risk appetite statements, defines governance responsibilities, and identifies all key controls required for effective credit risk management.\n\nKey sections include: Executive Summary, Governance Structure (referencing Credit Risk Committee mandate and membership), Core Processes (credit approval, limit monitoring, reporting), Key Controls (identified through RCSA), and Policy Review Schedule.\n\nAll processes referenced in this policy are documented using Operational Risk process map templates and link to the comprehensive controls inventory maintained by Operational Risk.',
    category: 'Policies',
    tags: ['credit-risk', 'policy', 'governance', 'risk-appetite', 'key-controls'],
    lastUpdated: new Date(2025, 9, 20),
    readTime: 15,
    views: 2847,
    isBookmarked: true,
    author: 'Risk Policy Team',
    relatedArticles: ['kb-002', 'kb-005']
  },
  {
    id: 'kb-002',
    title: 'Credit Risk Committee Terms of Reference',
    summary: 'Official mandate, membership, meeting frequency, and decision-making authority for the Credit Risk Committee - the primary governance forum for credit risk matters.',
    content: 'The Credit Risk Committee (CRC) is the primary governance forum for credit risk management. This document defines the committee\'s mandate, membership composition, meeting frequency, quorum requirements, and escalation procedures.\n\nMembership includes: Chief Credit Officer (Chair), Head of Credit Risk Analytics, Head of Credit Risk Reporting, representatives from each business line, and attendance from Operational Risk and Internal Audit.\n\nThe CRC meets monthly and has authority to approve credit limits up to £50M, review limit breaches, approve methodology changes, and escalate material issues to the Executive Risk Committee.',
    category: 'Governance',
    tags: ['governance', 'credit-risk', 'committee', 'mandate', 'terms-of-reference'],
    lastUpdated: new Date(2025, 9, 15),
    readTime: 8,
    views: 1523,
    isBookmarked: false,
    author: 'Governance Team',
    relatedArticles: ['kb-001', 'kb-003']
  },
  {
    id: 'kb-003',
    title: 'Credit Approval Process Map',
    summary: 'Detailed process flow for credit approval workflow including roles, responsibilities, approval authorities, key controls, and escalation procedures documented using Operational Risk templates.',
    content: 'The Credit Approval Process defines the end-to-end workflow for assessing and approving credit exposure across all business lines. This process map follows the standard Operational Risk process map template.\n\nProcess steps include: Initial Credit Request, Credit Analysis, Risk Rating Assignment, Limit Recommendation, Approval (based on authority matrix), Documentation, and System Update.\n\nKey controls embedded in this process: Segregation of duties between trading and credit risk, independent risk rating validation, dual approval for limits >£10M, automated limit monitoring, and quarterly limit review requirement.',
    category: 'Processes & Procedures',
    tags: ['credit-approval', 'process-map', 'workflow', 'controls', 'operational-risk'],
    lastUpdated: new Date(2025, 9, 18),
    readTime: 12,
    views: 1967,
    isBookmarked: true,
    author: 'Process Documentation Team',
    relatedArticles: ['kb-001', 'kb-004']
  },
  {
    id: 'kb-004',
    title: 'Credit Limit Monitoring Controls Inventory',
    summary: 'Inventory of all controls for credit limit monitoring including key controls (RCSA-identified), control descriptions, frequencies, owners, and testing requirements.',
    content: 'The Credit Limit Monitoring Controls Inventory documents all controls embedded in the credit limit monitoring process. This inventory distinguishes between key controls and non-key controls as identified through the Risk and Control Self-Assessment (RCSA) process.\n\nKey Controls: Daily automated limit monitoring (System: CRMS), Independent limit breach notification (Process: Alert generation), Escalation to CRC for material breaches (Governance: Committee review), Monthly limit utilization reporting (Report: Credit Dashboard).\n\nEach control specifies: Control ID (linkage to ORIS), Description, Frequency, Owner, Testing approach, and remediation procedures for control failures.',
    category: 'Controls',
    tags: ['controls', 'key-controls', 'rcsa', 'limit-monitoring', 'testing'],
    lastUpdated: new Date(2025, 9, 12),
    readTime: 10,
    views: 1345,
    isBookmarked: false,
    author: 'Operational Risk Team',
    relatedArticles: ['kb-003', 'kb-007']
  },
  {
    id: 'kb-005',
    title: 'Approved Products List - Interest Rate Derivatives',
    summary: 'Inventory of approved interest rate derivative products including product specifications, risk characteristics, approval dates, and linkage to valuation and risk methodologies.',
    content: 'The Approved Products List for Interest Rate Derivatives documents all products approved for trading through the Trade Execution Framework (TEF). Each product entry includes detailed specifications to ensure appropriate risk management.\n\nProduct entries include: Product Name, Product Code, Description, Risk Characteristics (delta, gamma, vega sensitivities), Valuation Methodology (curve dependencies), Risk Model (VaR methodology), Market Data Requirements (feeds needed), Approval Date, and Last Review Date.\n\nExamples: Interest Rate Swaps (IRS), Cross-Currency Swaps (CCS), Swaptions (European and Bermudan), Inflation Swaps, Basis Swaps. Each product references the specific curve inventory and methodology documents used for valuation and risk calculation.',
    category: 'Products',
    tags: ['products', 'derivatives', 'interest-rate', 'approved-products', 'tef'],
    lastUpdated: new Date(2025, 9, 22),
    readTime: 14,
    views: 1789,
    isBookmarked: true,
    author: 'Product Control Team',
    relatedArticles: ['kb-001', 'kb-009']
  },
  {
    id: 'kb-006',
    title: 'Credit Risk Dashboard - Report Specification',
    summary: 'Report inventory entry for the Credit Risk Dashboard including distribution frequency, recipients, data sources, BCBS239 compliance, and report owner responsibilities.',
    content: 'The Credit Risk Dashboard is the primary management information report for credit risk. This report specification follows BCBS239 principles for risk data aggregation and reporting.\n\nReport Details: Frequency (Daily, with monthly Board pack version), Distribution (Email + Online Portal), Report Owner (Head of Credit Risk Reporting), Last Review Date, Data Sources (CRMS, Trading Systems, Market Data), Automated Generation (Yes - with manual commentary).\n\nReport Sections: Executive Summary, Limit Utilization by Business Line, Top 20 Exposures, Limit Breaches, Credit Rating Migrations, Concentration Analysis, Trend Analysis (30-day and 90-day).\n\nQuality Controls: Automated reconciliation to source systems, manual review checklist, sign-off process, and exception reporting for data quality issues.',
    category: 'Reports',
    tags: ['reports', 'dashboard', 'bcbs239', 'mi', 'credit-risk'],
    lastUpdated: new Date(2025, 9, 25),
    readTime: 11,
    views: 2156,
    isBookmarked: false,
    author: 'Credit Risk Reporting Team',
    relatedArticles: ['kb-001', 'kb-008']
  },
  {
    id: 'kb-007',
    title: 'Trading System to CRMS Feed Interface',
    summary: 'Feed inventory entry documenting the interface between trading systems and Credit Risk Management System (CRMS) including IDD specification, SLA, frequency, and data quality controls.',
    content: 'The Trading System to CRMS Feed is a critical data interface delivering real-time position and exposure data. This feed inventory entry includes the Interface Definition Document (IDD) and Service Level Agreement (SLA).\n\nFeed Specification: Feed Name (TS-CRMS-001), Source System (Trading Platform), Target System (CRMS), Frequency (Real-time, 15-second latency SLA), Format (XML), Transport (MQ Series), Feed Owner (Trading Technology).\n\nInterface Definition Document (IDD): Data fields (Trade ID, Counterparty ID, Notional, Currency, Product Type, Valuation, Delta, Gamma), Data types, Validation rules, Error handling procedures.\n\nData Quality Controls: Timeliness (15-second SLA monitoring), Accuracy (automated reconciliation to trading blotter), Completeness (record count validation), Exception alerting (automated notifications for SLA breaches or validation failures).',
    category: 'Feeds',
    tags: ['feeds', 'interface', 'idd', 'sla', 'data-quality'],
    lastUpdated: new Date(2025, 9, 10),
    readTime: 13,
    views: 1423,
    isBookmarked: true,
    author: 'Data Integration Team',
    relatedArticles: ['kb-004', 'kb-008']
  },
  {
    id: 'kb-008',
    title: 'Credit Exposure Data Dictionary',
    summary: 'Data inventory documenting all credit exposure metrics including upstream input data (from feeds), calculated output data (from models), data quality controls, and ownership.',
    content: 'The Credit Exposure Data Dictionary provides a comprehensive inventory of all data domains required for credit risk reporting. This includes both upstream input data (specified in feed IDDs) and calculated output data (produced by risk models).\n\nData Domains: Counterparty Master Data, Position Data (from trading feeds), Market Data (from market data feeds), Credit Exposure Calculations (output from CVA model), Potential Future Exposure (output from PFE model), Expected Exposure (output from simulation model).\n\nFor each data element: Data Element Name, Definition, Data Type, Source (system and feed), Calculation Logic (for derived metrics), Model Reference (for model outputs), Quality Controls (timeliness, accuracy, completeness checks), Data Owner, Last Validated Date.\n\nQuality Control Framework: Automated validation rules, reconciliation procedures, exception handling, remediation workflows, and monthly data quality reporting to the Data Governance Committee.',
    category: 'Data',
    tags: ['data', 'data-dictionary', 'data-quality', 'metrics', 'exposure'],
    lastUpdated: new Date(2025, 9, 8),
    readTime: 16,
    views: 1876,
    isBookmarked: false,
    author: 'Data Governance Team',
    relatedArticles: ['kb-006', 'kb-007', 'kb-009']
  },
  {
    id: 'kb-009',
    title: 'CVA Methodology and Model Registry Entry',
    summary: 'Comprehensive methodology document for Credit Valuation Adjustment (CVA) calculation including model theory, implementation, calibration, validation status, and curve dependencies.',
    content: 'The CVA Methodology document provides the theoretical foundation and implementation details for CVA calculation across all credit portfolios. This is the primary reference for the CVA model registered in the Model Registry (Model ID: CVA-001).\n\nMethodology Overview: CVA represents the market value of counterparty credit risk. The model uses a Monte Carlo simulation approach with 10,000 scenarios to project future exposure profiles and applies counterparty credit spreads to value the default risk.\n\nKey Components: Exposure Simulation Engine (using IR and FX curves), Credit Spread Curves (sourced from CDS market data), Wrong-Way Risk Adjustments, Netting Set Aggregation, Collateral Modeling (CSA terms).\n\nCurve Dependencies: Interest Rate Curves (sourced from Curve Inventory CI-001 through CI-045), FX Curves (CI-101 through CI-125), Credit Spread Curves (CI-201 through CI-250).\n\nModel Governance: Annual validation by Model Validation Team, quarterly recalibration, monthly performance monitoring, change control process for methodology updates (requires Model Risk Committee approval).',
    category: 'Methodologies & Models',
    tags: ['cva', 'methodology', 'model', 'curves', 'validation'],
    lastUpdated: new Date(2025, 9, 5),
    readTime: 18,
    views: 2543,
    isBookmarked: true,
    author: 'Model Development Team',
    relatedArticles: ['kb-005', 'kb-008', 'kb-010']
  },
  {
    id: 'kb-010',
    title: 'Credit Risk Management System (CRMS) Configuration',
    summary: 'Systems inventory entry for CRMS including system architecture, data flows, integration points, configuration management, and End User Computing (EUC) dependencies.',
    content: 'The Credit Risk Management System (CRMS) is the primary system for credit risk calculation, monitoring, and reporting. This systems inventory entry documents the complete system architecture and all integration points.\n\nSystem Overview: Platform (Windows Server 2019), Database (SQL Server 2019), Application (Custom C# application), Deployment (Production cluster with DR), Ownership (Credit Risk Technology Team).\n\nData Flow: Inbound feeds from Trading Systems (TS-CRMS-001), Market Data System (MD-CRMS-001), Counterparty Master Data (CDM-CRMS-001). Outbound feeds to Risk Dashboard (CRMS-RD-001), Data Warehouse (CRMS-DW-001), Regulatory Reporting (CRMS-RR-001).\n\nSystem Configuration: Limit hierarchies (configured in XML), Calculation rules (stored procedures), User access (AD integration), Workflow rules (approval matrices).\n\nEnd User Computing (EUC): Excel-based position reconciliation tool (documented EUC-CR-001), Access database for manual limit overrides (EUC-CR-002 - pending replacement with system enhancement).\n\nChange Management: All system changes follow standard SDLC process, configuration changes require dual approval, deployment follows release calendar with monthly production windows.',
    category: 'Systems',
    tags: ['systems', 'crms', 'architecture', 'euc', 'integration'],
    lastUpdated: new Date(2025, 9, 14),
    readTime: 15,
    views: 1678,
    isBookmarked: false,
    author: 'Technology Documentation Team',
    relatedArticles: ['kb-007', 'kb-008']
  },
  {
    id: 'kb-011',
    title: 'Risk Taxonomy - Credit Risk Classification',
    summary: 'Inventory of credit risk types and sub-types providing the classification scheme for comprehensive credit risk management across all business lines and product types.',
    content: 'The Credit Risk Taxonomy provides a structured classification of all credit risk types faced by ICBCS. This taxonomy enables consistent risk identification, measurement, and management across the organization.\n\nTop-Level Risk: Credit Risk - The risk of loss arising from a borrower or counterparty failing to meet their contractual obligations.\n\nSub-Types: Counterparty Credit Risk (OTC derivatives and securities financing), Issuer Risk (bond holdings and securitizations), Settlement Risk (failed settlements in payment and securities systems), Country Risk (sovereign and transfer risk), Concentration Risk (single name and sector concentrations).\n\nFor Counterparty Credit Risk - Further Classification: Pre-Settlement Risk (mark-to-market exposure before maturity), Settlement Risk (delivery-versus-payment exposures), Wrong-Way Risk (correlation between exposure and counterparty credit quality), Correlation Risk (joint default scenarios in portfolio context).\n\nRisk Identification Framework: Each business line maps their activities to relevant risk sub-types, policies reference specific risk types, controls target identified risks, methodologies calculate risk metrics for each type, reports aggregate by risk classification.\n\nThis taxonomy facilitates: Complete risk coverage assessment, Consistent application of controls across domains, Clear communication with regulators and auditors, Effective change management (what risks are impacted by changes).',
    category: 'Risks',
    tags: ['risk-taxonomy', 'credit-risk', 'classification', 'risk-types', 'framework'],
    lastUpdated: new Date(2025, 9, 1),
    readTime: 12,
    views: 3127,
    isBookmarked: true,
    author: 'Risk Taxonomy Team',
    relatedArticles: ['kb-001', 'kb-002']
  }
];

/**
 * Extract unique categories from articles
 */
function getUniqueCategories(articles: KnowledgeArticle[]): string[] {
  const categories = new Set(articles.map(article => article.category));
  return Array.from(categories).sort();
}

/**
 * Filter and sort articles based on current filter state
 */
function filterArticles(articles: KnowledgeArticle[], filter: FilterState): KnowledgeArticle[] {
  let filtered = [...articles];

  // Apply search filter
  if (filter.search) {
    const searchLower = filter.search.toLowerCase();
    filtered = filtered.filter(article =>
      article.title.toLowerCase().includes(searchLower) ||
      article.summary.toLowerCase().includes(searchLower) ||
      article.tags?.some(tag => tag.toLowerCase().includes(searchLower)) ||
      article.author?.toLowerCase().includes(searchLower)
    );
  }

  // Apply category filter
  if (filter.category) {
    filtered = filtered.filter(article => article.category === filter.category);
  }

  // Apply bookmarks filter
  if (filter.showBookmarksOnly) {
    filtered = filtered.filter(article => article.isBookmarked);
  }

  // Apply sorting
  filtered.sort((a, b) => {
    switch (filter.sortBy) {
      case 'title':
        return a.title.localeCompare(b.title);
      case 'popular':
        return (b.views || 0) - (a.views || 0);
      case 'recent':
      default:
        return b.lastUpdated.getTime() - a.lastUpdated.getTime();
    }
  });

  return filtered;
}

/**
 * Knowledge Browser Page Component
 */
export default function KnowledgePage() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterState>({
    search: '',
    category: null,
    sortBy: 'recent',
    showBookmarksOnly: false
  });
  const [selectedArticle, setSelectedArticle] = useState<KnowledgeArticle | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  // Load knowledge documents from API
  useEffect(() => {
    async function loadKnowledge() {
      try {
        setLoading(true);
        setError(null);

        // Get taxonomy to discover all documents
        const taxonomy = await api.getTaxonomy();

        // Load all documents
        const allDocuments: KnowledgeDocument[] = [];

        // Parse nested taxonomy structure
        for (const domain of taxonomy.domains) {
          for (const category of domain.children) {
            for (const doc of category.children) {
              try {
                // Extract filename from path (e.g., "market-risk/policies/var-policy.md" -> "var-policy.md")
                const filename = doc.name + '.md';

                // Fetch full document content
                const fullDoc = await api.getDocument(domain.name, category.name, filename);
                allDocuments.push(fullDoc);
              } catch (docError) {
                console.error(`Failed to load ${doc.path}:`, docError);
                // Continue loading other documents
              }
            }
          }
        }

        // Transform to article format
        const transformedArticles = allDocuments.map(transformToArticle);
        setArticles(transformedArticles);

        console.log(`Loaded ${transformedArticles.length} knowledge documents`);
      } catch (err) {
        console.error('Failed to load knowledge:', err);
        setError('Failed to load knowledge documents. Using fallback data.');
        // Fallback to mock data on error
        setArticles(MOCK_ARTICLES);
      } finally {
        setLoading(false);
      }
    }

    loadKnowledge();
  }, []);

  const categories = useMemo(() => getUniqueCategories(articles), [articles]);
  const filteredArticles = useMemo(() => filterArticles(articles, filter), [articles, filter]);

  const handleFilterChange = (newFilter: FilterState) => {
    setFilter(newFilter);
  };

  const handleViewDetails = (article: KnowledgeArticle) => {
    setSelectedArticle(article);
    setIsDetailsOpen(true);
  };

  const handleToggleBookmark = (articleId: string) => {
    setArticles(prevArticles =>
      prevArticles.map(article =>
        article.id === articleId
          ? { ...article, isBookmarked: !article.isBookmarked }
          : article
      )
    );

    // Update selected article if it's the one being bookmarked
    if (selectedArticle?.id === articleId) {
      setSelectedArticle(prev =>
        prev ? { ...prev, isBookmarked: !prev.isBookmarked } : null
      );
    }
  };

  const handleViewRelated = (articleId: string) => {
    const relatedArticle = articles.find(a => a.id === articleId);
    if (relatedArticle) {
      setSelectedArticle(relatedArticle);
      // Modal stays open, just updates the content
    }
  };

  return (
    <PageContainer>
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Knowledge', href: '/knowledge' }
        ]}
      />

      {/* Page Header */}
      <PageHeader
        title="Risk Taxonomy Framework"
        description="Browse artefacts across the 11 inventory components of the Risk Taxonomy Framework"
        actions={
          <div className="flex items-center gap-2 text-sm text-slate-400">
            {loading ? (
              <span className="text-slate-500">Loading...</span>
            ) : (
              <>
                <span className="font-semibold text-slate-300">
                  {filteredArticles.length}
                </span>
                <span>
                  {filteredArticles.length === 1 ? 'artefact' : 'artefacts'} available
                </span>
              </>
            )}
          </div>
        }
      />

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6">
        <CategoryFilter
          categories={categories}
          filter={filter}
          onFilterChange={handleFilterChange}
        />
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-slate-400">Loading knowledge documents...</p>
        </div>
      ) : (
        /* Articles Grid */
        <KnowledgeGrid
          articles={filteredArticles}
          onViewDetails={handleViewDetails}
          onToggleBookmark={handleToggleBookmark}
          emptyMessage={
            filter.search || filter.category || filter.showBookmarksOnly
              ? 'No artefacts match your current filters'
              : 'No artefacts available'
          }
        />
      )}

      {/* Article Details Modal */}
      <KnowledgeDetails
        article={selectedArticle}
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        onToggleBookmark={handleToggleBookmark}
        onViewRelated={handleViewRelated}
      />
    </PageContainer>
  );
}
