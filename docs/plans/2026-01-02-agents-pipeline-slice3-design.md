# Agents Pipeline (Slice 3) Design

> **⚠️ SUPERSEDED (2026-01-02):** Implementation complete
>
> - Replacement: `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md` and `plugins/plugin-dev/skills/implementing-agents/SKILL.md`
>
> *Original preserved for historical reference.*

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Create brainstorming-agents and implementing-agents skills to complete Slice 3 of the plugin development pipeline.

**Architecture:** Two workflow skills following the pattern established in Slice 1 (Skills) and Slice 2 (Hooks). brainstorming-agents guides design using the official 6-step process; implementing-agents guides validation using triggering-first TDD.

**Tech Stack:** Markdown skills with YAML frontmatter, references to existing agent-development skill.

---

## Context

### Pipeline Status

| Slice | Skills | Status |
|-------|--------|--------|
| 1. Skills | brainstorming-skills, implementing-skills | ✅ Complete |
| 2. Hooks | brainstorming-hooks, implementing-hooks | ✅ Complete |
| 3. Agents | brainstorming-agents, implementing-agents | 🔲 This design |
| 4. Commands | brainstorming-commands, implementing-commands | 🔲 Not started |

### Key References

| File | Purpose | Lines |
|------|---------|-------|
| `plugins/plugin-dev/skills/agent-development/SKILL.md` | Structural reference | 416 |
| `plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md` | Official 6-step process | 208 |
| `plugins/plugin-dev/skills/agent-development/references/triggering-examples.md` | Example crafting guide | 492 |
| `docs/claude-code-documentation/subagents-overview.md` | Official Anthropic docs | 581 |

### Existing Stubs

- `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md` - Currently "[COMING SOON]"
- `plugins/plugin-dev/skills/implementing-agents/SKILL.md` - Currently "[COMING SOON]"

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Design framing | Two-phase: delegation + persona | Agents require both "what to hand off" and "who handles it" |
| Workflow structure | Official 6-step from agent-creation-system-prompt.md | Proven pattern, consistency with Claude Code internals |
| Presentation style | Conversational questions (hybrid) | Follows brainstorming-skills/hooks patterns |
| Triggering examples | Design concern (in design doc) | Official system prompt mandates examples in description |
| Validation order | Triggering first, then quality | System prompt only runs after Claude delegates |
| Core principle | "Test triggering before tuning quality" | From agent-development skill ordering (lines 307-326) |

---

## brainstorming-agents Skill

### Purpose

Guide users through designing agents before implementation, ensuring they think through delegation decisions, persona design, and triggering scenarios.

### Core Principle

> Description with examples is the most critical field. If Claude doesn't know when to delegate, the system prompt doesn't matter.

### Two-Phase Framing

1. **Delegation Decision** — What complex work should Claude hand off?
2. **Persona Design** — What specialist handles this work?

### 6-Step Workflow

Mapped from `agent-creation-system-prompt.md`:

| Step | Question | What It Produces |
|------|----------|------------------|
| 1. Extract Core Intent | "What task is complex enough to delegate?" | Clear delegation rationale |
| 2. Design Expert Persona | "What specialist would you hire?" | Agent role, expertise, identity |
| 3. Architect Comprehensive Instructions | "What process should the agent follow?" | System prompt structure |
| 4. Optimize for Performance | "What quality checks and fallbacks?" | Decision frameworks, boundaries |
| 5. Create Identifier | "What's a clear, memorable name?" | Final `subagent_type` name |
| 6. Define Triggering Examples | "When exactly should Claude delegate?" | `<example>` blocks for description field |

### Key Insight

Step 6 produces examples that go in the `description` frontmatter field (called `whenToUse` in JSON). This field is "the most critical" per agent-development skill (line 84).

### Output

Design document with:
- Agent name and identifier
- Description with 2-4 `<example>` blocks
- System prompt structure
- Tool restrictions (if any)
- Model and color choices

---

## implementing-agents Skill

### Purpose

Guide users through implementing and validating agents using a test-first approach, ensuring triggering works before investing in system prompt quality.

### Core Principle

> TEST TRIGGERING BEFORE TUNING QUALITY. If Claude won't delegate to your agent, perfecting the system prompt is wasted effort.

### Why This Order Matters

- System prompt only runs AFTER Claude decides to delegate
- A beautiful system prompt with bad triggering = agent never used
- Bad triggering is cheaper to fix than bad system prompt

