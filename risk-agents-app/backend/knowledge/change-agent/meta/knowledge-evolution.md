# Knowledge Evolution Framework

## Purpose
Defines how knowledge documents evolve over time through controlled change management, inspired by the Risk Taxonomy Framework's check-out/check-in workflow.

---

## The Dual Context Pattern

Change Agent operates in **two contexts**, each with different knowledge management needs:

### Context 1: Change Agent Domain Knowledge
**Static Knowledge**: Standards and best practices for change management itself
- Meeting types taxonomy
- Action item standards
- Decision capture standards
- Project management methodologies

**Usage**: Referenced during Change Agent skill execution
**Ownership**: Change Agent domain experts
**Evolution**: Updated through internal Change Agent improvement process

### Context 2: Cross-Domain Knowledge Modification
**Dynamic Knowledge**: Tracking changes to other domain knowledge bases
- What artefacts are being updated
- Why changes are needed
- What's changing in each artefact
- Who approved the changes

**Usage**: Generated during skills that modify other domains
**Ownership**: Joint ownership (Change Agent + target domain)
**Evolution**: Updated through formal change projects

---

## Knowledge Evolution Workflow (Check-Out/Check-In)

### Phase 1: Check-Out
**Trigger**: Change project initiated that affects domain artefacts

**Actions**:
1. **Identify Affected Artefacts**: Which knowledge documents will change
2. **Create Change Context**: Document current state of artefacts
3. **Lock Version**: "Check out" current production version
4. **Record Baseline**: Store pre-change state for comparison

**Example**:
```markdown
## Change Project: Onboard New Product "FX Options"
**Domain Affected**: Market Risk
**Artefacts to Update**:
- market-risk/products/approved-products-list.md (add FX Options)
- market-risk/methodologies/risk-calculations.md (add FX Options methodology)
- market-risk/data/metrics-dictionary.md (add FX Options metrics)

**Checked Out**: 2025-10-23
**Change Owner**: Sarah Johnson
**Expected Check-In**: 2025-11-15
```

### Phase 2: Modify
**During**: Change project implementation

**Actions**:
1. **Update Draft Artefacts**: Make changes to checked-out versions
2. **Track Changes**: Document what changed and why
3. **Link to Change Context**: Connect updates to change project
4. **Review Cycles**: Domain experts review draft changes

**Change Tracking Format**:
```markdown
## Change Log: approved-products-list.md

**Change Date**: 2025-10-25
**Modified By**: Change Agent via meeting-minutes-capture skill
**Reason**: Decision made in Product Approval Committee (2025-10-25)

**Changes**:
- Added: FX Options to approved products list
- Updated: Last review date to 2025-10-25
- Added: Product risk characteristics (see decision-capture ref #DC-2025-1023)

**References**:
- Meeting Minutes: PAC-2025-10-25
- Decision Record: DC-2025-1023
- Change Project: PROJ-FX-OPTIONS-2025
```

### Phase 3: Validate
**Before Check-In**: Changes must be validated

**Validation Steps**:
1. **Completeness Check**: All required artefact updates made
2. **Consistency Check**: Changes align across related artefacts
3. **Quality Review**: Domain experts approve changes
4. **Testing**: Changes work in test environment
5. **Sign-Off**: Formal approval from change authority

**Validation Checklist**:
- [ ] All artefacts identified in check-out have been updated
- [ ] Cross-references between artefacts are consistent
- [ ] Changes align with decision records from meetings
- [ ] Domain expert has reviewed and approved
- [ ] Testing completed successfully
- [ ] Regulatory/compliance requirements met (if applicable)
- [ ] Change authority has signed off

### Phase 4: Check-In
**Final Step**: Updated artefacts become production

**Actions**:
1. **Version Update**: Increment version numbers
2. **Archive Old Version**: Store previous version for history
3. **Release to Production**: Updated knowledge becomes active
4. **Notify Stakeholders**: Inform affected teams
5. **Close Change Context**: Mark change project complete

**Check-In Record**:
```markdown
## Check-In: Market Risk Artefacts Update

**Project**: Onboard New Product "FX Options"
**Checked In**: 2025-11-15
**Approved By**: Market Risk Director

**Artefacts Updated** (3):
1. approved-products-list.md (v2.3 → v2.4)
2. risk-calculations.md (v1.8 → v1.9)
3. metrics-dictionary.md (v3.1 → v3.2)

**Impact Summary**:
- New product added to bank-wide list
- 5 new risk metrics defined
- 2 new calculation methodologies documented

**Stakeholders Notified**:
- Market Risk team
- Product team
- IT Systems team
- Compliance team
```

