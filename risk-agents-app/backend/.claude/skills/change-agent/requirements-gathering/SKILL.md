---
name: requirements-gathering
description: Extract and structure requirements from unstructured text with IDs, priorities, acceptance criteria, and traceability
domain: change-agent
category: requirements-management
taxonomy: change-agent/requirements-management
parameters:
  - requirements_text
  - requirement_type
output_format: json
estimated_duration: 5-7 minutes
tags:
  - requirements
  - user-stories
  - acceptance-criteria
  - traceability
version: 1.0.0
author: Risk Agents Team
---

# Requirements Gathering Skill

## Purpose
Extract, structure, and organize requirements from unstructured text (meeting notes, emails, documents) into well-formed requirements with IDs, priorities, acceptance criteria, and traceability.

## When to Use This Skill
- After requirements elicitation sessions or workshops
- When analyzing stakeholder emails or meeting notes for requirements
- To structure informal requirements into formal specifications
- When creating user stories from feature requests
- For requirements traceability and impact analysis

## How It Works
This skill analyzes unstructured text and produces:

1. **Requirements Extraction**: Identifies individual requirements from text
2. **Classification**: Categorizes as functional, non-functional, constraint, or assumption
3. **Structuring**: Formats as user stories (As a... I want... So that...)
4. **Prioritization**: Assigns MoSCoW priority (Must, Should, Could, Won't)
5. **Acceptance Criteria**: Defines testable acceptance criteria (Given-When-Then)
6. **Traceability**: Links requirements to business objectives and dependencies

## Parameters

### Required Parameters
- **`requirements_text`** (string): Unstructured text containing requirements

### Recommended Parameters
- **`requirement_type`** (string): Type filter (functional, non-functional, both)
  - Default: "both"
  - Options: "functional", "non-functional", "both"

### Optional Parameters
- **`project_context`** (object): Additional context
  - `business_objectives` (array): High-level business goals
  - `existing_requirements` (array): Already defined requirements (for dependency linking)
  - `priority_guidance` (string): Prioritization criteria or constraints

## Expected Output

JSON format with structured requirements:

```json
{
  "status": "success",
  "summary": {
    "total_requirements": 15,
    "functional": 10,
    "non_functional": 4,
    "constraints": 1,
    "by_priority": {
      "must_have": 6,
      "should_have": 5,
      "could_have": 3,
      "wont_have": 1
    }
  },
  "requirements": [
    {
      "id": "REQ-001",
      "type": "functional",
      "category": "user-authentication",
      "priority": "must_have",
      "user_story": {
        "as_a": "registered user",
        "i_want": "to log in with my email and password",
        "so_that": "I can access my personalized dashboard and saved preferences"
      },
      "description": "Users must be able to authenticate using email/password credentials to access protected features",
      "acceptance_criteria": [
        {
          "id": "AC-001-1",
          "scenario": "Successful login with valid credentials",
          "given": "User has a valid account with email 'user@example.com' and password 'SecurePass123'",
          "when": "User enters correct email and password and clicks Login",
          "then": "User is redirected to dashboard, session token is created, welcome message displays"
        },
        {
          "id": "AC-001-2",
          "scenario": "Failed login with invalid credentials",
          "given": "User enters incorrect password",
          "when": "User clicks Login",
          "then": "Error message 'Invalid credentials' displays, user remains on login page, failed attempt is logged"
        },
        {
          "id": "AC-001-3",
          "scenario": "Account lockout after failed attempts",
          "given": "User has failed 5 login attempts",
          "when": "User attempts 6th login",
          "then": "Account is locked for 30 minutes, email notification sent to user, support contact info displayed"
        }
      ],
      "business_value": "Enable personalized user experience and protect user data with secure authentication",
      "dependencies": ["REQ-015"],
      "linked_to": {
        "business_objective": "OBJ-002: Improve user retention through personalization",
        "epic": "EPIC-001: User Account Management"
      },
      "estimated_effort": "5 story points",
      "technical_notes": "Use JWT for session management, bcrypt for password hashing, implement rate limiting",
      "risks": [
        "Security vulnerability if implementation flawed",
        "Performance impact of bcrypt hashing at scale"
      ],
      "validation_method": "Automated testing + penetration testing",
      "source": "Stakeholder workshop Oct 15, 2025 - User Experience Team"
    },
    {
      "id": "REQ-002",
      "type": "non_functional",
      "category": "performance",
      "priority": "must_have",
      "user_story": {
        "as_a": "any user",
        "i_want": "pages to load in under 2 seconds",
        "so_that": "I have a smooth, responsive experience"
      },
      "description": "All web pages must load and become interactive within 2 seconds on standard broadband connection (10 Mbps)",
      "acceptance_criteria": [
        {
          "id": "AC-002-1",
          "scenario": "Homepage load time",
          "given": "User is on standard broadband (10 Mbps), cache is clear",
          "when": "User navigates to homepage",
          "then": "Page is fully loaded and interactive within 2 seconds (measured by Lighthouse)"
        },
        {
          "id": "AC-002-2",
          "scenario": "Dashboard load time with data",
          "given": "User has 100 saved items, cache is clear",
          "when": "User navigates to dashboard after login",
          "then": "Dashboard displays within 2 seconds with all data rendered"
        }
      ],
      "business_value": "Reduce bounce rate and improve user satisfaction (target: 4.5/5 satisfaction score)",
      "dependencies": [],
      "linked_to": {
        "business_objective": "OBJ-003: Deliver best-in-class user experience",
        "quality_attribute": "Performance"
      },
      "estimated_effort": "8 story points",
      "technical_notes": "Implement code splitting, lazy loading, CDN for static assets, database query optimization",
      "measurement": "Lighthouse performance score > 90, Core Web Vitals: LCP < 2s, FID < 100ms, CLS < 0.1",
      "validation_method": "Automated performance testing in CI/CD pipeline",
      "source": "Performance requirements workshop Oct 18, 2025"
    }
  ],
  "requirements_matrix": {
    "traceability": [
      {
        "requirement_id": "REQ-001",
        "traces_to": {
          "business_objective": "OBJ-002",
          "epic": "EPIC-001",
          "dependencies": ["REQ-015"],
          "test_cases": ["TC-001", "TC-002", "TC-003"]
        }
      }
    ]
  },
  "moscow_analysis": {
    "must_have": {
      "count": 6,
      "description": "Critical for MVP launch, non-negotiable",
      "requirements": ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-015"]
    },
    "should_have": {
      "count": 5,
      "description": "Important but can be deferred if timeline at risk",
      "requirements": ["REQ-006", "REQ-007", "REQ-008", "REQ-009", "REQ-010"]
    },
    "could_have": {
      "count": 3,
      "description": "Nice to have, low priority",
      "requirements": ["REQ-011", "REQ-012", "REQ-013"]
    },
    "wont_have": {
      "count": 1,
      "description": "Out of scope for current release",
      "requirements": ["REQ-014"],
      "rationale": "Complexity too high, limited business value for v1.0"
    }
  },
  "dependency_graph": {
    "REQ-001": ["REQ-015"],
    "REQ-003": ["REQ-001", "REQ-002"]
  },
  "quality_metrics": {
    "completeness_score": 92,
    "clarity_score": 88,
    "testability_score": 95,
    "traceability_score": 90,
    "overall_quality": "excellent"
  },
  "recommendations": [
    {
      "type": "priority",
      "message": "6 Must-Have requirements form critical path - ensure these are delivered first"
    },
    {
      "type": "dependency",
      "message": "REQ-015 blocks 2 other requirements - prioritize implementation"
    },
    {
      "type": "risk",
      "message": "REQ-002 (performance) has high technical complexity - start early spike"
    },
    {
      "type": "clarity",
      "message": "REQ-011 needs clearer acceptance criteria - schedule refinement session"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T17:00:00Z",
    "skill_name": "requirements-gathering",
    "version": "1.0.0",
    "source_document": "Requirements Workshop Notes - Oct 15-18, 2025",
    "analyst": "Product Team",
    "frameworks_used": ["User Stories", "MoSCoW", "Given-When-Then", "Gherkin"]
  }
}
```

## Success Criteria
- All requirements extracted from source text
- Each requirement has unique ID
- Functional requirements formatted as user stories (As a... I want... So that...)
- Acceptance criteria use Given-When-Then format (testable)
- MoSCoW priorities assigned with justification
- Dependencies identified
- Traceability to business objectives established
- Quality score > 80% (completeness, clarity, testability)

## Tips for Best Results

### Input Text Quality
Better quality input → better structured output

**Good Input** (specific, detailed):
```
"Users told us they want to log in faster. Currently takes 3-4 clicks and a password reset every month. They want social login (Google, Microsoft) and remember me option. Must work on mobile. Performance requirement: login should complete in under 1 second."
```

**Poor Input** (vague):
```
"Users need to log in"
```

### Requirement Types

**Functional Requirements**:
- What the system must DO
- Features and capabilities
- User interactions
- Business rules

**Non-Functional Requirements**:
- How the system must BE
- Performance, security, usability
- Quality attributes
- Constraints

### MoSCoW Priority Guidelines
- **Must Have**: Without this, solution doesn't work or has no value
- **Should Have**: Important but solution still works without it
- **Could Have**: Desirable but not important
- **Won't Have**: Out of scope for this release

## Version History

- **1.0.0** (2025-10-26): Initial release
