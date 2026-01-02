# Plugin Pipeline Audit Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply 10 audit fixes to the plugin pipeline design document before implementing skills.

**Architecture:** Edit the design document (`~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`) in 10 sequential steps, each targeting a specific fix identified by the 4-lens audit.

**Tech Stack:** Markdown editing only.

---

## Task 1: Add Explicit Handoff Commands (Fix 1.1)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Locate brainstorming-plugins handoff section**

Search for: `## Handoff` in the brainstorming-plugins skill design (around line 181-186)

**Step 2: Replace handoff with explicit command**

Find:
```markdown
## Handoff
"Use brainstorming-{component} to design each:
- brainstorming-skills
- brainstorming-hooks
- brainstorming-agents
- brainstorming-commands"
```

Replace with:
```markdown
## Next Step

Run the command for your first component:

| Component | Command |
|-----------|---------|
| Skill | `/brainstorming-skills` |
| Hook | `/brainstorming-hooks` |
| Agent | `/brainstorming-agents` |
| Command | `/brainstorming-commands` |

Copy-paste the command above to continue.
```

**Step 3: Locate brainstorming-skills handoff section**

Search for: `## Handoff` in the brainstorming-skills skill design (around line 414-417)

**Step 4: Replace handoff with explicit command**

Find:
```markdown
## Handoff

"Design complete. Next steps:
- Use **implementing-skills** to build it (TDD workflow)
- Reference **skill-development** for structural details"
```

Replace with:
```markdown
## Next Step

Run this command to continue:

```
/implementing-skills docs/plans/[your-design-file].md
```

Replace `[your-design-file]` with the actual design document path.
```

**Step 5: Locate implementing-skills handoff section**

Search for: `## Handoff` in the implementing-skills skill design (around line 692-700)

**Step 6: Replace handoff with explicit command**

Find:
```markdown
## Handoff

"Skill implemented and tested. What's next?

| Situation | Next Step |
|-----------|-----------|
| More components to build | → brainstorming-{component} |
| Plugin complete, want polish | → optimizing-plugins |
| Ready to publish | → deploying-plugins |
| Personal use only | Done (skill is active) |"
```

Replace with:
```markdown
## Next Step

Choose one and run:

| Situation | Command |
|-----------|---------|
| More components to build | `/brainstorming-{component}` |
| Plugin complete, want polish | `/optimizing-plugins path/to/plugin` |
| Ready to publish (skip polish) | `/deploying-plugins path/to/plugin` |
| Personal use only | Done — skill is active in `~/.claude/skills/` |

Copy-paste the command above to continue.
```

**Step 7: Verify changes**

Run: `grep -n "## Next Step" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 3 matches (brainstorming-plugins, brainstorming-skills, implementing-skills)

---

## Task 2: Replace Checklists with Show-Your-Work (Fix 1.2)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Locate brainstorming-skills verification section**

Search for: `## Verification` in brainstorming-skills (around line 432-440)

**Step 2: Replace checkbox list with output table**

Find:
```markdown
## Verification

After design session:

- [ ] Purpose statement is specific (not generic)
- [ ] 3-5 trigger phrases cover different phrasings
- [ ] Scope has explicit IN and OUT boundaries
- [ ] SKILL.md outline is self-sufficient
- [ ] References are for depth, not workflow steps
- [ ] Checked for overlap with existing skills
- [ ] Design document written to docs/plans/
- [ ] User validated each section
```

Replace with:
```markdown
## Verification Output

Before completing, output these with actual values:

| Check | Your Answer |
|-------|-------------|
| Purpose statement | [paste the 1-2 sentence statement] |
| Why it's specific, not generic | [1 sentence explanation] |
| 3-5 trigger phrases | [list them] |
| Why they cover different phrasings | [1 sentence] |
| IN scope (3+ items) | [list them] |
| OUT of scope (3+ items) | [list them] |
| SKILL.md outline | [list main sections] |
| Similar existing skills checked | [list skills checked, or "none found"] |
| Design document path | [exact path] |
```

**Step 3: Locate implementing-skills verification section**

