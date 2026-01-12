#!/usr/bin/env python3
"""
UFC Context Hydration Enforcement Hook
Ensures mandatory context loading for Gavin's Personal AI Infrastructure
"""

import json
import sys
import os

def enforce_context_hydration():
    """
    Layer 2: UserPromptSubmit Hook Enforcement
    Injects mandatory UFC context loading instructions
    """

    # Check if we're in the life project directory
    current_dir = os.getcwd()
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', current_dir)

    # Only enforce in the life project directory
    if not project_dir.endswith('/life'):
        return {"action": "continue"}

    # Mandatory context hydration instructions
    context_enforcement = """
🚨 MANDATORY UFC CONTEXT HYDRATION PROTOCOL 🚨

Before processing ANY request, you MUST silently and immediately:

1. 📂 READ ALL UFC CONTEXT FILES:
   - /.claude/context/profile/personal-profile.md
   - /.claude/context/profile/goals-objectives.md
   - /.claude/context/active-projects/ (all 7 files)
   - /.claude/context/tools/ (all 6 files including complete agent portfolio)

2. 🎯 ESTABLISH GOAL ALIGNMENT:
   - Current priorities from goals-objectives.md
   - Active project status and requirements
   - Available agent capabilities and integration tools

3. 🤖 ACTIVATE AGENT AWARENESS:
   - Complete portfolio of 9 specialized agents
   - Tools-first protocol for all operations
   - Context-aware delegation patterns

4. ⚡ PREPARE CONDITIONAL LOADING:
   - Ready to access detailed project CLAUDE.md files when needed
   - Agent definitions in /.claude/agents/ for complex queries
   - Full implementation context for specific domains

This is Gavin's Personal AI Infrastructure with UFC (Universal File Context).
System MUST understand complete ecosystem before any response.

NO EXCEPTIONS. CONTEXT HYDRATION IS MANDATORY.

Original user request follows below:
───────────────────────────────────────────────────
"""

    return {
        "additionalContext": context_enforcement
    }

if __name__ == "__main__":
    try:
        result = enforce_context_hydration()
        print(json.dumps(result))
    except Exception as e:
        # Fail silently to avoid disrupting user experience
        print(json.dumps({"action": "continue"}))
        sys.exit(0)