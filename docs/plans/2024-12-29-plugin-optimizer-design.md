# Plugin Optimizer Design

An interactive skill for systematic plugin improvement through collaborative dialogue.

## Overview

The optimizer examines plugins through six analytical lenses, producing a prioritized design document. It guides improvement from "good" to "great" — distinct from audit, which fixes broken plugins.

**Invocation:** `/plugin-dev:optimize path/to/plugin`

**Output:** Optimization design at `docs/plans/YYYY-MM-DD-<plugin>-optimization.md`

## Component Structure

```
plugins/plugin-dev/
├── commands/
│   └── optimize.md              # Handles invocation, parses path
└── skills/
    └── optimizing-plugins/
        ├── SKILL.md             # Session flow, interaction modes
        └── references/
            └── lenses.md        # Detailed lens criteria
```

The command delegates to the skill. The skill contains methodology; references hold detailed criteria.

## Session Flow

### Phase 1: Orientation

Claude scans the plugin and delivers a one-paragraph assessment:

- Overall health
- Areas of strength
- Where opportunity lies

This grounds both Claude and user before the tour begins.

### Phase 2: Guided Tour

Claude walks through six lenses in fixed order:

| # | Lens | Core Question |
|---|------|---------------|
| 1 | Trigger Fidelity | Will Claude invoke this at the right moment? |
| 2 | Token Economy | Does every token earn its keep? |
| 3 | Structural Clarity | Can Claude navigate and understand efficiently? |
| 4 | Degrees of Freedom | Does specificity match task fragility? |
| 5 | Resilience | What happens when things go wrong? |
| 6 | Plugin Coherence | Does this work as a unified whole? |

At each lens, Claude presents findings. User chooses depth:

- **Skip** — No significant issues; move on
- **Skim** — Show all suggestions briefly; add to design as-is
- **Deep** — One suggestion at a time; discuss and refine together

For clean lenses, Claude acknowledges briefly and advances automatically: "Trigger Fidelity looks solid — descriptions are specific and action-oriented."

### Phase 3: Synthesis

After all lenses, Claude reviews cross-cutting concerns:

- Interactions between suggestions
- Opportunities to consolidate related changes
- Dependencies that affect implementation order

### Phase 4: Document & Handoff

Claude writes the optimization design, then asks: "Ready to set up for implementation?"

If yes:
1. `superpowers:using-git-worktrees` creates isolated workspace
2. `superpowers:writing-plans` creates implementation plan
3. Execute the plan

## Interaction Modes

### Skip

User determines no action needed. Nothing added to design. Move to next lens.

### Skim

Claude presents all suggestions at once, brief format:

```
1. [Quick Win] Improve trigger phrase specificity
2. [High Value] Add error recovery examples
3. [Consider] Restructure for token efficiency
```

User reviews. "Questions before moving on?" Suggestions go to design as-is.

### Deep

Claude asks at entry: "Go deep on all 4 suggestions, or focus on high-impact ones?"

User specifies breadth and depth. Claude presents one suggestion at a time:

- Issue description
- Before/after examples
- Rationale
- Cross-cutting connections: "Also affects: validator agent's skill list"

User can reshape, challenge, or refine each suggestion. Refined suggestions go to design.

## Priority Model

Suggestions use an Effort × Impact matrix:

| Priority | Criteria | Action |
|----------|----------|--------|
| **Quick Win** | Low effort, any impact | Do first |
| **High Value** | High impact, any effort | Worth the investment |
| **Consider** | Low impact, high effort | May not justify cost |

## Suggestion Format

Each suggestion in the design document follows this structure:

```markdown
### [Quick Win] Improve trigger phrase specificity
**Lens:** Trigger Fidelity
**File:** skills/debugging/SKILL.md
**Effort:** ~2 min | **Impact:** High

**Issue:** Description says "use for debugging" — too vague for reliable invocation.

**Before:**
description: "Use for debugging problems"

**After:**
description: "Use when encountering bugs, test failures, or unexpected behavior — before proposing fixes"

**Rationale:** Specific trigger phrases ("bugs", "test failures", "unexpected behavior") match user vocabulary. The action clause ("before proposing fixes") clarifies position in workflow.
```

## Design Document Structure

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
[Interactions, consolidated refactors, implementation dependencies]
```

## SKILL.md Structure

```yaml
---
name: optimizing-plugins
description: Systematically improves Claude Code plugins through 6 analytical
  lenses. Use after audit confirms no broken issues, when asked to optimize,
  improve, or enhance a plugin, or when refining trigger phrases, token
  efficiency, or structural clarity.
---

# Plugin Optimizer

## Overview
[Purpose, relationship to audit]

## The Process

### Phase 1: Orientation
[Quick scan, overall assessment]

### Phase 2: Guided Tour
[6 lenses in order, Skip/Skim/Deep interaction]

See [references/lenses.md](references/lenses.md) for detailed lens criteria.

### Phase 3: Synthesis
[Cross-cutting review, consolidation]

### Phase 4: Document & Handoff
[Write design, offer implementation]

## Interaction Modes
[Skip/Skim/Deep patterns with examples]

## After the Session

**Documentation:**
- Write design to `docs/plans/YYYY-MM-DD-<plugin>-optimization.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create implementation plan
```

## The Six Lenses

Detailed criteria live in `references/lenses.md`. Summary:

### 1. Trigger Fidelity
- Description specificity and trigger phrases
- Keyword coverage matching user vocabulary
- Clear invocation conditions

### 2. Token Economy
- SKILL.md under 500 lines
- Progressive disclosure via references
- No redundant content

### 3. Structural Clarity
- Table of contents for files over 100 lines
- One level deep for references
- Clear navigation paths

### 4. Degrees of Freedom
- High freedom for flexible tasks
- Low freedom for fragile operations
- Matched to task characteristics

### 5. Resilience
- Hook error handling
- Agent failure modes
- MCP server recovery

### 6. Plugin Coherence
- Consistent naming conventions
- Clear component boundaries
- Smooth handoffs between components

## Cross-Cutting Awareness

Throughout Deep mode, Claude flags when a suggestion affects other components:

> "This trigger phrase change also applies to your `validator` agent's skill list."

After all lenses, the synthesis pass catches emergent patterns — synergies and conflicts that appear only after examining the whole plugin.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Session model | Guided tour | Ensures comprehensive coverage |
| Lens order | Fixed | Predictable, learnable flow |
| Interaction | Skip/Skim/Deep | User controls depth per lens |
| Clean lens handling | Auto-advance | Maintains momentum |
| Output | Design document | Separates analysis from implementation |
| Priority model | Effort × Impact | Quick wins first, clear decision criteria |
| Cross-cutting | Flag + synthesize | Catches both immediate and emergent interactions |

## Implementation Notes

1. Command parses path, validates plugin exists, delegates to skill
2. Skill orientation reads plugin structure, samples key files
3. Each lens applies specific criteria from `references/lenses.md`
4. Design document uses elements-of-style for clarity
5. Handoff follows brainstorming pattern: worktrees → writing-plans
