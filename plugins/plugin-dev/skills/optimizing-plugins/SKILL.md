---
name: optimizing-plugins
description: "Guides systematic plugin improvement from 'good' to 'great' using 6 analytical lenses. Use after audit passes, when plugin works but feels rough, triggers aren't firing reliably, skills overlap confusingly, or when asked to optimize plugin, improve plugin quality, refine descriptions."
license: MIT
metadata:
  version: 1.0.0
  model: claude-opus-4-5-20251101
  domains: [plugin-development, optimization, quality]
  type: process
---

# Plugin Optimizer

Guides systematic plugin improvement through collaborative dialogue, examining plugins through 6 lenses and producing a prioritized optimization design.

**Announce at start:** "I'm using the optimizing-plugins skill to systematically improve this plugin."

## Overview

The optimizer examines plugins through six analytical lenses, producing a prioritized design document. It guides improvement from "good" to "great" — distinct from audit, which fixes broken plugins.

**Relationship to audit:**

- **Audit** finds problems — "broken to working"
- **Optimizer** improves quality — "good to great"

## Triggers

- `optimize plugin` - After audit passes, improve quality
- `improve plugin quality` - Refine descriptions and structure
- `plugin feels rough` - Works but needs polish
- `triggers aren't firing` - Skills not activating reliably
- `skills overlap confusingly` - Unclear boundaries between skills

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

| #   | Lens               | Core Question                                   |
| --- | ------------------ | ----------------------------------------------- |
| 1   | Trigger Fidelity   | Will Claude invoke this at the right moment?    |
| 2   | Token Economy      | Does every token earn its keep?                 |
| 3   | Structural Clarity | Can Claude navigate and understand efficiently? |
| 4   | Degrees of Freedom | Does specificity match task fragility?          |
| 5   | Resilience         | What happens when things go wrong?              |
| 6   | Plugin Coherence   | Does this work as a unified whole?              |

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

| Priority       | Criteria                | Action               |
| -------------- | ----------------------- | -------------------- |
| **Quick Win**  | Low effort, any impact  | Do first             |
| **High Value** | High impact, any effort | Worth the investment |
| **Consider**   | Low impact, high effort | May not justify cost |

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
- Use elements-of-style:writing-clearly-and-concisely skill
- Commit the design document to git

**Implementation (if continuing):**

- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create implementation plan

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Skipping orientation | Loses shared context, suggestions feel arbitrary | Always deliver orientation paragraph first |
| Deep-diving every lens | Exhausts user, diminishes focus | Let user choose depth per lens |
| Mixing analysis with implementation | Scope creep, incomplete analysis | Complete design document before any code changes |
| Treating all suggestions equally | Wastes effort on low-impact items | Use Quick Win / High Value / Consider prioritization |
| Ignoring cross-cutting concerns | Suggestions conflict or duplicate effort | Flag interactions during Deep mode, synthesize at end |

## Verification

After optimization session:

- [ ] Orientation paragraph delivered and grounded conversation
- [ ] All 6 lenses examined (skip/skim/deep choices made)
- [ ] Cross-cutting concerns identified during synthesis
- [ ] Design document written to `docs/plans/YYYY-MM-DD-<plugin>-optimization.md`
- [ ] Suggestions categorized by priority (Quick Win / High Value / Consider)
- [ ] User confirmed next steps (implement or defer)

## Extension Points

1. **Custom Lenses:** Add domain-specific lenses (e.g., "Security Lens" for auth plugins)
2. **Automated Pre-scan:** Script to identify obvious issues before human tour begins
3. **Optimization Templates:** Pre-built suggestion formats for common issues
4. **Integration with Audit:** Chain audit → optimize workflow with shared context

## Key Principles

- **Fixed lens order** — Predictable, learnable flow
- **User controls depth** — Skip/Skim/Deep per lens
- **Auto-advance clean lenses** — Maintain momentum
- **Flag cross-cutting** — Surface interactions during Deep mode
- **Synthesize at end** — Catch emergent patterns
- **Separate analysis from implementation** — Design document first