Search for: `## Verification` in implementing-skills (around line 713-739)

**Step 4: Replace checkbox list with output table**

Find:
```markdown
## Verification

After implementation:

**RED Phase:**
- [ ] Created pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Ran WITHOUT skill — documented baseline verbatim
- [ ] Identified rationalization patterns

**GREEN Phase:**
- [ ] Name uses only letters, numbers, hyphens
- [ ] Description starts "Use when..." with specific triggers
- [ ] Addressed specific baseline failures
- [ ] Ran WITH skill — verified compliance

**REFACTOR Phase:**
- [ ] Identified NEW rationalizations
- [ ] Added explicit counters
- [ ] Built rationalization table (discipline skills)
- [ ] Re-tested until bulletproof

**Quality:**
- [ ] Quick reference table included
- [ ] Common mistakes section (if applicable)
- [ ] No narrative storytelling
- [ ] References only for depth, not workflow steps
```

Replace with:
```markdown
## Verification Output

Before completing, output these with actual values:

**RED Phase:**
| Check | Your Answer |
|-------|-------------|
| Pressure scenarios created | [list 3+ pressures combined] |
| Baseline test result (without skill) | [quote verbatim what agent did wrong] |
| Rationalization patterns found | [list exact phrases] |

**GREEN Phase:**
| Check | Your Answer |
|-------|-------------|
| Skill name | [name, letters/numbers/hyphens only] |
| Description | [paste full description starting "Use when..."] |
| Baseline failures addressed | [list which failures this fixes] |
| Test result (with skill) | [quote what agent did correctly] |

**REFACTOR Phase:**
| Check | Your Answer |
|-------|-------------|
| New rationalizations found | [list any new ones, or "none"] |
| Counters added | [list counters added] |
| Final test result | [quote final behavior] |
```

**Step 5: Verify changes**

Run: `grep -n "## Verification Output" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 2 matches (brainstorming-skills, implementing-skills)

---

## Task 3: Reverse Light/Deep Default (Fix 1.3)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Locate "Choosing Depth" section in brainstorming-skills**

Search for: `## Choosing Depth` (around line 319-332)

**Step 2: Replace with reversed default**

Find:
```markdown
## Choosing Depth

Assess before starting:

| Signal | Depth | Action |
|--------|-------|--------|
| Simple knowledge, clear scope | Light | Use this skill |
| Multiple valid approaches | Light | More questions, same process |
| Foundational/critical skill | Deep | → skillforge |
| Complex domain, many unknowns | Deep | → skillforge |
| User requests thorough analysis | Deep | → skillforge |

Ask: "This seems [simple/complex]. Light design here, or deep analysis
via skillforge?"
```

Replace with:
```markdown
## Routing Decision

**Default:** Use skillforge methodology (deep path)

**Light path only if ALL conditions met:**
- [ ] Scope is obvious (can state in one sentence)
- [ ] No coordination with other skills
- [ ] No failure modes that need explicit handling
- [ ] Similar skill exists as template

If uncertain about ANY condition, use skillforge.

**Announce decision:** "Using [light/skillforge] because [reason]."
```

**Step 3: Verify change**

Run: `grep -n "## Routing Decision" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 1 match

---

## Task 4: Add Progress Markers (Fix 1.4)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Locate brainstorming-skills process phases**

Search for: `### 1. Core Purpose` (around line 336)

**Step 2: Add progress marker to phase 1**

Find:
```markdown
### 1. Core Purpose
Ask one question at a time:
```

Replace with:
```markdown
### Step 1 of 6: Core Purpose

Ask one question at a time:
```

**Step 3: Add progress marker to phase 2**

Find:
```markdown
### 2. Trigger Design

| Aspect | Questions |
```

Replace with:
```markdown
### Step 2 of 6: Trigger Design

---
Progress: █░░░░░ 1/6 complete | Next: Trigger Design
---

| Aspect | Questions |
```

**Step 4: Add progress marker to phase 3**

Find:
```markdown
### 3. Knowledge Scope

| Boundary | Define Explicitly |
```

