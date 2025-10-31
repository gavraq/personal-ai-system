# Real-World Usage & Testing Guide

**Purpose**: Use the Risk Agents app for actual work and document findings
**Duration**: 1-2 weeks of regular usage
**Goal**: Validate MVP, identify issues, prioritize improvements

---

## Testing Approach

### Phase 1: Exploration (Day 1)
**Goal**: Familiarize yourself with all features

### Phase 2: Real Tasks (Days 2-7)
**Goal**: Use for actual work scenarios

### Phase 3: Documentation (Days 8-14)
**Goal**: Document findings and plan improvements

---

## Quick Start: Using the App

### 1. Start the Application

```bash
cd /Users/gavinslater/projects/life/risk-agents-app
docker-compose up
```

**Access**:
- Frontend: http://localhost:3050
- Backend API: http://localhost:8050
- API Docs: http://localhost:8050/docs

---

## Feature Testing Checklist

### Dashboard (http://localhost:3050/dashboard)

**What to Test**:
- [ ] Dashboard loads without errors
- [ ] Metrics display correctly (skills used, queries made)
- [ ] Recent activity shows your queries
- [ ] Quick actions are clickable
- [ ] Refresh updates data

**Real-World Use**:
- Check daily to see your usage patterns
- Use quick actions for frequent tasks

**Issues to Note**:
- Slow loading?
- Missing metrics?
- Confusing layout?
- Feature requests?

---

### Chat Interface (http://localhost:3050/chat)

**What to Test**:
- [ ] Chat interface loads
- [ ] Can send messages
- [ ] AI responses stream correctly
- [ ] Message history persists during session
- [ ] Can clear conversation
- [ ] Copy responses works

**Real-World Use Cases**:

**Scenario 1: General Questions**
```
Ask: "What skills are available for meeting management?"
Expected: List of meeting-related skills
```

**Scenario 2: Skill Execution Request**
```
Ask: "Generate a project charter for a new risk reporting system"
Expected: Structured project charter with all sections
```

**Scenario 3: Knowledge Query**
```
Ask: "Explain the VAR Policy approval process"
Expected: Information from VAR Policy with metadata
```

**Scenario 4: Complex Task**
```
Ask: "Create meeting minutes from my last standup meeting"
Expected: Structured minutes with action items
```

**Issues to Note**:
- Response accuracy?
- Response speed?
- Formatting issues?
- Context understanding?
- Missing capabilities?

---

### Skills Browser (http://localhost:3050/skills)

**What to Test**:
- [ ] All skills display in grid
- [ ] Domain filter works (change-agent)
- [ ] Search functionality works
- [ ] Can click skill for details
- [ ] Skill details modal shows all information
- [ ] Can execute skill from modal
- [ ] Parameter inputs work correctly

**Real-World Use Cases**:

**Task 1: Browse Available Skills**
1. Open Skills Browser
2. Filter by "change-agent" domain
3. Review all 15 skills
4. Note which ones you'd actually use

**Task 2: Execute a Skill Directly**
1. Click "Project Charter Generator"
2. Fill in parameters:
   - Project name
   - Objectives
   - Stakeholders
3. Click "Execute"
4. Review generated charter

**Task 3: Find Specific Skill**
1. Use search: "meeting"
2. Verify relevant skills appear
3. Try executing one

**Issues to Note**:
- Skills you'd actually use?
- Skills missing that you need?
- Parameter inputs intuitive?
- Output format useful?
- Execution speed?

---

### Knowledge Browser (http://localhost:3050/knowledge)

**What to Test**:
- [ ] Documents load from API
- [ ] Can browse by category
- [ ] Search works
- [ ] Document cards show summary
- [ ] Click document opens modal
- [ ] Document metadata displays (for policies)
- [ ] Plain markdown documents work (change-agent docs)
- [ ] Related artefacts show
- [ ] Related skills show
- [ ] Content readable and formatted

**Real-World Use Cases**:

