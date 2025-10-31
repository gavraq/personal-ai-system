---
name: stakeholder-analysis
description: Analyze stakeholders with power/interest matrix, influence mapping, and tailored engagement strategies
domain: change-agent
category: stakeholder-management
taxonomy: change-agent/stakeholder-management
parameters:
  - stakeholder_list
  - project_context
output_format: mixed
estimated_duration: 4-6 minutes
tags:
  - stakeholders
  - engagement
  - influence
  - communication
version: 1.0.0
author: Risk Agents Team
---

# Stakeholder Analysis Skill

## Purpose
Systematically analyze project stakeholders to understand their power, interest, influence, and optimal engagement strategies using industry-standard frameworks (Power/Interest Grid, Influence Mapping).

## When to Use This Skill
- At project initiation to identify all stakeholders
- When planning communication and engagement strategies
- When navigating organizational politics and influence
- When preparing for change management activities
- When stakeholder resistance or challenges emerge

## How It Works
This skill analyzes stakeholder information and produces:

1. **Power/Interest Matrix**: Classic 2x2 grid categorizing stakeholders
2. **Influence Map**: Network diagram showing relationships and influence paths
3. **Engagement Strategies**: Tailored approach for each stakeholder group
4. **Communication Plan**: Frequency, method, and messaging for each stakeholder
5. **Risk Assessment**: Identification of potential resistance or blockers

## Parameters

### Required Parameters
- **`stakeholder_list`** (array): List of stakeholders (strings or objects)
  - As strings: `["John Smith - CEO", "Sarah Johnson - PM", "Dev Team"]`
  - As objects with details (recommended)

### Optional Parameters
- **`project_context`** (object): Additional project context
  - `project_type` (string): Type of project (technical, organizational change, etc.)
  - `key_decisions` (array): Major decisions requiring stakeholder input
  - `known_concerns` (array): Known stakeholder concerns or resistance points

## Expected Output

Mixed format output with JSON data + Markdown visualization:

