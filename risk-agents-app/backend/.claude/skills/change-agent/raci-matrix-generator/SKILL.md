---
name: raci-matrix-generator
description: Create RACI (Responsible, Accountable, Consulted, Informed) matrices for clear role definition and accountability
domain: change-agent
category: project-management
taxonomy: change-agent/project-management
parameters:
  - activities
  - stakeholders
output_format: csv
estimated_duration: 3-5 minutes
tags:
  - raci
  - accountability
  - roles
  - governance
version: 1.0.0
author: Risk Agents Team
---

# RACI Matrix Generator Skill

## Purpose
Generate a clear RACI (Responsible, Accountable, Consulted, Informed) matrix that defines roles and responsibilities for project activities, eliminating confusion and ensuring accountability.

## When to Use This Skill
- At project kickoff to clarify roles and responsibilities
- When role confusion or accountability gaps exist
- When onboarding new team members or stakeholders
- When activities cross multiple teams or departments
- When governance structure needs documentation

## How It Works
This skill creates a RACI matrix by:

1. **Analyzing Activities**: Understanding what needs to be done
2. **Mapping Stakeholders**: Identifying who's involved
3. **Assigning RACI Roles**: Applying RACI logic to each activity-stakeholder combination
4. **Validation**: Ensuring each activity has exactly ONE Accountable person
5. **Recommendations**: Suggesting adjustments for balanced workload

**RACI Definitions**:
- **R (Responsible)**: Does the work to complete the activity (can be multiple)
- **A (Accountable)**: Ultimately answerable for completion (exactly ONE per activity)
- **C (Consulted)**: Provides input, two-way communication (subject matter experts)
- **I (Informed)**: Kept up-to-date, one-way communication (need to know)

## Parameters

### Required Parameters
- **`activities`** (array): List of activities/tasks/deliverables (strings)
- **`stakeholders`** (array): List of stakeholders/roles (strings)

### Optional Parameters
- **`activity_details`** (array of objects): Detailed activity information
  - `activity` (string): Activity name
  - `description` (string): What the activity involves
  - `suggested_responsible` (array): Suggested R roles
  - `suggested_accountable` (string): Suggested A role

## Expected Output

CSV format suitable for spreadsheet import, plus recommendations in JSON:

```csv
Activity,PM,Tech Lead,Design Lead,Dev Team,QA Team,Sponsor,Legal,Finance
Requirements Gathering,R,C,C,I,I,A,I,I
Design Mockups,C,C,R,I,I,A,I,I
Technical Architecture,C,A,I,R,C,I,I,I
Development,I,A,I,R,C,I,I,I
QA Testing,I,C,I,C,A/R,I,I,I
UAT,R,C,I,I,C,A,I,I
Legal Review,C,I,I,I,I,I,A/R,I
Budget Approval,C,I,I,I,I,C,I,A/R
Go-Live Decision,R,C,C,I,C,A,I,I
Post-Launch Support,R,A,I,R,R,I,I,I
```

**Plus JSON Metadata**:
```json
{
  "status": "success",
  "matrix_stats": {
    "total_activities": 10,
    "total_stakeholders": 8,
    "total_assignments": 45
  },
  "validation": {
    "all_activities_have_accountable": true,
    "no_multiple_accountables": true,
    "no_activities_without_responsible": true,
    "balanced_workload": false
  },
  "workload_analysis": [
    {
      "stakeholder": "PM",
      "responsible_count": 3,
      "accountable_count": 0,
      "total_involvement": 8,
      "workload_level": "high"
    },
    {
      "stakeholder": "Sponsor",
      "responsible_count": 0,
      "accountable_count": 5,
      "total_involvement": 7,
      "workload_level": "appropriate"
    }
  ],
  "recommendations": [
    {
      "type": "workload",
      "message": "PM has 8 total involvements - consider delegating some 'Responsible' activities"
    },
    {
      "type": "accountability",
      "message": "Sponsor is Accountable for 5 activities - ensure they have capacity for oversight"
    },
    {
      "type": "coverage",
      "message": "Dev Team only Consulted on QA Testing - consider making them Responsible for fixing bugs"
    },
    {
      "type": "validation",
      "message": "Legal Review has combined A/R - consider separating these roles for clearer accountability"
    }
  ],
  "raci_tips": {
    "responsible": "The doers - can be multiple people, these folks do the work",
    "accountable": "The owner - MUST be exactly one person who is ultimately answerable",
    "consulted": "The advisors - provide input before activity completion (two-way communication)",
    "informed": "The observers - kept updated after decisions (one-way communication)"
  },
  "metadata": {
    "generated_at": "2025-10-26T16:15:00Z",
    "skill_name": "raci-matrix-generator",
    "version": "1.0.0"
  }
}
```

## Success Criteria
- Every activity has exactly ONE Accountable person (no more, no less)
- Every activity has at least one Responsible person
- No stakeholder is overloaded (too many R or A assignments)
- Appropriate use of C (Consulted) for subject matter experts
- Appropriate use of I (Informed) for stakeholders who need awareness
- Matrix is clear, concise, and actionable

## Tips for Best Results

### Activity Granularity
- **Too Broad**: "Complete Project" (not actionable)
- **Too Narrow**: "Send email to John" (too detailed)
- **Just Right**: "Requirements Gathering", "Design Review", "Development Sprint 1"

### Stakeholder Roles
- Use roles (PM, Tech Lead) rather than names for reusability
- Include all key players even if involvement is minimal
- Don't include stakeholders with zero involvement in any activity

### Input Examples

**Simple Format**:
```json
{
  "activities": [
    "Requirements Gathering",
    "Design",
    "Development",
    "Testing",
    "Launch"
  ],
  "stakeholders": [
    "Project Manager",
    "Tech Lead",
    "Developer",
    "QA",
    "Sponsor"
  ]
}
```

**Detailed Format** (provides hints):
```json
{
  "activities": [
    "Requirements Gathering",
    "Design",
    "Development"
  ],
  "stakeholders": ["PM", "Tech Lead", "Dev Team", "Sponsor"],
  "activity_details": [
    {
      "activity": "Requirements Gathering",
      "description": "Gather and document requirements from stakeholders",
      "suggested_responsible": ["PM"],
      "suggested_accountable": "Sponsor"
    }
  ]
}
```

## Common RACI Patterns

**Project Management Activities**:
- PM: Usually R (responsible for doing)
- Sponsor: Usually A (accountable for approval)
- Team: Often C (consulted for input) or I (informed of decisions)

**Technical Activities**:
- Tech Lead: Usually A (accountable for technical decisions)
- Developers: Usually R (responsible for implementation)
- PM: Often C (consulted on timelines/scope)

**Approval/Sign-off Activities**:
- Decision maker: A (accountable for the decision)
- Preparer: R (responsible for preparing materials)
- Stakeholders: C (provide input) or I (notified of decision)

## RACI Rules
1. **Every activity must have exactly ONE A** (no shared accountability)
2. **Every activity should have at least one R** (someone must do the work)
3. **R and A can be the same person** (for small tasks) but shown as A/R
4. **Too many Rs dilutes responsibility** (3-5 maximum ideal)
5. **C means two-way** (they provide input, you incorporate it)
6. **I means one-way** (you tell them what happened)
7. **Empty cells are OK** (not everyone involved in everything)

## Version History

- **1.0.0** (2025-10-26): Initial release
