---
name: ecosystem-builder
description: |
  Trigger autonomous ecosystem expansion. Use when asked to "build skills", "expand ecosystem", "find gaps", or "generate artifacts".
license: MIT
metadata:
  version: 0.1.0
  model: claude-opus-4-5-20251101
  domains: [meta, automation, skills]
  type: orchestrator
allowed-tools:
  - Bash
  - Read
  - Task
---

# Ecosystem Builder

Autonomous workflow that expands the skill ecosystem by finding gaps, building artifacts, and staging for review.

## Triggering

When the user asks to:
- "Build N skills"
- "Expand the ecosystem"
- "Find gaps in skills"
- "Generate new skills"

## Process

1. **Parse the request** to determine budget:
   - Number of artifacts (required)
   - Time limit (optional, default 4 hours)
   - Cost limit (optional, default $50)

2. **Start the run:**
   ```bash
   ~/.claude/plugins/ecosystem-builder/bin/ecosystem-builder run --artifacts N
   ```

3. **Monitor progress:**
   ```bash
   ~/.claude/plugins/ecosystem-builder/bin/ecosystem-builder status
   ```

4. **Report completion** with summary of:
   - Artifacts analyzed, built, passed, failed
   - Location of staged artifacts
   - Next step: review with `ecosystem-builder review`

## Example

User: "Build 5 new skills for me"

Response: "I'll start an ecosystem-builder run to generate 5 skills."

```bash
~/.claude/plugins/ecosystem-builder/bin/ecosystem-builder run --artifacts 5
```

"The run is in progress. I'll monitor and report when complete."

## Limitations

- Phase 2: Build function returns None (not yet implemented)
- Phase 2: Validation always passes (not yet implemented)
- Gap analysis uses heuristics (expected patterns, structural checks)
- Skills will be staged, not deployed to production
- Human review required via `ecosystem-builder review`