### Three-Phase Validation

Derived from agent-development skill (lines 307-326) and triggering-examples.md debugging section (lines 439-469):

| Phase | What to Test | How to Test | Iterate On |
|-------|--------------|-------------|------------|
| **1. Triggering** | Does Claude delegate? | Ask tasks matching your examples | description/examples |
| **2. Quality** | Does agent produce good output? | Invoke agent explicitly by name | system prompt |
| **3. Harden** | Edge cases, false positives? | Various phrasings, edge scenarios | both |

### Phase 1: Triggering (RED/GREEN)

1. Write description with `<example>` blocks
2. Ask Claude a task matching your examples
3. **RED:** Claude doesn't delegate → fix description/examples
4. **GREEN:** Claude delegates → move to Phase 2

### Phase 2: Quality

1. Invoke agent explicitly (bypass triggering)
2. Evaluate output against expectations
3. Iterate on system prompt until output is good

### Phase 3: Harden

1. Test with varied phrasings of same intent
2. Check for false positives (triggering when it shouldn't)
3. Test edge cases mentioned in system prompt

### Three Triggering Failure Modes

From `triggering-examples.md` lines 439-469:

| Failure Mode | Symptom | Fix |
|--------------|---------|-----|
| Not triggering | Claude ignores agent | Add more examples covering different phrasings |
| Triggering too often | Agent fires inappropriately | Make examples more specific, add negative examples |
| Wrong scenarios | Agent fires for wrong tasks | Revise examples to show only correct scenarios |

---

## Implementation Tasks

### Task 1: Replace brainstorming-agents stub

**Files:**
- Replace: `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md`

**Content structure:**
```markdown
---
name: brainstorming-agents
description: [trigger phrases]
version: 0.1.0
---

# Brainstorming Agents

## Quick Start
[6 steps as questions]

## Triggers
[When skill activates]

## Prerequisites
[Link to agent-development skill]

## Pipeline Context
[Position in plugin-dev pipeline]

## Core Principle
[Description is most critical field]

## Two-Phase Framing
[Delegation + Persona]

## 6-Step Workflow
[Full workflow with questions, guidance, examples]

## Anti-Patterns
[Common mistakes]

## Verification
[How to validate design completeness]

## Handoff
[Link to implementing-agents]
```

**Commit:** `feat(plugin-dev): add brainstorming-agents skill`

### Task 2: Replace implementing-agents stub

**Files:**
- Replace: `plugins/plugin-dev/skills/implementing-agents/SKILL.md`

**Content structure:**
```markdown
---
name: implementing-agents
description: [trigger phrases]
version: 0.1.0
---

# Implementing Agents

## Quick Start
[3 phases overview]

## Triggers
[When skill activates]

## Prerequisites Check
[Design from brainstorming-agents]

## Pipeline Context
[Position in plugin-dev pipeline]

## Core Principle
[Test triggering before tuning quality]

## Three-Phase Validation
[Triggering → Quality → Harden]

## Phase 1: Triggering (RED/GREEN)
[Detailed workflow]

## Phase 2: Quality
[Detailed workflow]

## Phase 3: Harden
[Detailed workflow]

## Triggering Failure Modes
[Three modes with fixes]

## Checklist
[Verification checklist]

## Anti-Patterns
[Common mistakes]
```

**Commit:** `feat(plugin-dev): add implementing-agents skill`

### Task 3: Update design document

**Files:**
- Modify: `docs/plans/2026-01-02-agents-pipeline-slice3-design.md`

**Changes:**
- Add implemented marker at top

**Commit:** `docs: mark agents pipeline slice 3 as implemented`

### Task 4: Verify skills load

**Verification:**
```bash
# Check frontmatter validity
head -20 plugins/plugin-dev/skills/brainstorming-agents/SKILL.md
head -20 plugins/plugin-dev/skills/implementing-agents/SKILL.md

# Verify skill count
ls plugins/plugin-dev/skills/*/SKILL.md | wc -l
```

### Task 5: Merge to main

Use `superpowers:finishing-a-development-branch` skill.

---

## Success Criteria

- [ ] brainstorming-agents skill follows 6-step workflow from official docs
- [ ] implementing-agents skill follows triggering-first validation
- [ ] Both skills have valid frontmatter (name, description, version)
- [ ] Both skills reference agent-development for structural details
- [ ] Pipeline documentation updated
- [ ] All commits follow conventional format
