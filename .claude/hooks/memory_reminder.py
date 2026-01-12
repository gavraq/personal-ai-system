#!/usr/bin/env python3
"""
Memory reminder hook - reminds the agent to update context files after completing tasks.
Triggers on Stop event to inject a reminder before the response is finalized.
"""

import json
import sys
from pathlib import Path


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Get session info for context
        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path', '')

        # Count conversation turns to determine if this was a substantial session
        turn_id = "0"
        try:
            if transcript_path and Path(transcript_path).exists():
                with open(transcript_path, "r", encoding="utf-8") as f:
                    lines = [line for line in f if line.strip()]
                    turn_id = str(len(lines))
        except Exception:
            pass

        reminder = """<system-reminder>
**CONTEXT MAINTENANCE - FINAL STEP BEFORE COMPLETING**:

You are solely responsible for maintaining the context system. Before this session ends, assess whether any `.claude/context/` files should be updated:

1. **Profile Updates** (`.claude/context/profile/`):
   - New preferences or work patterns learned
   - Updated goals or priorities
   - Changed personal circumstances

2. **Project Updates** (`.claude/context/active-projects/`):
   - Project progress or status changes
   - New information about current initiatives
   - Completed milestones or blockers

3. **Tool Updates** (`.claude/context/tools/`):
   - New integrations or capabilities discovered
   - Changed API configurations or workflows

**If updates are needed**: Make the edits now before responding.
**If no updates needed**: Proceed with your response.

This ensures session-to-session continuity since you are stateless.
</system-reminder>"""

        # Output the result with the reminder
        result = {
            "continue": True,
            "message": reminder
        }

        print(json.dumps(result))
        sys.exit(0)

    except json.JSONDecodeError:
        # If we can't parse input, just continue
        print(json.dumps({"continue": True}))
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        print(json.dumps({"continue": True}))
        sys.exit(0)


if __name__ == '__main__':
    main()