Replace with:
```markdown
### Step 3 of 6: Knowledge Scope

---
Progress: ██░░░░ 2/6 complete | Next: Knowledge Scope
---

| Boundary | Define Explicitly |
```

**Step 5: Add progress marker to phase 4**

Find:
```markdown
### 4. Structure Decisions

| Component | Decision | Size Target |
```

Replace with:
```markdown
### Step 4 of 6: Structure Decisions

---
Progress: ███░░░ 3/6 complete | Next: Structure Decisions
---

| Component | Decision | Size Target |
```

**Step 6: Add progress marker to phase 5**

Find:
```markdown
### 5. Composition

- What skills might be used alongside this one?
```

Replace with:
```markdown
### Step 5 of 6: Composition

---
Progress: ████░░ 4/6 complete | Next: Composition
---

- What skills might be used alongside this one?
```

**Step 7: Add progress marker to phase 6**

Find:
```markdown
### 6. Present Design

Present in 200-300 word sections:
```

Replace with:
```markdown
### Step 6 of 6: Present Design

---
Progress: █████░ 5/6 complete | Next: Present Design
---

Present in 200-300 word sections:
```

**Step 8: Add progress markers to implementing-skills RED/GREEN/REFACTOR**

Find:
```markdown
### RED: Write Failing Test (Baseline)
```

Replace with:
```markdown
### Step 1 of 3: RED — Write Failing Test (Baseline)
```

Find:
```markdown
### GREEN: Write Minimal Skill
```

Replace with:
```markdown
### Step 2 of 3: GREEN — Write Minimal Skill

---
Progress: █░░ 1/3 complete | Next: GREEN
---
```

Find:
```markdown
### REFACTOR: Close Loopholes
```

Replace with:
```markdown
### Step 3 of 3: REFACTOR — Close Loopholes

---
Progress: ██░ 2/3 complete | Next: REFACTOR
---
```

**Step 9: Verify changes**

Run: `grep -c "Step [0-9] of [0-9]" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 9 (6 in brainstorming-skills + 3 in implementing-skills)

---

## Task 5: Add Pipeline Context References (Fix 2.1)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: In brainstorming-skills, add Pipeline Context after Prerequisites**

Find:
```markdown
## Prerequisites

| Prerequisite | Source |
|--------------|--------|
| Know you need a skill | brainstorming-plugins or direct knowledge |
| Understand the problem | User context |

## Quick Reference
```

Insert between (after Prerequisites, before Quick Reference):
```markdown
## Pipeline Context

This skill is **Stage 2: Design** in the plugin development pipeline.

See: `brainstorming-plugins` for full pipeline overview.

| Aspect | Value |
|--------|-------|
| This stage | Design skill from requirements |
| Prerequisite | `/brainstorming-plugins` (or direct request) |
| Hands off to | `/implementing-skills` |

## Quick Reference
```

**Step 2: In implementing-skills, add Pipeline Context after Prerequisites**

Find:
```markdown
## Prerequisites

| Prerequisite | Source |
|--------------|--------|
| Skill design (purpose, triggers, scope) | brainstorming-skills or equivalent |
| Structural knowledge | skill-development (reference) |

**No design?** Use brainstorming-skills first, or proceed with clear
mental model of what you're building.

## Quick Reference
```

Insert between:
```markdown
## Pipeline Context

This skill is **Stage 3: Implement** in the plugin development pipeline.

See: `brainstorming-plugins` for full pipeline overview.

| Aspect | Value |
|--------|-------|
| This stage | Build skill from design using TDD |
| Prerequisite | `/brainstorming-skills` (design document) |
| Hands off to | `/optimizing-plugins` or `/deploying-plugins` |

## Quick Reference
```

**Step 3: Verify changes**

Run: `grep -n "## Pipeline Context" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 2 matches (brainstorming-skills, implementing-skills)

---

## Task 6: Remove All Extension Points Sections (Fix 2.2)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Delete brainstorming-skills Extension Points**

Find and delete entire section (around line 459-463):
```markdown
## Extension Points

1. **Domain-specific checklists** — Add scope questions for specific domains
2. **Trigger testing scripts** — Automated trigger quality checking
3. **Ecosystem scan integration** — Auto-check for similar skills
```

