# Module 7 Step 7.2: Selected Policies for Migration

**Date**: October 27, 2025
**Status**: ✅ COMPLETE
**Purpose**: Select 5-8 representative policies for YAML frontmatter demonstration

---

## Selection Criteria

1. **Risk Domain Coverage**: Represent multiple risk domains
2. **Size Variety**: Mix of small (11-20K), medium (20-40K), and large (40K+) policies
3. **Complexity Range**: Simple single-domain to complex cross-domain policies
4. **Artefact Type Variety**: Primarily policies, but include 1 standards/framework document
5. **Cross-Reference Opportunities**: Policies that reference methodologies, models, data
6. **Skills Connection**: Policies we can connect to existing/future skills

---

## Selected Policies (7 Total)

### 1. Value-At-Risk Policy (Market Risk)
**File**: `Market_Risk/VaR/Value-At-Risk_Policy_FINAL.md`
**Size**: 35K
**Risk Domain**: Market Risk
**Artefact Type**: Policy

**Why Selected**:
- ✅ Core market risk policy - governance and technical
- ✅ References methodologies (VAR calculation methodology)
- ✅ References models (Historical Simulation VAR model)
- ✅ References data (market data fields)
- ✅ References feeds (Bloomberg market data)
- ✅ Can connect to existing `var-calculation` skill
- ✅ Good example of policy → methodology → model chain

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  methodologies:
    - var-methodology
    - historical-simulation-methodology
  models:
    - historical-var-model
  data:
    - market-data-dictionary
  feeds:
    - bloomberg-market-data
  governance:
    - market-risk-committee-tor
  controls:
    - var-limit-monitoring
    - var-backtesting
```

---

### 2. Market Risk Stress Testing Framework (Market Risk)
**File**: `Market_Risk/Stress/Market_Risk_Stress_Testing_Framework_FINAL.md`
**Size**: 13K (small)
**Risk Domain**: Market Risk
**Artefact Type**: Framework/Methodology

**Why Selected**:
- ✅ Different artefact type (Framework, not Policy)
- ✅ Small size - easy to work with
- ✅ Technical/methodology-focused
- ✅ References VAR policy (cross-reference opportunity)
- ✅ Can connect to `stress-testing` skill

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - var-policy
    - market-risk-policy
  methodologies:
    - stress-scenario-methodology
  models:
    - stress-var-model
  data:
    - stress-scenario-library
```

---

### 3. Model and Tool Risk Management Policy (Model Risk)
**File**: `Model_Risk/Model_Tool_Risk/Model_and_Tool_Risk_Management_Policy_FINAL.md`
**Size**: 42K (medium-large)
**Risk Domain**: Model Risk
**Artefact Type**: Policy

**Why Selected**:
- ✅ Cross-domain policy (affects Market, Credit, Operational risk)
- ✅ References governance (RMAC committee)
- ✅ References processes (model lifecycle)
- ✅ References Model Validation Policy (cross-reference)
- ✅ References Model Risk Standards (cross-reference)
- ✅ Example of governance-heavy policy

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - model-validation-policy
    - model-risk-standards
  governance:
    - risk-model-approval-committee-tor
  processes:
    - model-development-process
    - model-validation-process
  controls:
    - model-risk-appetite
    - model-inventory-control
```

---

### 4. Model Validation Policy (Model Risk)
**File**: `Model_Risk/Model_Validation_Policy_FINAL.md`
**Size**: 52K (large)
**Risk Domain**: Model Risk
**Artefact Type**: Policy

**Why Selected**:
- ✅ Large policy - tests handling of substantial content
- ✅ Process-heavy (model validation process)
- ✅ References Model Risk Management Policy (sibling policy)
- ✅ References controls (validation controls)
- ✅ Can connect to `model-validation` skill (future)

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - model-risk-management-policy
  processes:
    - model-validation-process
    - model-approval-process
  controls:
    - model-validation-control
    - model-documentation-control
  governance:
    - model-validation-committee-tor
```

---

### 5. Operational Risk Policy (Operational Risk)
**File**: `Operational_Risk/Operational_Risk_Policy_FINAL.md`
**Size**: 49K (large)
**Risk Domain**: Operational Risk
**Artefact Type**: Policy

**Why Selected**:
- ✅ Third risk domain represented
- ✅ Broad scope - governance + processes + controls
- ✅ References multiple processes (RCSA, incident management)
- ✅ References controls inventory
- ✅ References reports (operational risk reports)

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - operational-risk-incident-management-policy
    - operational-risk-scenario-analysis-policy
  processes:
    - rcsa-process
    - operational-risk-incident-process
  controls:
    - operational-risk-controls-inventory
  reports:
    - operational-risk-dashboard
  governance:
    - operational-risk-committee-tor