**Task 1: Find Policy Information**
1. Open Knowledge Browser
2. Look for "Value-At-Risk Policy"
3. Click to open
4. Review metadata section:
   - Artefact type badge
   - Risk domain
   - Difficulty level
   - Owner information
   - Related artefacts (8 types)
   - Related skills (3 skills)
5. Read policy content
6. Check if frontmatter is stripped correctly

**Task 2: Browse Change Agent Knowledge**
1. Filter by "change-agent" domain
2. Open "Meeting Types" document
3. Verify plain markdown displays correctly
4. Note if content is useful

**Task 3: Cross-Reference Navigation**
1. Open VAR Policy
2. Look at related artefacts
3. Note which ones you'd want to click to navigate
4. Check if related skills make sense

**Issues to Note**:
- Content useful?
- Metadata accurate?
- Navigation intuitive?
- Missing cross-references?
- Layout issues?
- Performance with large documents?

---

## Real-World Task Scenarios

### Scenario 1: Project Kickoff

**Objective**: Use Risk Agents to plan a new project

**Steps**:
1. **Chat**: "I need to start a new project for migrating our risk reporting system to a new platform"
2. **Skills**: Execute "Project Charter Generator"
   - Input: Project details
   - Review: Generated charter
3. **Skills**: Execute "Stakeholder Analysis"
   - Input: Key stakeholders
   - Review: Analysis and recommendations
4. **Skills**: Execute "RACI Matrix Generator"
   - Input: Activities and roles
   - Review: RACI matrix
5. **Knowledge**: Read "Project Management Methodologies"

**Document**:
- Quality of outputs
- Time saved vs manual creation
- Accuracy of recommendations
- Missing features

---

### Scenario 2: Meeting Management

**Objective**: Manage a project meeting from start to finish

**Steps**:
1. **Before Meeting**:
   - Skills: "Meeting Types" - Review meeting types
   - Knowledge: Read "Effective Meetings" guide

2. **During Meeting**:
   - Take notes manually
   - Identify action items

3. **After Meeting**:
   - Skills: Execute "Meeting Minutes Capture"
     - Input: Your notes
     - Review: Structured minutes
   - Skills: Execute "Action Item Tracking"
     - Input: Identified actions
     - Review: Action item list with owners/dates
   - Skills: Execute "Follow-up Generator"
     - Review: Follow-up email template

**Document**:
- Usefulness for actual meetings
- Time saved
- Output quality
- Missing features

---

### Scenario 3: Requirements Gathering

**Objective**: Capture and validate requirements for a new feature

**Steps**:
1. **Chat**: "I need to gather requirements for a new risk dashboard"
2. **Skills**: Execute "Business Requirements Capture"
   - Input: Stakeholder needs
   - Review: Structured requirements
3. **Skills**: Execute "Requirement Validation"
   - Input: Captured requirements
   - Review: Validation checklist
4. **Skills**: Execute "Use Case Generator"
   - Input: Key scenarios
   - Review: Use case documentation

**Document**:
- Completeness of output
- Practical usability
- Missing requirement types

---

### Scenario 4: Risk Documentation

**Objective**: Work with existing risk policies

**Steps**:
1. **Knowledge**: Browse Market Risk policies
2. **Knowledge**: Read VAR Policy
   - Note metadata usefulness
   - Check related artefacts
   - Verify cross-references
3. **Knowledge**: Read Stress Testing Framework
   - Compare metadata display
   - Check different artefact type rendering
4. **Chat**: "Explain the difference between VAR and Stress VAR"
5. **Chat**: "What methodologies are used in VAR calculation?"

**Document**:
- Knowledge base usefulness
- Metadata value
- Cross-reference utility
- AI understanding of policies

---

## Daily Usage Patterns

### Week 1: Light Usage
- **Day 1**: Exploration - Try all features once
- **Day 2-3**: Use for 1-2 actual tasks
- **Day 4-5**: Identify most useful features
- **Day 6-7**: Document initial findings

### Week 2: Regular Usage
- **Daily**: Use for at least one real task
- **Track**: Which features you use most
- **Note**: What's missing or broken
- **Record**: Time saved vs manual work