---

## Cross-Domain Knowledge Linking

Knowledge documents often reference artefacts in other domains. These links must be maintained.

### Link Types

#### 1. Reference Links
**Purpose**: Point to related knowledge in another domain
**Format**: `[[domain/category/document.md]]`

**Example**:
```markdown
## Action Items for Product Onboarding

When capturing action items for new product decisions, ensure:
- Product is added to [[market-risk/products/approved-products-list.md]]
- Risk methodologies updated in [[market-risk/methodologies/risk-calculations.md]]
- Data feeds configured as per [[market-risk/data/feed-specifications.md]]
```

#### 2. Update Links
**Purpose**: Track when this document triggers updates to other domains
**Format**: Change log with cross-domain references

**Example**:
```markdown
## Cross-Domain Updates Triggered

**Meeting**: Product Approval Committee (2025-10-25)
**Decision**: Approved FX Options product

**Downstream Updates Required**:
- [ ] Market Risk: Add product (Owner: Sarah, Due: 2025-11-01)
- [ ] Credit Risk: Define counterparty limits (Owner: John, Due: 2025-11-05)
- [ ] Operations: Configure systems (Owner: Mike, Due: 2025-11-10)
- [ ] Compliance: Update regulatory reporting (Owner: Lisa, Due: 2025-11-15)
```

#### 3. Dependency Links
**Purpose**: Identify when this document depends on other domain knowledge
**Format**: Prerequisites section

**Example**:
```markdown
## Prerequisites

This meeting minutes template assumes:
- [[risk-management/governance/decision-authority.md]] defines who can approve
- [[risk-management/policies/documentation-standards.md]] defines retention rules
- [[product-management/products/product-categories.md]] defines valid products
```

### Link Maintenance

**When to Update Links**:
- Domain structure changes (categories renamed/moved)
- Referenced documents are deprecated
- New dependencies are identified
- Cross-domain processes change

**Broken Link Detection**:
- Automated checks scan for broken `[[...]]` references
- Weekly reports identify links to non-existent documents
- Change projects must update dependent links

---

## Knowledge Versioning

### Version Numbering Scheme

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Fundamental restructure (e.g., 1.0 → 2.0)
- **MINOR**: Content additions or significant updates (e.g., 1.3 → 1.4)
- **PATCH**: Minor corrections or clarifications (e.g., 1.3.2 → 1.3.3)

**Version Tracking**:
```markdown
---
document: action-items-standards.md
version: 2.4.1
last_updated: 2025-10-23
updated_by: Change Agent Team
previous_version: 2.4.0
---

## Version History

### v2.4.1 (2025-10-23)
- PATCH: Clarified priority level definitions
- Fixed: Typo in P2 description

### v2.4.0 (2025-09-15)
- MINOR: Added priority levels (P0-P3)
- MINOR: Added common action item patterns section

### v2.3.0 (2025-08-01)
- MINOR: Enhanced quality checklist
- MINOR: Added more examples
```

### Version Control Integration

**Git-Based Versioning**:
- Each knowledge document is version controlled
- Commit messages reference change projects
- Tags mark production releases
- Branches support draft changes during check-out

**Change Tracking**:
```bash
# Check out artefact for change project
git checkout -b change/proj-fx-options-2025

# Make updates to knowledge documents
git commit -m "Add FX Options to approved products [PROJ-FX-OPTIONS-2025]"

# After validation and sign-off
git checkout main
git merge change/proj-fx-options-2025
git tag v2.4.0 -m "FX Options product onboarding complete"
```

---

## Knowledge Ownership

### Federated Ownership Model

**Central Framework**: Risk Agents application defines:
- Knowledge directory structure
- Version control standards
- Cross-domain linking format
- Check-out/check-in workflow

**Distributed Maintenance**: Domain teams own:
- Content of their domain knowledge
- Quality and accuracy of artefacts
- Review and approval of changes
- Expertise for their domain area

### Ownership Matrix

| Domain | Category | Knowledge Document | Owner | Review Frequency |
|--------|----------|-------------------|-------|------------------|
| Change Agent | meeting-management | meeting-types.md | Change Agent Team | Quarterly |
| Change Agent | meeting-management | action-items-standards.md | Change Agent Team | Quarterly |
| Change Agent | meeting-management | decision-capture.md | Change Agent Team | Quarterly |
| Market Risk | products | approved-products-list.md | Market Risk Team | Monthly |
| Market Risk | methodologies | risk-calculations.md | Market Risk Analytics | Annually |
| Credit Risk | policies | credit-approval-limits.md | Credit Risk Team | Annually |