**Step 2: Delete implementing-skills Extension Points**

Find and delete entire section (around line 756-760):
```markdown
## Extension Points

1. **Automated pressure testing** — Scripts to run scenarios systematically
2. **Rationalization library** — Common rationalizations by skill type
3. **Coverage metrics** — Track which pressures tested
```

**Step 3: Delete deploying-plugins Extension Points**

Find and delete entire section (around line 1085-1090):
```markdown
## Extension Points

1. **Automated packaging scripts** — CI/CD for plugin releases
2. **Marketplace API integration** — Automated submission
3. **Announcement templates** — Consistent release communications
4. **Installation testing automation** — Scripted install verification
```

**Step 4: Verify removal**

Run: `grep -n "## Extension Points" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 0 matches

---

## Task 7: Extract Deep Dives to References (Fix 2.3)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Note location of Deep Dives in implementing-skills**

Find the two `<details>` blocks (around lines 609-681):
- "Deep Dive: Bulletproofing Against Rationalization"
- "Deep Dive: Pressure Scenario Design"

**Step 2: Replace first Deep Dive with reference**

Find:
```markdown
<details>
<summary><strong>Deep Dive: Bulletproofing Against Rationalization</strong></summary>

For discipline skills, build explicit defenses against agent rationalization.
[...entire content...]
</details>
```

Replace with:
```markdown
**Deep Dive:** See `references/bulletproofing-rationalization.md` for building explicit defenses against agent rationalization.
```

**Step 3: Replace second Deep Dive with reference**

Find:
```markdown
<details>
<summary><strong>Deep Dive: Pressure Scenario Design</strong></summary>

Effective pressure scenarios combine multiple pressure types:
[...entire content...]
</details>
```

Replace with:
```markdown
**Deep Dive:** See `references/pressure-scenario-design.md` for designing effective pressure scenarios.
```

**Step 4: Add note about creating reference files**

Add comment at end of implementing-skills section:
```markdown
<!-- NOTE: Create these reference files during implementation:
- references/bulletproofing-rationalization.md (from original Deep Dive content)
- references/pressure-scenario-design.md (from original Deep Dive content)
-->
```

**Step 5: Verify changes**

Run: `grep -c "<details>" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 0 (all `<details>` blocks removed)

---

## Task 8: Add Design Template Reference (Fix 3.1)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Find Output section in brainstorming-skills**

Search for: `## Output` in brainstorming-skills (around line 400-412)

**Step 2: Add template reference**

Find:
```markdown
## Output

Write validated design to: `docs/plans/YYYY-MM-DD-<skill-name>-design.md`

**Design document includes:**
```

Replace with:
```markdown
## Output

Write validated design to: `docs/plans/YYYY-MM-DD-<skill-name>-design.md`

**Use template:** `references/design-template.md`

**Design document includes:**
```

**Step 3: Add design template content to the design doc**

Add after the brainstorming-skills skill block (after line ~464, after the closing triple-backticks):

```markdown
#### Design Template (references/design-template.md)

```markdown
# Skill Design: [Name]

## Purpose
[One sentence: what this skill does]

## Triggers
- [natural phrase 1]
- [natural phrase 2]
- [natural phrase 3]

## Scope
**In scope:**
- [what this skill handles]

**Out of scope:**
- [what this skill does NOT handle]

## Structure
| Component | Content |
|-----------|---------|
| SKILL.md | [outline of main sections] |
| references/ | [list files needed, or "none"] |
| scripts/ | [list scripts needed, or "none"] |

## Anti-Patterns
| Avoid | Why | Instead |
|-------|-----|---------|

## Success Criteria
[How to know the skill is working correctly]
```
```

**Step 4: Verify change**

Run: `grep -n "references/design-template.md" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 2 matches (reference in Output + the template itself)

---

## Task 9: Add Fast-Path (Fix 3.2)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Find Overview section in brainstorming-plugins**

Search for: `## Overview` in brainstorming-plugins (around line 129-132)

