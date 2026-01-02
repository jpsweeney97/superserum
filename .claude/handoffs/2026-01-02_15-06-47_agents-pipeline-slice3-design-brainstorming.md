---
date: 2026-01-02T15:06:47.885225
version: 1
git_commit: b520ed2
branch: main
repository: superserum
tags: ["plugin-dev", "agents", "slice3", "brainstorming"]
---

# Handoff: agents-pipeline-slice3-design-brainstorming

## Goal
Design brainstorming-agents and implementing-agents skills for Slice 3 of the plugin development pipeline

## Key Decisions
- Two-phase design framing: (1) delegation decision - what work should Claude hand off, (2) persona design - what specialist handles it
- Follow official Claude Code agent creation system prompt 6-step structure, presented conversationally with questions (hybrid approach)
- Triggering examples are a DESIGN concern (Option A) - design doc includes full description with <example> blocks, not implementation detail
- Implementation validation: Triggering first, then Quality (Option C with ordering) - test automatic delegation before investing in system prompt
- Core principle for implementing-agents: TEST TRIGGERING BEFORE TUNING QUALITY - if Claude wont delegate, system prompt doesnt matter
- agent-development skill remains as structural reference (like hook-development), new skills handle workflow

## Learnings
- Official Claude Code agent creation system prompt (in agent-development/references/agent-creation-system-prompt.md) mandates <example> blocks in whenToUse field
- Example format: <example>Context:... user:... assistant:... <commentary>...</commentary></example>
- Agent triggering has 3 failure modes: not triggering, triggering too often, wrong scenarios - each needs different fixes
- Agents can be invoked explicitly by name OR automatically via delegation - both paths need testing
- agent-development skill lists Test Triggering BEFORE Test System Prompt (lines 307-326)
- triggering-examples.md (492 lines) is comprehensive reference for crafting examples

## 6-Step Workflow Mapping (for brainstorming-agents)

| Official Step | Question-Driven Version |
|---------------|------------------------|
| 1. Extract Core Intent | "What complex work should Claude hand off?" |
| 2. Design Expert Persona | "What specialist handles this?" |
| 3. Architect Instructions | "What process should the agent follow?" |
| 4. Optimize for Performance | "What quality checks and fallbacks?" |
| 5. Create Identifier | "What's a clear, memorable name?" |
| 6. Create Examples | "When exactly should Claude use this?" |

## implementing-agents Phases

| Phase | What to Test | How to Test | Iterate On |
|-------|--------------|-------------|------------|
| 1. Triggering | Does Claude delegate? | Ask task matching examples | description/examples |
| 2. Quality | Does agent produce good output? | Explicit invocation | system prompt |
| 3. Harden | Edge cases, false positives | Various phrasings | both |

## Critical References

| File | Purpose | Lines |
|------|---------|-------|
| `plugins/plugin-dev/skills/agent-development/SKILL.md` | Structural reference | 416 lines |
| `plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md` | Official 6-step process | 208 lines |
| `plugins/plugin-dev/skills/agent-development/references/triggering-examples.md` | Example crafting guide | 492 lines |
| `docs/claude-code-documentation/subagents-overview.md` | Official Anthropic docs | 581 lines |

## Existing Stubs to Replace

- `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md` - Currently "[COMING SOON]"
- `plugins/plugin-dev/skills/implementing-agents/SKILL.md` - Currently "[COMING SOON]"

## Completed This Session

- Slice 2 (Hooks) fully implemented and merged to main (commit b520ed2)
- brainstorming-hooks: 6-step hook design workflow
- implementing-hooks: TDD hook implementation with RED/GREEN/REFACTOR

## Next Steps
1. Present design Section 1: brainstorming-agents overview and 6-step workflow mapping
2. Present design Section 2: implementing-agents TDD-style phases (Triggering -> Quality -> Harden)
3. Write design document to docs/plans/2026-01-02-agents-pipeline-slice3-design.md
4. Create worktree and implementation plan
5. Implement skills using subagent-driven-development

## Uncommitted Files
```
claude/handoffs/2026-01-01_22-35-11_superserum-marketplace-migration-complete.md
.claude/handoffs/2026-01-02_12-56-05_plugin-pipeline-slice1-complete.md
```
