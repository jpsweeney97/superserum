# Plugin Optimizer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an interactive optimization skill for Claude Code plugins that examines plugins through 6 analytical lenses and produces prioritized design documents.

**Architecture:** Command + skill separation. Command (`optimize.md`) handles invocation and delegates to skill (`optimizing-plugins/SKILL.md`). Skill contains session methodology; detailed lens criteria live in `references/lenses.md` for progressive disclosure.

**Tech Stack:** Markdown (YAML frontmatter), Claude Code plugin system

**Design Document:** `docs/plans/2024-12-29-plugin-optimizer-design.md`

---

## Task 1: Create the Optimize Command

**Files:**
- Create: `plugins/plugin-dev/commands/optimize.md`

**Step 1: Create command file with frontmatter**

```markdown
---
description: Systematically optimize a plugin through 6 analytical lenses, producing a prioritized design document
argument-hint: "<plugin-path>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - TodoWrite
  - AskUserQuestion
  - Skill
---

# Optimize Plugin Command

Invoke the optimizing-plugins skill to systematically improve a Claude Code plugin from "good" to "great."

## Arguments

- `$1` - Plugin path (required)

## Process

1. **Validate plugin path**
   - Verify path exists
   - Verify `.claude-plugin/plugin.json` exists
   - If invalid, report error and exit

2. **Invoke the skill**
   - Use the Skill tool to invoke `plugin-dev:optimizing-plugins`
   - Pass the plugin path as context

## Relationship to Audit

- **Audit** (`/plugin-dev:audit-plugin`) finds problems — "broken to working"
- **Optimize** (`/plugin-dev:optimize`) improves quality — "good to great"

Run audit first if unsure whether the plugin has structural issues.

## Example

```
/plugin-dev:optimize plugins/superpowers
```
```

**Step 2: Verify file created**

Run: `ls -la plugins/plugin-dev/commands/optimize.md`
Expected: File exists with correct permissions

**Step 3: Commit**

```bash
git add plugins/plugin-dev/commands/optimize.md
git commit -m "feat(plugin-dev): add optimize command"
```

---

## Task 2: Create the Skill Directory Structure

**Files:**
- Create: `plugins/plugin-dev/skills/optimizing-plugins/` directory
- Create: `plugins/plugin-dev/skills/optimizing-plugins/references/` directory

**Step 1: Create directories**

```bash
mkdir -p plugins/plugin-dev/skills/optimizing-plugins/references
```

**Step 2: Verify structure**

Run: `ls -la plugins/plugin-dev/skills/optimizing-plugins/`
Expected: Directory exists with references/ subdirectory

---

## Task 3: Create the Main SKILL.md

**Files:**
- Create: `plugins/plugin-dev/skills/optimizing-plugins/SKILL.md`

**Step 1: Write the skill file**