```json
{
  "status": "success",
  "stakeholder_analysis": {
    "total_stakeholders": 8,
    "by_category": {
      "manage_closely": 3,
      "keep_satisfied": 2,
      "keep_informed": 2,
      "monitor": 1
    },
    "by_sentiment": {
      "champion": 2,
      "supporter": 3,
      "neutral": 2,
      "skeptic": 1,
      "blocker": 0
    }
  },
  "stakeholders": [
    {
      "id": 1,
      "name": "John Smith",
      "role": "CEO / Executive Sponsor",
      "power": "high",
      "interest": "high",
      "category": "manage_closely",
      "influence_level": 10,
      "sentiment": "champion",
      "key_concerns": [
        "ROI and business value",
        "Timeline and budget adherence",
        "Strategic alignment"
      ],
      "engagement_strategy": "Weekly 1:1 updates, involve in key decisions, seek approval for major changes",
      "communication_frequency": "weekly",
      "communication_method": "1:1 meeting + exec summary email",
      "win_conditions": [
        "Demonstrate early wins and ROI",
        "Keep within budget and timeline",
        "Align with strategic objectives"
      ],
      "relationships": [2, 3, 5]
    }
  ],
  "power_interest_matrix": "```\nHIGH INTEREST\n┌─────────────────┬─────────────────┐\n│  KEEP INFORMED  │  MANAGE CLOSELY │\n│                 │                 │\n│  • Dev Team     │  • CEO (John)   │\n│  • QA Team      │  • PM (Sarah)   │\n│                 │  • Tech Lead    │\n├─────────────────┼─────────────────┤\n│    MONITOR      │ KEEP SATISFIED  │\n│                 │                 │\n│  • End Users    │  • CFO          │\n│                 │  • Legal        │\n└─────────────────┴─────────────────┘\n   LOW POWER         HIGH POWER\n```",
  "engagement_plan": {
    "manage_closely": {
      "stakeholders": ["CEO", "PM", "Tech Lead"],
      "approach": "Active partnership - involve in planning and decision-making",
      "communication": "Weekly updates minimum, ad-hoc as needed",
      "tactics": [
        "1:1 meetings to understand concerns and priorities",
        "Involve in key decisions before they're finalized",
        "Seek early input on changes to build buy-in",
        "Provide detailed status updates"
      ]
    },
    "keep_satisfied": {
      "stakeholders": ["CFO", "Legal"],
      "approach": "Keep happy but don't overwhelm - they have high power but moderate interest",
      "communication": "Bi-weekly summary updates",
      "tactics": [
        "Proactively address their specific concerns (budget, compliance)",
        "Provide concise executive summaries",
        "Escalate issues that impact their domains early",
        "Respect their time - concise, relevant communication only"
      ]
    },
    "keep_informed": {
      "stakeholders": ["Dev Team", "QA Team"],
      "approach": "Keep in the loop - high interest but lower organizational power",
      "communication": "Daily standups + weekly team updates",
      "tactics": [
        "Regular team communication and transparency",
        "Solicit input on technical decisions",
        "Recognize contributions publicly",
        "Provide context for strategic decisions affecting them"
      ]
    },
    "monitor": {
      "stakeholders": ["End Users"],
      "approach": "Monitor with minimal effort - low power and interest currently",
      "communication": "Launch announcement + user guides",
      "tactics": [
        "Passive communication (announcements, documentation)",
        "Respond to inquiries but don't proactively engage",
        "Gather feedback through surveys post-launch"
      ]
    }
  },
  "risk_assessment": [
    {
      "risk": "CFO may block budget if ROI not clear",
      "probability": "medium",
      "impact": "high",
      "mitigation": "Prepare detailed ROI analysis, schedule early CFO review, demonstrate quick wins"
    },
    {
      "risk": "Dev Team skepticism about feasibility",
      "probability": "medium",
      "impact": "medium",
      "mitigation": "Early technical involvement in planning, address concerns transparently, technical spike to prove approach"
    }
  ],
  "key_relationships": [
    {
      "from": "CEO",
      "to": "CFO",
      "relationship": "Direct report, high trust",
      "implication": "CFO support critical for CEO buy-in, leverage CFO as champion"
    },
    {
      "from": "PM",
      "to": "Tech Lead",
      "relationship": "Close collaboration, mutual respect",
      "implication": "Tech Lead can influence PM priorities, align them early"
    }
  ],
  "recommendations": [
    {
      "type": "engagement",
      "message": "Focus 60% of effort on 'Manage Closely' group - they have highest power and interest"
    },
    {
      "type": "communication",
      "message": "Create tiered communication plan: detailed for high interest, summaries for high power/lower interest"
    },
    {
      "type": "risk",
      "message": "Address CFO ROI concerns proactively in first 2 weeks to prevent budget blocks"
    },
    {
      "type": "influence",
      "message": "Leverage CEO→CFO relationship - secure CEO support first, then use to influence CFO"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T16:00:00Z",
    "skill_name": "stakeholder-analysis",
    "version": "1.0.0",
    "analysis_framework": "Power/Interest Grid + Influence Mapping"
  }
}
```

## Success Criteria
- All key stakeholders identified (minimum 5, typically 8-15)
- Each stakeholder categorized in Power/Interest matrix
- Specific, actionable engagement strategies for each category
- Communication plan tailored to stakeholder needs
- Relationships and influence paths mapped
- Risks and mitigation strategies identified

## Tips for Best Results

### Better Stakeholder Analysis
- Provide stakeholder roles/positions (helps assess power)
- Indicate known concerns or resistance (helps tailor strategies)
- Mention key relationships if known (CEO→CFO, etc.)
- Specify project type (technical vs organizational change affects stakeholder dynamics)

### Input Format Examples

**Simple List** (skill will analyze):
```json
{
  "stakeholder_list": [
    "John Smith - CEO",
    "Sarah Johnson - Project Manager",
    "Michael Chen - Tech Lead",
    "Finance Department",
    "Development Team"
  ]
}
```

**Detailed Objects** (recommended):
```json
{
  "stakeholder_list": [
    {
      "name": "John Smith",
      "role": "CEO",
      "known_concerns": ["ROI", "timeline"],
      "sentiment": "supportive"
    },
    {
      "name": "Finance Department",
      "role": "Budget Approvers",
      "known_concerns": ["cost overruns"],
      "sentiment": "neutral"
    }
  ],
  "project_context": {
    "project_type": "technical",
    "key_decisions": ["Technology platform choice", "Go-live date"]
  }
}
```

## Version History

- **1.0.0** (2025-10-26): Initial release