**Step 2: Add Fast Path after Overview**

Find:
```markdown
## Overview
Identify which components your plugin needs, then hand off to
component-specific design skills.

## Prerequisites
```

Insert between:
```markdown
## Fast Path

If user request explicitly mentions component type, skip triage:

| User Says | Skip To |
|-----------|---------|
| "I want to build a skill for X" | `/brainstorming-skills` |
| "I need a hook that Y" | `/brainstorming-hooks` |
| "Create a command for Z" | `/brainstorming-commands` |
| "Build an agent that W" | `/brainstorming-agents` |

**Only use triage when:** User is unsure what components they need, or describes a problem without specifying component type.

## Prerequisites
```

**Step 3: Verify change**

Run: `grep -n "## Fast Path" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 1 match

---

## Task 10: Add Prerequisites Check (Fix 3.3)

**Files:**
- Modify: `~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

**Step 1: Find Prerequisites section in implementing-skills**

Search for: `## Prerequisites` in implementing-skills (around line 513-520)

**Step 2: Add Prerequisites Check after**

Find:
```markdown
**No design?** Use brainstorming-skills first, or proceed with clear
mental model of what you're building.

## Pipeline Context
```

Insert between:
```markdown
## Prerequisites Check

Before proceeding, verify and announce:

1. **Design document exists?**
   - If yes: "I see the design at `[path]`. Proceeding with implementation."
   - If no: "I don't see a design document. Should we start with `/brainstorming-skills`?"

2. **Design has required sections?**
   | Section | Status |
   |---------|--------|
   | Purpose | [present/missing] |
   | Triggers | [present/missing] |
   | Scope | [present/missing] |

If any section is missing, ask: "The design is missing [sections]. Should we complete it first?"

## Pipeline Context
```

**Step 3: Verify change**

Run: `grep -n "## Prerequisites Check" ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md`

Expected: 1 match

---

## Task 11: Commit All Changes

**Step 1: Verify all fixes applied**

Run verification commands from each task. Expected results:
- 3 "## Next Step" sections
- 2 "## Verification Output" sections
- 1 "## Routing Decision" section
- 9 "Step N of M" markers
- 2 "## Pipeline Context" sections
- 0 "## Extension Points" sections
- 0 `<details>` blocks
- 2 "design-template.md" references
- 1 "## Fast Path" section
- 1 "## Prerequisites Check" section

**Step 2: Stage and commit**

```bash
git add ~/.claude/docs/plans/2026-01-02-plugin-pipeline-slice1-design.md
git commit -m "docs: apply 10 audit fixes to plugin pipeline design

- Fix 1.1: Replace prose handoffs with literal /commands
- Fix 1.2: Replace checkbox verification with show-your-work tables
- Fix 1.3: Reverse light/deep default (skillforge is now default)
- Fix 1.4: Add progress markers (Step N of M) to workflow phases
- Fix 2.1: Add Pipeline Context sections referencing brainstorming-plugins
- Fix 2.2: Remove all Extension Points sections (YAGNI)
- Fix 2.3: Replace inline Deep Dives with references/ links
- Fix 3.1: Add design template reference and content
- Fix 3.2: Add Fast Path for explicit component requests
- Fix 3.3: Add Prerequisites Check section

Source: 4-lens audit (Robustness + Minimalist + Capability + Arbiter)"
```

---

## Summary

| Task | Fix | Description |
|------|-----|-------------|
| 1 | 1.1 | Add explicit handoff commands |
| 2 | 1.2 | Replace checklists with show-your-work |
| 3 | 1.3 | Reverse light/deep default |
| 4 | 1.4 | Add progress markers |
| 5 | 2.1 | Add Pipeline Context references |
| 6 | 2.2 | Remove Extension Points |
| 7 | 2.3 | Extract Deep Dives to references |
| 8 | 3.1 | Add design template reference |
| 9 | 3.2 | Add Fast Path |
| 10 | 3.3 | Add Prerequisites Check |
| 11 | — | Commit all changes |

**Total edits:** ~25 find/replace operations
**Commits:** 1 (all fixes together)