### Review Cycles

**Regular Reviews**:
- **Quarterly**: High-frequency domains (Change Agent, Products)
- **Annually**: Stable domains (Policies, Methodologies)
- **Ad-Hoc**: Triggered by regulatory changes or major incidents

**Review Process**:
1. Schedule review meeting with domain experts
2. Review current document for accuracy
3. Identify gaps or outdated content
4. Propose updates (if needed)
5. Follow check-out/check-in workflow for changes
6. Update "last reviewed" date even if no changes

---

## Architecture for Context 2 (Future Enhancement)

### Current State (MVP - Context 1)
✅ Static knowledge for Change Agent domain
✅ Basic cross-domain reference links
✅ Manual version tracking

### Future State (Context 2)
⏳ Automated check-out/check-in workflow
⏳ Cross-domain change impact analysis
⏳ Real-time link validation
⏳ Change project integration
⏳ Automated stakeholder notification

### Technical Requirements for Context 2

**1. Change Context Manager**
```python
class ChangeContextManager:
    def check_out(self, artefacts: List[str], project_id: str) -> ChangeContext
    def track_modification(self, artefact: str, changes: Dict) -> None
    def validate_changes(self, context_id: str) -> ValidationReport
    def check_in(self, context_id: str, approval: Approval) -> CheckInResult
```

**2. Cross-Domain Link Validator**
```python
class LinkValidator:
    def scan_links(self, knowledge_dir: Path) -> List[Link]
    def validate_links(self, links: List[Link]) -> List[BrokenLink]
    def update_link(self, old_path: str, new_path: str) -> UpdateResult
```

**3. Knowledge Version Control**
```python
class KnowledgeVersionControl:
    def create_version(self, document: str, changes: str) -> Version
    def get_history(self, document: str) -> List[Version]
    def rollback(self, document: str, version: str) -> RollbackResult
```

---

## Best Practices

### For Domain Teams

1. **Keep Knowledge Current**: Regular reviews prevent staleness
2. **Document Changes**: Always explain why artefact was updated
3. **Cross-Reference**: Link related knowledge across domains
4. **Validate Links**: Check references when updating documents
5. **Version Consistently**: Follow semantic versioning scheme

### For Change Projects

1. **Identify Artefacts Early**: List all affected knowledge documents upfront
2. **Check Out Formally**: Create change context record
3. **Track All Changes**: Document every artefact modification
4. **Validate Thoroughly**: Complete all validation steps
5. **Check In Cleanly**: Ensure all updates are complete before check-in

### For Skills Development

1. **Reference, Don't Duplicate**: Link to authoritative knowledge, don't copy
2. **Respect Ownership**: Don't modify other domain knowledge directly
3. **Generate Change Records**: When skills trigger changes, document them
4. **Validate Cross-Domain**: Check that referenced knowledge still exists

---

## Monitoring and Metrics

### Knowledge Health Metrics

**Completeness**:
- % of domains with complete artefact coverage
- Number of empty/stub documents

**Consistency**:
- Number of broken cross-domain links
- Number of version conflicts

**Currency**:
- Average time since last review
- Number of documents overdue for review

**Usage**:
- Most frequently referenced documents
- Skills that reference each knowledge document

### Change Velocity Metrics

**Active Changes**:
- Number of checked-out change contexts
- Average duration from check-out to check-in
- Number of change projects per domain

**Change Impact**:
- Average number of artefacts per change
- Most frequently updated documents
- Cross-domain change frequency

---

## Summary

The Knowledge Evolution Framework ensures:
- **Controlled Change**: Check-out/check-in workflow manages knowledge updates
- **Dual Context Support**: Handles both static domain knowledge and dynamic cross-domain changes
- **Federated Ownership**: Central standards, distributed maintenance
- **Cross-Domain Linking**: Knowledge documents reference each other reliably
- **Version Control**: All changes tracked with full history
- **Quality Assurance**: Validation required before knowledge goes to production

This framework provides the foundation for **Context 2** (Change Agent as change modifier), enabling Risk Agents to not just manage its own domain, but also facilitate controlled evolution of knowledge across all domains.

---

**Version**: 1.0.0
**Created**: 2025-10-23
**Owner**: Change Agent Team
**Review Frequency**: Quarterly