```markdown
---
name: optimizing-plugins
description: Systematically improves Claude Code plugins through 6 analytical lenses. Use after audit confirms no broken issues, when asked to optimize, improve, or enhance a plugin, or when refining trigger phrases, token efficiency, or structural clarity.
---

# Plugin Optimizer

Guides systematic plugin improvement through collaborative dialogue, examining plugins through 6 lenses and producing a prioritized optimization design.

**Announce at start:** "I'm using the optimizing-plugins skill to systematically improve this plugin."

## Overview

The optimizer examines plugins through six analytical lenses, producing a prioritized design document. It guides improvement from "good" to "great" — distinct from audit, which fixes broken plugins.

**Relationship to audit:**
- **Audit** finds problems — "broken to working"
- **Optimizer** improves quality — "good to great"

## The Process

### Phase 1: Orientation

Scan the plugin and deliver a one-paragraph assessment:

1. Read `.claude-plugin/plugin.json` for plugin metadata
2. List all skills, commands, agents, hooks
3. Sample 2-3 key files to understand quality level
4. Provide overall health assessment:
   - General quality level
   - Areas of strength
   - Where the most opportunity lies

This grounds both Claude and user before the tour begins.

### Phase 2: Guided Tour

Walk through 6 lenses in fixed order:

| # | Lens | Core Question |
|---|------|---------------|
| 1 | Trigger Fidelity | Will Claude invoke this at the right moment? |
| 2 | Token Economy | Does every token earn its keep? |
| 3 | Structural Clarity | Can Claude navigate and understand efficiently? |
| 4 | Degrees of Freedom | Does specificity match task fragility? |
| 5 | Resilience | What happens when things go wrong? |
| 6 | Plugin Coherence | Does this work as a unified whole? |

See [references/lenses.md](references/lenses.md) for detailed criteria per lens.

**At each lens:**

1. Analyze the plugin against lens criteria
2. Present findings summary
3. User chooses depth: **Skip**, **Skim**, or **Deep**

**For clean lenses:** Acknowledge briefly and auto-advance: "Trigger Fidelity looks solid — descriptions are specific and action-oriented."

### Phase 3: Synthesis

After all lenses, review cross-cutting concerns:

- Interactions between suggestions
- Opportunities to consolidate related changes
- Dependencies that affect implementation order

### Phase 4: Document & Handoff

1. Write the optimization design document
2. Ask: "Ready to set up for implementation?"
3. If yes: worktrees → writing-plans → execute

## Interaction Modes

### Skip

User determines no action needed. Nothing added to design. Move to next lens.

### Skim

Present all suggestions at once, brief format:

```
1. [Quick Win] Improve trigger phrase specificity
2. [High Value] Add error recovery examples
3. [Consider] Restructure for token efficiency
```

"Questions before moving on?" Suggestions go to design as-is.

### Deep

Ask at entry: "Go deep on all N suggestions, or focus on high-impact ones?"

User specifies breadth. Present one suggestion at a time:

- Issue description
- Before/after examples
- Rationale
- Cross-cutting connections: "Also affects: validator agent's skill list"

User can reshape, challenge, or refine. Refined suggestions go to design.

## Priority Model

Suggestions use Effort × Impact matrix:

| Priority | Criteria | Action |
|----------|----------|--------|
| **Quick Win** | Low effort, any impact | Do first |
| **High Value** | High impact, any effort | Worth the investment |
| **Consider** | Low impact, high effort | May not justify cost |

## Suggestion Format

Each suggestion follows this structure:

```markdown
### [Priority] Issue title
**Lens:** Which lens identified this
**File:** path/to/file.md
**Effort:** ~X min | **Impact:** High/Medium/Low

**Issue:** What's wrong

**Before:**
[Current state]

**After:**
[Improved state]

**Rationale:** Why this matters
```

## Design Document Structure

Write to `docs/plans/YYYY-MM-DD-<plugin>-optimization.md`:

```markdown
# Plugin Optimization: <plugin-name>
Generated: YYYY-MM-DD

## Summary
[One paragraph from orientation]

## Quick Wins
[Low effort, any impact — do first]

## High Value
[Worth the investment]

## Consider
[May not justify cost]

## Cross-Cutting Notes
[Interactions, consolidated refactors, dependencies]
```

## After the Session

**Documentation:**
- Write design to `docs/plans/YYYY-MM-DD-<plugin>-optimization.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create implementation plan

## Key Principles

- **Fixed lens order** — Predictable, learnable flow
- **User controls depth** — Skip/Skim/Deep per lens
- **Auto-advance clean lenses** — Maintain momentum
- **Flag cross-cutting** — Surface interactions during Deep mode
- **Synthesize at end** — Catch emergent patterns
- **Separate analysis from implementation** — Design document first
```

**Step 2: Verify file created**

Run: `cat plugins/plugin-dev/skills/optimizing-plugins/SKILL.md | head -20`
Expected: Frontmatter with name and description visible

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/optimizing-plugins/SKILL.md
git commit -m "feat(plugin-dev): add optimizing-plugins skill"
```

---

## Task 4: Create the Lenses Reference

**Files:**
- Create: `plugins/plugin-dev/skills/optimizing-plugins/references/lenses.md`

**Step 1: Write the lenses reference file**