```

---

### 6. Credit Delegated Authority Policy (Credit Risk)
**File**: `Credit_Risk/Credit_Delegated_Authority/Credit_Delegated_Authority_Policy_FINAL.md`
**Size**: 62K (large)
**Risk Domain**: Credit Risk
**Artefact Type**: Policy

**Why Selected**:
- ✅ Fourth risk domain represented (Credit Risk)
- ✅ Governance-focused (approval authorities)
- ✅ References Credit Policy (parent policy)
- ✅ References org structure (authority levels)
- ✅ Example of governance/authorization policy

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - credit-policy
  governance:
    - credit-committee-tor
    - board-credit-committee-tor
  processes:
    - credit-approval-process
  org_charts:
    - credit-approval-authorities
```

---

### 7. New Product Approval Policy (Product Risk)
**File**: `Product_Risk/New_Product_Approval_Policy_FINAL.md`
**Size**: 37K (medium)
**Risk Domain**: Product Risk (cross-domain)
**Artefact Type**: Policy

**Why Selected**:
- ✅ Cross-domain policy (affects all risk types)
- ✅ Process-focused (approval workflow)
- ✅ References multiple risk policies
- ✅ References governance (Product Approval Committee)
- ✅ Example of business process policy
- ✅ Can connect to `product-approval` skill (future)

**Related Artefacts** (for YAML):
```yaml
related_artefacts:
  policies:
    - market-risk-policy
    - credit-policy
    - operational-risk-policy
  governance:
    - new-product-approval-committee-tor
  processes:
    - new-product-approval-process
  products:
    - approved-product-list
```

---

## Summary of Selection

### Risk Domain Coverage
| Risk Domain | Policies Selected | Coverage |
|-------------|-------------------|----------|
| **Market Risk** | 2 (VAR, Stress Testing) | ✅ |
| **Model Risk** | 2 (Management, Validation) | ✅ |
| **Operational Risk** | 1 (Policy) | ✅ |
| **Credit Risk** | 1 (Delegated Authority) | ✅ |
| **Product Risk** | 1 (New Product Approval) | ✅ |

### Size Distribution
| Size Range | Count | Examples |
|------------|-------|----------|
| **Small** (10-20K) | 1 | Stress Testing Framework (13K) |
| **Medium** (20-40K) | 2 | VAR Policy (35K), New Product Approval (37K) |
| **Large** (40K+) | 4 | Model Risk Management (42K), Operational Risk (49K), Model Validation (52K), Credit Delegated Authority (62K) |

### Artefact Type Variety
| Artefact Type | Count | Examples |
|---------------|-------|----------|
| **Policy** | 6 | VAR, Model Risk Management, Operational Risk, etc. |
| **Framework/Methodology** | 1 | Stress Testing Framework |

### Cross-Reference Opportunities
- **Policy → Policy**: Model Risk Management ↔ Model Validation
- **Policy → Methodology**: VAR Policy → VAR Methodology
- **Policy → Model**: VAR Policy → Historical VAR Model
- **Policy → Data**: VAR Policy → Market Data Dictionary
- **Policy → Feed**: VAR Policy → Bloomberg Feed
- **Policy → Governance**: All policies → Committee TORs
- **Policy → Process**: Operational Risk → RCSA Process
- **Policy → Control**: Operational Risk → Controls Inventory

### Skills Connection Opportunities
- `var-calculation` skill → VAR Policy
- `stress-testing` skill → Stress Testing Framework
- `model-validation` skill (future) → Model Validation Policy
- `product-approval` skill (future) → New Product Approval Policy

---

## Destination Directory Structure

After migration, the knowledge directory will look like:

```
backend/knowledge/
├── market-risk/
│   ├── policies/
│   │   ├── var-policy.md                         (NEW - 35K)
│   │   └── stress-testing-framework.md          (NEW - 13K)
│   └── methodologies/
│       └── (placeholders for future)
├── model-risk/
│   └── policies/
│       ├── model-risk-management-policy.md      (NEW - 42K)
│       └── model-validation-policy.md           (NEW - 52K)
├── operational-risk/
│   └── policies/
│       └── operational-risk-policy.md           (NEW - 49K)
├── credit-risk/
│   └── policies/
│       └── credit-delegated-authority-policy.md (NEW - 62K)
└── product-risk/
    └── policies/
        └── new-product-approval-policy.md       (NEW - 37K)
```

**Total**: 7 policies, 290K of content across 5 risk domains

---

## Next Step: 7.3 - Copy and Enhance

For each of the 7 selected policies:
1. Copy from source location
2. Add YAML frontmatter (artefact_type, related_artefacts, etc.)
3. Preserve original content unchanged
4. Save to knowledge directory

**Ready to proceed with Step 7.3?**