---

## Issues & Feedback Tracking

### Create Issues Log

**File**: `/Users/gavinslater/projects/life/risk-agents-app/docs/usage-feedback.md`

**Template**:
```markdown
# Usage Feedback Log

## Week 1

### Day 1 - [Date]
**Tasks Attempted**:
- Task description

**What Worked**:
- Feature X worked well
- Output quality good

**Issues Found**:
- [ ] Bug: Description (Severity: High/Medium/Low)
- [ ] Missing: Feature request
- [ ] Improvement: Enhancement idea

**Time Saved**: Estimated X minutes

---

### Day 2 - [Date]
...
```

---

## Key Questions to Answer

### Usage Patterns
1. Which features do you use most?
2. Which features do you never use?
3. What's your typical workflow?
4. How often do you use it daily?

### Value Assessment
1. Does it save time?
2. Is output quality sufficient?
3. Would you recommend it to others?
4. What's the killer feature?

### Pain Points
1. What's frustrating?
2. What's missing?
3. What's broken?
4. What's confusing?

### Prioritization
1. What must be fixed? (Blockers)
2. What should be improved? (High value)
3. What would be nice? (Low priority)
4. What can be removed? (Not useful)

---

## Metrics to Track

### Quantitative
- [ ] Number of queries per day
- [ ] Skills executed per day
- [ ] Documents viewed per day
- [ ] Average response time
- [ ] Errors encountered
- [ ] Time saved (estimated)

### Qualitative
- [ ] Output quality (1-10 scale)
- [ ] Ease of use (1-10 scale)
- [ ] Usefulness (1-10 scale)
- [ ] Would recommend? (Yes/No)

---

## After Testing Period

### Analysis Tasks
1. **Review feedback log** - Compile all issues
2. **Categorize issues** - Bugs vs features vs improvements
3. **Prioritize fixes** - Critical → High → Medium → Low
4. **Estimate effort** - Hours per fix/feature
5. **Create action plan** - Next 2-4 weeks of work

### Decision Points
- [ ] Ready for deployment? (If yes → Module 10)
- [ ] Need critical fixes? (If yes → Fix first)
- [ ] Need new features? (If yes → Prioritize)
- [ ] Need Module 8 (Context)? (Based on usage)

---

## Success Criteria

**MVP is successful if**:
✅ You use it at least 3x per week
✅ It saves time vs manual work
✅ Output quality is acceptable
✅ No critical bugs blocking usage
✅ You would recommend to colleagues

**Ready for deployment if**:
✅ All critical bugs fixed
✅ Core workflows work smoothly
✅ Performance acceptable
✅ Error handling robust
✅ Documentation complete

---

## Quick Reference: Common Tasks

### Start/Stop Application
```bash
# Start
cd /Users/gavinslater/projects/life/risk-agents-app
docker-compose up

# Stop
docker-compose down

# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Health
```bash
# Backend health
curl http://localhost:8050/health

# Frontend accessible
curl -I http://localhost:3050
```

### Debug Issues
```bash
# Backend logs
docker-compose logs backend | tail -50

# Frontend logs
docker-compose logs frontend | tail -50

# Exec into backend
docker-compose exec backend bash

# Check Python environment
docker-compose exec backend uv pip list
```

---

## Support Resources

### Documentation
- Implementation Plan: `/risk-agents-app-implementation-plan.md`
- Module 1-7 Docs: `/docs/module-*.md`
- API Documentation: http://localhost:8050/docs

### Key Files
- Backend Skills: `/backend/.claude/skills/change-agent/`
- Knowledge Docs: `/backend/knowledge/`
- Frontend Components: `/frontend/components/`

---

## Contact & Feedback

**During Testing**:
- Keep notes in `usage-feedback.md`
- Screenshot issues
- Note timestamps for errors

**After Testing**:
- Compile feedback
- Prioritize issues
- Discuss next steps

---

**Start Date**: _____________
**End Date**: _____________
**Status**: In Progress

**Goal**: Determine if MVP is ready for deployment or needs improvements