```markdown
# Optimization Lenses Reference

Detailed criteria for each of the 6 analytical lenses used by the plugin optimizer.

## Lens 1: Trigger Fidelity

**Core question:** Will Claude invoke this skill/command at the right moment?

### What to Check

**Skill descriptions:**
- Uses third-person format ("This skill..." not "Use this skill...")
- Contains specific trigger phrases in quotes
- Includes action verbs matching user vocabulary
- Specifies when NOT to use (if ambiguous with other skills)
- Length: 50-200 words optimal

**Trigger phrase quality:**
- Concrete nouns: "bugs", "tests", "API", "database"
- Action verbs: "debug", "fix", "create", "analyze"
- Context phrases: "before committing", "when stuck", "after writing"

**Red flags:**
- Vague words: "help", "assist", "general", "various"
- Missing action context: when in workflow?
- Overlapping triggers with other skills

### Evaluation Questions

1. Would a user naturally say words that match this description?
2. Does Claude have enough context to know when to invoke?
3. Are there false-positive triggers that would cause wrong invocation?

### Example Improvements

**Before:** "Use for debugging problems"
**After:** "Use when encountering bugs, test failures, or unexpected behavior — before proposing fixes"

**Before:** "Helps with code review"
**After:** "Reviews code for bugs, security issues, and style violations. Use after completing a feature or before creating a pull request."

---

## Lens 2: Token Economy

**Core question:** Does every token earn its keep?

### What to Check

**File sizes:**
- SKILL.md under 500 lines (optimal: 200-400)
- Reference files used for detailed content
- No redundant information across files

**Progressive disclosure:**
- Essential info in SKILL.md
- Detailed criteria in references/
- Scripts for deterministic operations

**Content efficiency:**
- No verbose explanations of obvious things
- Tables instead of paragraphs where appropriate
- Examples are minimal but sufficient

### Evaluation Questions

1. Could this be shorter without losing clarity?
2. Is detailed content properly delegated to references?
3. Are there redundant sections saying the same thing?

### Example Improvements

**Before:** Long paragraph explaining when to use each option
**After:** Decision table with criteria and recommendations

**Before:** Inline code examples repeated in multiple places
**After:** Single reference file with examples, linked from SKILL.md

---

## Lens 3: Structural Clarity

**Core question:** Can Claude navigate and understand efficiently?

### What to Check

**Navigation:**
- Clear section headings
- Table of contents for files >100 lines
- Logical flow from overview to details

**Reference depth:**
- One level deep (SKILL.md → references/)
- No chains: A → B → C
- Clear what lives where

**Consistency:**
- Same heading style throughout
- Consistent formatting patterns
- Predictable structure across similar components

### Evaluation Questions

1. Can Claude find specific information quickly?
2. Is the document structure self-explanatory?
3. Would a new reader understand the organization?

### Example Improvements

**Before:** Mixed heading levels, inconsistent formatting
**After:** H2 for major sections, H3 for subsections, consistent patterns

**Before:** Important details buried in paragraphs
**After:** Key information in bullet points or tables at section start

---

## Lens 4: Degrees of Freedom

**Core question:** Does specificity match task fragility?

### What to Check

**Task fragility assessment:**
- Fragile tasks (security, data integrity): Need rigid instructions
- Creative tasks (design, exploration): Need flexible guidance
- Mixed tasks: Clear which parts are rigid vs flexible

**Instruction specificity:**
- Rigid: Exact steps, exact commands, exact formats
- Flexible: Principles, options, guidelines

**Decision points:**
- Are choices explicit or implicit?
- Does Claude know when to ask vs decide?

### Evaluation Questions

1. For fragile operations: Are instructions precise enough to prevent mistakes?
2. For creative tasks: Is there room for Claude to adapt?
3. Are the boundaries between rigid and flexible clear?

### Example Improvements

**Before:** "Validate the input before processing"
**After:** "Validate input using schema at `schemas/input.json`. Reject with specific error if: missing required fields, invalid types, values out of range."

**Before:** Rigid steps for exploratory task
**After:** "Explore the codebase to understand X. Consider: [list of approaches]. Choose based on what you find."

---

## Lens 5: Resilience

**Core question:** What happens when things go wrong?

### What to Check

**Error handling:**
- Are failure modes documented?
- What should Claude do when X fails?
- Are there recovery paths?

**Hooks:**
- Do hooks handle errors gracefully?
- Is stderr captured and reported?
- Non-zero exit codes handled?

**Agents:**
- What if the agent can't complete?
- Are there explicit failure instructions?
- Timeout handling?

**MCP:**
- Server connection failures?
- Malformed responses?
- Authentication errors?

### Evaluation Questions

1. What happens if the primary approach fails?
2. Are error messages actionable?
3. Is there a graceful degradation path?

### Example Improvements

**Before:** "Run the validation script"
**After:** "Run validation script. If it fails: check error message, report to user with suggested fix, offer to proceed with manual validation."

**Before:** No error handling in hook
**After:** Hook returns structured error with actionable message

---

## Lens 6: Plugin Coherence

**Core question:** Does this work as a unified whole?

### What to Check

**Naming conventions:**
- Consistent naming across skills, commands, agents
- Names reflect function
- No confusing overlaps

**Component boundaries:**
- Each component has clear responsibility
- No overlapping functionality
- Dependencies are explicit

**Handoffs:**
- How do components work together?
- Are transitions documented?
- Is the user journey clear?

**Documentation:**
- README reflects actual capabilities
- No orphaned or undocumented components
- Examples show realistic usage

### Evaluation Questions

1. Does the plugin feel like one cohesive tool?
2. Would a new user understand what each part does?
3. Are component relationships clear?

### Example Improvements

**Before:** Skills with overlapping triggers, unclear which to use
**After:** Clear differentiation in descriptions, explicit "use X when... use Y when..."

**Before:** Command invokes skill but relationship undocumented
**After:** Command docs explain delegation, skill docs reference command

---

## Cross-Cutting Patterns

When analyzing, watch for these cross-lens issues:

**Description ↔ Implementation mismatch:**
- Description promises X but instructions do Y
- Triggers don't match actual capability

**Redundancy across components:**
- Same instructions in multiple skills
- Duplicate error handling logic

**Missing integration:**
- Components that should reference each other don't
- No guidance on combined usage

**Inconsistent quality:**
- Some skills polished, others rough
- Uneven documentation depth
```

**Step 2: Verify file created**

Run: `wc -l plugins/plugin-dev/skills/optimizing-plugins/references/lenses.md`
Expected: ~250-300 lines

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/optimizing-plugins/references/lenses.md
git commit -m "feat(plugin-dev): add lenses reference for optimizer"
```

---

## Task 5: Update plugin-dev Manifest

**Files:**
- Modify: `plugins/plugin-dev/.claude-plugin/plugin.json`

**Step 1: Read current manifest**

Run: `cat plugins/plugin-dev/.claude-plugin/plugin.json`

**Step 2: Verify skills directory is referenced**

The manifest should already reference `./skills/` since other skills exist. Verify no changes needed.

If skills not referenced, add:
```json
"skills": "./skills/"
```

**Step 3: Commit if changed**

```bash
git add plugins/plugin-dev/.claude-plugin/plugin.json
git commit -m "chore(plugin-dev): update manifest for optimizer skill"
```

---

## Task 6: Test the Command

**Step 1: Verify command loads**

From the worktree, check if the command file is syntactically correct:

```bash
head -20 plugins/plugin-dev/commands/optimize.md
```

Expected: Valid YAML frontmatter with description and allowed-tools

**Step 2: Verify skill loads**

```bash
head -20 plugins/plugin-dev/skills/optimizing-plugins/SKILL.md
```

Expected: Valid YAML frontmatter with name and description

**Step 3: Verify references accessible**

```bash
ls -la plugins/plugin-dev/skills/optimizing-plugins/references/
```

Expected: lenses.md present

---

## Task 7: Final Commit and Branch Status

**Step 1: Check status**

```bash
git status
git log --oneline -5
```

Expected: All files committed, clean working directory

**Step 2: Summary of commits**

Should have approximately:
1. `feat(plugin-dev): add optimize command`
2. `feat(plugin-dev): add optimizing-plugins skill`
3. `feat(plugin-dev): add lenses reference for optimizer`

---

## Completion Checklist

- [ ] `plugins/plugin-dev/commands/optimize.md` created with frontmatter
- [ ] `plugins/plugin-dev/skills/optimizing-plugins/SKILL.md` created with session flow
- [ ] `plugins/plugin-dev/skills/optimizing-plugins/references/lenses.md` created with 6 lenses
- [ ] All files committed to `feat/plugin-optimizer` branch
- [ ] No uncommitted changes
