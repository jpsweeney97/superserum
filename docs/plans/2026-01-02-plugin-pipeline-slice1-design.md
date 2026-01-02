# Plugin Development Pipeline - Slice 1 Design

## Overview

Comprehensive refactor of plugin-dev skills to create a clear, staged pipeline for plugin development.

**Approach:** Vertical slices — complete the full pipeline for skills first, then add component types.

**This document:** Slice 1 (Skills Pipeline) design specification.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ TRIAGE: brainstorming-plugins                            │
│                                                          │
│ Output: Component list (e.g., "Skill + Hook")            │
│ Handoff: "Use brainstorming-{type} for each component"  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ DESIGN: brainstorming-skills                             │
│ Light: Collaborative dialogue                            │
│ Deep: → skillforge                                       │
│                                                          │
│ Output: Design document                                  │
│ Handoff: "Use implementing-skills to build it"          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: implementing-skills                           │
│ TDD workflow (reference: skill-development)              │
│                                                          │
│ Output: Working, tested skill                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                ┌────────────────────┐
                │ What's next?       │
                └────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────────┐
         │               │               │                 │
         ▼               ▼               ▼                 ▼
   ┌───────────┐  ┌─────────────┐  ┌──────────┐    ┌──────────┐
   │ More      │  │ Polish      │  │ Publish  │    │ Personal │
   │ components│  │ (recommend) │  │ (skip    │    │ use only │
   │           │  │             │  │ polish)  │    │          │
   └───────────┘  └─────────────┘  └──────────┘    └──────────┘
         │               │               │                 │
         │               ▼               │                 │
         │  ┌─────────────────────────┐  │                 │
         │  │ OPTIMIZE:               │  │                 │
         │  │ optimizing-plugins      │  │                 │
         │  │                         │  │                 │
         │  │ 6 lenses, validation    │  │                 │
         │  │ panel                   │  │                 │
         │  └─────────────────────────┘  │                 │
         │               │               │                 │
         │               ▼               │                 │
         │  ┌─────────────────────────┐  │                 │
         │  │ DEPLOY:                 │◄─┘                 │
         │  │ deploying-plugins       │                    │
         │  │                         │                    │
         │  │ Packaging, docs,        │                    │
         │  │ versioning, marketplace │                    │
         │  └─────────────────────────┘                    │
         │               │                                 │
         ▼               ▼                                 ▼
┌─────────────┐  ┌─────────────┐                   ┌─────────────┐
│ Loop back   │  │ Published   │                   │ Done        │
│ to DESIGN   │  │ plugin      │                   │ (active in  │
│ for next    │  │             │                   │ ~/.claude/) │
│ component   │  │             │                   │             │
└─────────────┘  └─────────────┘                   └─────────────┘
```

### Stages & Artifacts

| Stage | Skill | Output Artifact |
|-------|-------|-----------------|
| **Triage** | brainstorming-plugins | Component list with rationale |
| **Design** | brainstorming-{component} | Design doc: `docs/plans/YYYY-MM-DD-<name>-design.md` |
| **Implement** | implementing-{component} | Working component + passing tests |
| **Optimize** | optimizing-plugins | Optimization doc + improvements |
| **Deploy** | deploying-plugins | Published plugin |

### If a Stage Fails

| Stage | Failure Signal | Resolution |
|-------|----------------|------------|
| Triage | Can't determine components | Ask more questions; user clarifies problem |
| Design | Design doesn't converge | Escalate to skillforge for deep analysis |
| Design | Scope too broad | Apply YAGNI; split into multiple components |
| Implement | Tests don't pass | Iterate RED-GREEN-REFACTOR; don't skip phases |
| Implement | Design was wrong | Return to brainstorming-{component} |
| Optimize | Validation panel rejects | Address feedback; re-run affected lenses |
| Deploy | Packaging fails | Fix issues per error messages; re-validate |

---

## Slice 1 Deliverables

| Skill | Action | Status |
|-------|--------|--------|
| brainstorming-plugins | Slim to triage + add Pipeline Overview | Designed |
| brainstorming-skills | Create new | Designed |
| implementing-skills | Rename from writing-skills + updates | Designed |
| optimizing-plugins | Add Prerequisites/Handoff | Designed |
| deploying-plugins | Create new | Designed |

---

## Skill Designs

### 1. brainstorming-plugins (Slimmed to Triage)

```markdown
---
name: brainstorming-plugins
description: Use when starting plugin development, "build a plugin",
  "create a plugin for X", or unsure which components are needed.
---

# Plugin Component Triage

## Overview
Identify which components your plugin needs, then hand off to
component-specific design skills.

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
None — this is the entry point.

## The Process

### 1. Understand the Problem
Ask one question at a time:
- What problem does this solve?
- Who uses it? (User explicitly? Claude automatically? Both?)
- When should it activate? (Explicit command? Automatic trigger? Event-driven?)

### 2. Distribution & Scope
Before selecting components, understand the context:
- Who uses this? (Personal, team, community?)
- Installation scope: user, project, or managed?
- Does it need marketplace distribution?

This affects complexity decisions — a personal tool can be simpler.

### 3. Component Selection
Use decision matrix:

| Need | Component | Why |
|------|-----------|-----|
| "Claude needs knowledge about X" | Skill | On-demand guidance |
| "User runs action X explicitly" | Command | User-initiated action |
| "Delegate complex work" | Agent | Isolated execution |
| "X must ALWAYS happen on event Y" | Hook | Guaranteed automation |

Present your recommendation with rationale for each component.

### 4. Simplicity Check (YAGNI)
Before confirming:
- What's the minimum that solves the problem?
- Can one component type handle it, or are multiple truly needed?
- What can we remove and still succeed?

Challenge your own recommendations. Simpler is better.

### 5. Confirm & Handoff
Present final recommendation: "For this plugin, I recommend:
- Skill for [reason]
- Hook for [reason]"

Get user confirmation before handoff.

## Next Step

Run the command for your first component:

| Component | Command |
|-----------|---------|
| Skill | `/brainstorming-skills` |
| Hook | `/brainstorming-hooks` |
| Agent | `/brainstorming-agents` |
| Command | `/brainstorming-commands` |

Copy-paste the command above to continue.

## Pipeline Overview

This skill is the entry point to the plugin development pipeline.

### Stages & Artifacts

| Stage | Skill | Output Artifact |
|-------|-------|-----------------|
| **Triage** | brainstorming-plugins | Component list with rationale |
| **Design** | brainstorming-{component} | Design doc: `docs/plans/YYYY-MM-DD-<name>-design.md` |
| **Implement** | implementing-{component} | Working component + passing tests |
| **Optimize** | optimizing-plugins | Optimization doc + improvements |
| **Deploy** | deploying-plugins | Published plugin |

### Data Flow

```
Component List        Design Document         Working Plugin
    │                      │                       │
    ▼                      ▼                       ▼
┌────────┐  list    ┌────────────┐  doc    ┌──────────────┐
│ Triage │ ──────►  │   Design   │ ──────► │  Implement   │
└────────┘          └────────────┘         └──────────────┘
                                                   │
                    ┌──────────────────────────────┘
                    │ working plugin
                    ▼
             ┌────────────┐  optimized    ┌────────────┐
             │  Optimize  │ ────────────► │   Deploy   │
             └────────────┘               └────────────┘
```

### If a Stage Fails

| Stage | Failure Signal | Resolution |
|-------|----------------|------------|
| Triage | Can't determine components | Ask more questions; user clarifies problem |
| Design | Design doesn't converge | Escalate to skillforge for deep analysis |
| Design | Scope too broad | Apply YAGNI; split into multiple components |
| Implement | Tests don't pass | Iterate RED-GREEN-REFACTOR; don't skip phases |
| Implement | Design was wrong | Return to brainstorming-{component} |
| Optimize | Validation panel rejects | Address feedback; re-run affected lenses |
| Deploy | Packaging fails | Fix issues per error messages; re-validate |

### Entry Points

Users can enter at any stage:

| Starting Point | Prerequisites | First Skill |
|----------------|---------------|-------------|
| "I have an idea" | None | brainstorming-plugins (here) |
| "I know I need a skill" | Component decision made | brainstorming-skills |
| "I have a design" | Design document exists | implementing-skills |
| "I have a working plugin" | Plugin functional | optimizing-plugins |
| "I want to publish" | Plugin ready | deploying-plugins |

## Key Principles
- One question at a time
- Prefer multiple choice when possible
- Explain WHY each component (not just what)
- YAGNI ruthlessly — challenge every component
- User confirms before handoff

## What This Skill Does NOT Do
- Detailed component design (→ brainstorming-{component})
- Implementation guidance (→ implementing-{component})
```

---

### 2. brainstorming-skills (New)

```markdown
---
name: brainstorming-skills
description: Use when designing a new skill, "design a skill for X",
  "what should this skill contain", "skill scope", "skill triggers",
  or after brainstorming-plugins identifies a skill is needed.
  Light collaborative design or handoff to skillforge for deep analysis.
license: MIT
metadata:
  version: 1.0.0
  domains: [plugin-development, skill-design, brainstorming]
  type: process
---

# Skill Design

Turn skill ideas into design documents through collaborative dialogue.

## Quick Start

```
User: "I need a skill for X"
Claude: Assesses complexity → Light path or → skillforge

Light path:
1. Core purpose (2-3 questions)
2. Trigger design (3-5 phrases)
3. Knowledge scope (in/out boundaries)
4. Structure decisions (SKILL.md, references, scripts)
5. Composition check (related skills)
6. Present design in sections, validate each
7. Write design document → handoff to implementing-skills
```

## Triggers

- `design a skill for {purpose}`
- `what should this skill contain`
- `skill scope` / `skill boundaries`
- `skill triggers` / `when should this skill activate`
- `brainstorm a skill` (after triage)

## Prerequisites

| Prerequisite | Source |
|--------------|--------|
| Know you need a skill | brainstorming-plugins or direct knowledge |
| Understand the problem | User context |

## Pipeline Context

This skill is **Stage 2: Design** in the plugin development pipeline.

See: `brainstorming-plugins` for full pipeline overview.

| Aspect | Value |
|--------|-------|
| This stage | Design skill from requirements |
| Prerequisite | `/brainstorming-plugins` (or direct request) |
| Hands off to | `/implementing-skills` |

## Quick Reference

| Design Area | Key Question | Output |
|-------------|--------------|--------|
| Purpose | What can Claude NOT do without this? | 1-2 sentence statement |
| Triggers | What phrases activate it? | 3-5 distinct phrases |
| Scope | What's in AND out? | Boundary list |
| Structure | What goes where? | SKILL.md outline + reference/script needs |
| Composition | How does it fit the ecosystem? | Related skills, conflicts |

## Routing Decision

**Default:** Use skillforge methodology (deep path)

**Light path only if ALL conditions met:**
- [ ] Scope is obvious (can state in one sentence)
- [ ] No coordination with other skills
- [ ] No failure modes that need explicit handling
- [ ] Similar skill exists as template

If uncertain about ANY condition, use skillforge.

**Announce decision:** "Using [light/skillforge] because [reason]."

## The Process

### Step 1 of 6: Core Purpose

Ask one question at a time:
- What specific knowledge does this skill provide?
- What can Claude NOT do well without this skill?
- Who benefits? (Claude operating better? User getting guidance? Both?)

**Output:** 1-2 sentence purpose statement

### Step 2 of 6: Trigger Design

---
Progress: █░░░░░ 1/6 complete | Next: Trigger Design
---

| Aspect | Questions |
|--------|-----------|
| Activation | What phrases should trigger this skill? |
| Symptoms | What problems indicate this skill is needed? |
| Boundaries | What should NOT trigger it? |

**Target:** 3-5 distinct trigger phrases covering different phrasings of same need.

**Quality check:** Would Claude find this skill when needed? Test mentally
against likely user queries.

### Step 3 of 6: Knowledge Scope

---
Progress: ██░░░░ 2/6 complete | Next: Knowledge Scope
---

| Boundary | Define Explicitly |
|----------|-------------------|
| IN scope | What this skill covers (be specific) |
| OUT of scope | What this skill does NOT cover (equally important) |
| Adjacent | Related skills that handle nearby concerns |

**Why out-of-scope matters:** Unbounded skills bloat and become unfocused.
Explicit boundaries prevent scope creep.

### Step 4 of 6: Structure Decisions

---
Progress: ███░░░ 3/6 complete | Next: Structure Decisions
---

| Component | Decision | Size Target |
|-----------|----------|-------------|
| SKILL.md body | Core workflow, must be self-sufficient | 1,500-2,000 words |
| references/ | Deep docs loaded on demand | Unlimited |
| scripts/ | Deterministic/repeated operations | As needed |
| examples/ | Working code to copy/adapt | As needed |

**Key principle:** SKILL.md must be self-sufficient for executing the skill.
References answer "tell me more about X," not "what's the next step."

### Step 5 of 6: Composition

---
Progress: ████░░ 4/6 complete | Next: Composition
---

- What skills might be used alongside this one?
- Does this skill depend on or reference others?
- Any overlap or conflict with existing skills?

**Check existing skills:** Search for similar triggers before finalizing.

### Step 6 of 6: Present Design

---
Progress: █████░ 5/6 complete | Next: Present Design
---

Present in 200-300 word sections:
1. **Purpose & Triggers** — What it does, how it activates
2. **Scope** — In/out boundaries
3. **Structure** — SKILL.md outline, references, scripts
4. **Composition** — Related skills, dependencies

After each section: "Does this look right so far?"

Be ready to revise based on feedback.

## Output

Write validated design to: `docs/plans/YYYY-MM-DD-<skill-name>-design.md`

**Use template:** `references/design-template.md`

**Design document includes:**
- Purpose statement
- Trigger phrases (3-5)
- Scope boundaries (in/out)
- SKILL.md outline
- Reference/script/example needs
- Composition notes
- Open questions (if any)

## Next Step

Run this command to continue:

```
/implementing-skills docs/plans/[your-design-file].md
```

Replace `[your-design-file]` with the actual design document path.

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Skipping scope boundaries | Leads to bloated, unfocused skills | Define OUT as carefully as IN |
| Generic triggers | Skill won't activate when needed | 3-5 specific, varied phrases |
| SKILL.md depends on references | User can't execute without loading more | SKILL.md self-sufficient |
| Designing in isolation | May duplicate existing skills | Check ecosystem early |
| Deep-diving simple skills | Over-engineering wastes effort | Assess complexity first |
| Skipping composition check | Causes conflicts and confusion | Identify related skills |

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

## Key Principles

- **One question at a time** — Don't overwhelm
- **Boundaries matter** — OUT of scope prevents bloat
- **Triggers determine discoverability** — Test them mentally
- **Self-sufficient SKILL.md** — References add depth, not steps
- **Check the ecosystem** — Avoid duplicates and conflicts
- **Validate incrementally** — Present in sections, confirm each
- **Right-size the depth** — Simple skills don't need skillforge

## References

- skill-development — Structural reference (file format, directories)
- skillforge — Deep analysis for complex skills
- implementing-skills — TDD implementation workflow

```

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

---

### 3. implementing-skills (Renamed from writing-skills)

```markdown
---
name: implementing-skills
description: Use when building a skill from a design, "implement this skill",
  "write the skill", "TDD for skills", "pressure testing skills", or
  "validating skill effectiveness". For structure reference, see skill-development.
  For deep creation methodology, see skillforge.
license: MIT
metadata:
  version: 2.0.0
  domains: [plugin-development, skill-implementation, tdd]
  type: process
---

# Implementing Skills

Build skills using test-driven development: write failing tests first,
then write the skill to pass them.

## Quick Start

```
Design document exists (from brainstorming-skills or equivalent)

1. RED: Create pressure scenarios, run WITHOUT skill, document baseline
2. GREEN: Write minimal skill addressing baseline failures
3. REFACTOR: Find new rationalizations, close loopholes, re-test

Output: Working, tested skill
Handoff: optimizing-plugins (polish) or deploying-plugins (publish)
```

## Triggers

- `implement this skill`
- `write the skill`
- `build the skill from design`
- `TDD for skills`
- `pressure testing skills`
- `validating skill effectiveness`

## Prerequisites

| Prerequisite | Source |
|--------------|--------|
| Skill design (purpose, triggers, scope) | brainstorming-skills or equivalent |
| Structural knowledge | skill-development (reference) |

**No design?** Use brainstorming-skills first, or proceed with clear
mental model of what you're building.

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

This skill is **Stage 3: Implement** in the plugin development pipeline.

See: `brainstorming-plugins` for full pipeline overview.

| Aspect | Value |
|--------|-------|
| This stage | Build skill from design using TDD |
| Prerequisite | `/brainstorming-skills` (design document) |
| Hands off to | `/optimizing-plugins` or `/deploying-plugins` |

## Quick Reference

| Phase | Action | Output |
|-------|--------|--------|
| RED | Test without skill, document failures | Baseline behavior |
| GREEN | Write minimal skill | Passing tests |
| REFACTOR | Close loopholes | Bulletproof skill |

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills.

Write skill before testing? Delete it. Start over.

**No exceptions:** Not for "simple additions," "just adding a section,"
or "documentation updates."

**Why this matters:** If you didn't watch an agent fail without the skill,
you don't know if the skill teaches the right thing.

## The Process

### Step 1 of 3: RED — Write Failing Test (Baseline)

Run pressure scenario with subagent WITHOUT the skill:

1. Create scenario combining multiple pressures (time, sunk cost, authority)
2. Run subagent against scenario
3. Document:
   - What choices did they make?
   - What rationalizations did they use (verbatim)?
   - Which pressures triggered violations?

**This is "watch the test fail"** — see what agents naturally do
before the skill exists.

**Why verbatim?** Paraphrasing loses the exact language you need to counter.
Capture the rationalization word-for-word.

### Step 2 of 3: GREEN — Write Minimal Skill

---
Progress: █░░ 1/3 complete | Next: GREEN
---

Write skill addressing those specific rationalizations:

1. Address documented baseline failures
2. Don't add content for hypothetical cases
3. Follow structure from skill-development reference
4. Run same scenarios WITH skill
5. Agent should now comply

**Minimal means minimal.** Only what's needed to pass the test.

**Why minimal?** Untested content is unverified content. Add more
only when tests demand it.

### Step 3 of 3: REFACTOR — Close Loopholes

---
Progress: ██░ 2/3 complete | Next: REFACTOR
---

Agent found new rationalization? Add explicit counter:

1. Identify new rationalizations from testing
2. Add explicit counters to skill
3. Build rationalization table
4. Re-test until bulletproof

**Why iterate?** Agents are creative rationalizers. First pass rarely
catches everything.

## Skill Content Guidelines

| Aspect | Guidance |
|--------|----------|
| Examples | One excellent example beats many mediocre ones |
| Language | Use most relevant (testing→TS/JS, system→Shell/Python) |
| Cross-references | Use `**REQUIRED:** Use skill-name`, not force-loading |
| Flowcharts | ONLY for non-obvious decisions, never for reference |
| Tables | Prefer over prose for structured info |

## Testing by Skill Type

| Type | Test Approach | Success Criteria |
|------|---------------|------------------|
| Discipline (rules) | Pressure scenarios, multiple pressures combined | Agent follows rule under maximum pressure |
| Technique (how-to) | Application scenarios, edge cases | Agent applies correctly to new scenario |
| Pattern/Reference | Recognition and retrieval tests | Agent finds right information |

**Deep Dive:** See `references/bulletproofing-rationalization.md` for building explicit defenses against agent rationalization.

**Deep Dive:** See `references/pressure-scenario-design.md` for designing effective pressure scenarios.

## Output

Working skill in correct location:
- Plugin skill: `plugin-name/skills/skill-name/SKILL.md`
- Personal skill: `~/.claude/skills/skill-name/SKILL.md`

Plus any references/, scripts/, examples/ as designed.

## Next Step

Choose one and run:

| Situation | Command |
|-----------|---------|
| More components to build | `/brainstorming-{component}` |
| Plugin complete, want polish | `/optimizing-plugins path/to/plugin` |
| Ready to publish (skip polish) | `/deploying-plugins path/to/plugin` |
| Personal use only | Done — skill is active in `~/.claude/skills/` |

Copy-paste the command above to continue.

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Writing skill before test | Can't verify it teaches the right thing | RED phase first, always |
| Keeping pre-test code as "reference" | Contaminates the TDD process | Delete means delete |
| Testing only happy path | Misses rationalization vectors | Combine multiple pressures |
| Adding hypothetical cases | Bloats skill without evidence | Only address documented failures |
| Skipping refactor phase | Leaves loopholes open | Close every rationalization |
| Paraphrasing rationalizations | Loses exact language to counter | Document verbatim |

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

## Key Principles

- **Iron Law** — No skill without failing test first
- **Document verbatim** — Capture exact rationalizations, not summaries
- **Minimal GREEN** — Only what's needed to pass
- **Close every loophole** — Explicit counters for each rationalization
- **Delete means delete** — No keeping pre-test code

## References

- skill-development — Structural reference (file format, frontmatter, directories)
- brainstorming-skills — Design phase (if design needed)
- skillforge — Deep creation methodology (when TDD isn't enough)
- references/testing-skills-with-subagents.md — Pressure scenario methodology
- references/persuasion-principles.md — Psychology of rationalization resistance

<!-- NOTE: Create these reference files during implementation:
- references/bulletproofing-rationalization.md (from original Deep Dive content)
- references/pressure-scenario-design.md (from original Deep Dive content)
-->
```

---

### 4. optimizing-plugins (Additions Only)

**Add after Overview:**

```markdown
## Prerequisites

| Prerequisite | Source |
|--------------|--------|
| Working plugin (all components implemented) | implementing-{component} skills |
| Plugin passes basic functionality tests | Component-level testing |
| Audit passed (recommended) | plugin-audit |

**Single component?** This skill works for single-skill plugins too.
The 6 lenses still apply.

**Skipping straight here?** If you have a working plugin but skipped
earlier stages, that's fine. Optimization identifies issues regardless
of how the plugin was built.
```

**Replace "After the Session" with:**

```markdown
## Handoff

"Plugin optimized. What's next?

| Situation | Next Step |
|-----------|-----------|
| Ready to publish | → deploying-plugins |
| Need to implement optimization suggestions | → implementing-{component} for changes |
| Discovered design issues | → brainstorming-{component} to redesign |
| Personal use, no distribution | Done |"

## After Optimization

**If implementing suggestions:**
- Use implementing-skills / implementing-hooks / etc. for changes
- Re-run optimization after significant changes

**If publishing:**
- Use deploying-plugins for marketplace packaging
- Optimization design document serves as quality evidence
```

**Add to References:**

```markdown
- deploying-plugins — Next stage (marketplace packaging)
- implementing-skills — For implementing optimization suggestions
- brainstorming-skills — If redesign needed
```

---

### 5. deploying-plugins (New)

```markdown
---
name: deploying-plugins
description: Use when publishing a plugin, "deploy plugin", "publish to marketplace",
  "package plugin", "create README", "version my plugin", or after optimizing-plugins
  completes. Covers packaging, documentation, versioning, and distribution.
license: MIT
metadata:
  version: 1.0.0
  domains: [plugin-development, deployment, distribution]
  type: process
---

# Deploying Plugins

Package, document, and publish plugins for distribution.

## Quick Start

```
Working plugin exists (from implementing-* or optimizing-plugins)

1. Pre-flight checks (structure, tests, audit)
2. Documentation (README, CHANGELOG, CONTRIBUTING)
3. Versioning (semver, changelog entry)
4. Packaging (validate structure, test installation)
5. Distribution (marketplace submission or manual sharing)

Output: Published, installable plugin
```

## Triggers

- `deploy plugin`
- `publish to marketplace`
- `package plugin for distribution`
- `create plugin README`
- `version my plugin`
- `prepare plugin release`

## Prerequisites

| Prerequisite | Source | Required? |
|--------------|--------|-----------|
| Working plugin | implementing-{component} | Yes |
| All tests passing | Component-level testing | Yes |
| Optimization complete | optimizing-plugins | Recommended |
| Audit passing | plugin-audit | Recommended |

**Skipping optimization?** Acceptable for personal/team plugins.
For marketplace distribution, optimization is strongly recommended.

## Quick Reference

| Phase | Key Actions | Output |
|-------|-------------|--------|
| Pre-flight | Validate structure, run tests | Green checks |
| Documentation | README, CHANGELOG, CONTRIBUTING | Doc files |
| Versioning | Semver decision, changelog entry | Version bump |
| Packaging | Structure validation, install test | Distributable plugin |
| Distribution | Marketplace or manual | Published plugin |

## The Process

### 1. Pre-flight Checks

Before packaging, verify:

| Check | Command/Action | Pass Criteria |
|-------|----------------|---------------|
| Structure valid | `plugin-audit` or manual check | No errors |
| Tests pass | Run component tests | All green |
| No secrets | Check for hardcoded credentials | None found |
| Dependencies declared | Review plugin.json | All listed |

**If checks fail:** Fix issues before proceeding. Don't deploy broken plugins.

### 2. Documentation

Generate or update required docs:

#### README.md

| Section | Content |
|---------|---------|
| Title + badge | Plugin name, version |
| Description | What it does, who it's for |
| Installation | How to install (marketplace or manual) |
| Quick Start | Minimal usage example |
| Features | Component list (skills, hooks, commands, agents) |
| Configuration | Any required setup |
| Contributing | Link to CONTRIBUTING.md |
| License | License type |

#### CHANGELOG.md

```markdown
# Changelog

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release
- Feature X
- Feature Y

### Changed
- (for updates)

### Fixed
- (for bug fixes)
```

Follow [Keep a Changelog](https://keepachangelog.com/) format.

#### CONTRIBUTING.md (if accepting contributions)

| Section | Content |
|---------|---------|
| Welcome | Encourage contributions |
| Process | How to submit (issues, PRs) |
| Standards | Code style, testing requirements |
| Development | How to set up local dev |

### 3. Versioning

Use semantic versioning:

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking changes | MAJOR | 1.0.0 → 2.0.0 |
| New features (backward compatible) | MINOR | 1.0.0 → 1.1.0 |
| Bug fixes | PATCH | 1.0.0 → 1.0.1 |

**Steps:**
1. Decide version bump based on changes
2. Update version in `plugin.json`
3. Add changelog entry
4. Commit: `chore: bump version to X.Y.Z`
5. Tag: `git tag vX.Y.Z`

### 4. Packaging

Validate plugin is installable:

| Check | Purpose |
|-------|---------|
| plugin.json valid | Required fields present, JSON valid |
| All files included | Skills, hooks, commands, agents all present |
| No extraneous files | No .git, node_modules, __pycache__, etc. |
| Paths correct | All internal references resolve |

**Test installation:**
```bash
# Install from local path
claude plugins install /path/to/plugin

# Verify components load
claude --debug  # Check for plugin loading messages

# Test functionality
# Run key features, verify they work
```

### 5. Distribution

#### Marketplace (if applicable)

1. Ensure plugin meets marketplace requirements
2. Submit via marketplace process
3. Await review
4. Announce on approval

#### Manual Distribution

1. Create distributable archive or git repo
2. Document installation: `claude plugins install <url-or-path>`
3. Share with users

#### Internal/Team

1. Add to team's plugin repository
2. Document in team knowledge base
3. Notify team members

## Output

| Artifact | Location |
|----------|----------|
| README.md | Plugin root |
| CHANGELOG.md | Plugin root |
| CONTRIBUTING.md | Plugin root (optional) |
| Updated plugin.json | Plugin root (version bumped) |
| Git tag | Repository |
| Published plugin | Marketplace or distribution channel |

## Handoff

"Plugin deployed.

| Status | Next |
|--------|------|
| Published successfully | Done — monitor for issues |
| Issues found during deployment | Fix and re-deploy |
| User feedback received | Iterate: implement → optimize → deploy |"

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Deploying without tests | Users hit bugs you could have caught | Run all tests first |
| Skipping changelog | Users don't know what changed | Document every release |
| Hardcoded paths | Breaks on other systems | Use ${CLAUDE_PLUGIN_ROOT} |
| Vague README | Users can't figure out how to use it | Include quick start example |
| No version tags | Can't rollback, can't reference versions | Tag every release |
| Secrets in repo | Security breach | Use environment variables |

## Verification

Before announcing:

**Pre-flight:**
- [ ] Plugin structure valid
- [ ] All tests passing
- [ ] No hardcoded secrets
- [ ] Dependencies declared

**Documentation:**
- [ ] README has all sections
- [ ] CHANGELOG updated for this version
- [ ] Installation instructions tested

**Versioning:**
- [ ] Version bumped appropriately (semver)
- [ ] plugin.json version matches
- [ ] Git tag created

**Packaging:**
- [ ] Clean install works
- [ ] All components load
- [ ] Key features tested post-install

**Distribution:**
- [ ] Published to target channel
- [ ] Installation docs accurate
- [ ] Announcement ready (if applicable)

## Key Principles

- **Test before deploy** — Never ship untested
- **Document everything** — README, CHANGELOG, CONTRIBUTING
- **Semantic versioning** — Users depend on version meaning
- **Clean packages** — No cruft, no secrets
- **Verify installation** — Test the actual install process

## References

- optimizing-plugins — Previous stage (polish before deploy)
- plugin-audit — Validation tool
- Keep a Changelog — Changelog format standard
- Semantic Versioning — Versioning standard

```

---

## Future Slices

| Slice | Components | Status |
|-------|------------|--------|
| Slice 1 | Skills pipeline | Designed (this document) |
| Slice 2 | Hooks (brainstorming-hooks, implementing-hooks) | Not started |
| Slice 3 | Agents (brainstorming-agents, implementing-agents) | Not started |
| Slice 4 | Commands (brainstorming-commands, implementing-commands) | Not started |

---

## Implementation Notes

### File Locations

| Skill | Location |
|-------|----------|
| brainstorming-plugins | `plugin-dev/skills/brainstorming-plugins/SKILL.md` (edit) |
| brainstorming-skills | `plugin-dev/skills/brainstorming-skills/SKILL.md` (new) |
| implementing-skills | `plugin-dev/skills/implementing-skills/SKILL.md` (rename from writing-skills) |
| optimizing-plugins | `plugin-dev/skills/optimizing-plugins/SKILL.md` (edit) |
| deploying-plugins | `plugin-dev/skills/deploying-plugins/SKILL.md` (new) |

### Migration

1. Rename `writing-skills/` → `implementing-skills/`
2. Update all cross-references to `writing-skills`
3. Update any commands that reference `writing-skills`

---

## Design Decisions Log

| Decision | Rationale |
|----------|-----------|
| Vertical slices over horizontal batches | Validates architecture early, ships value fast |
| Comprehensive refactor over incremental | Clean architecture compounds; patching accumulates debt |
| Light/deep toggle in design skills | Prevents over-engineering simple skills |
| TDD stays in implementation | Testing IS implementation in TDD; can't separate |
| Pipeline overview in triage skill | Entry point is authoritative source for pipeline |
| Explicit handoff artifacts | Clear contracts between stages (from SkillForge spec template) |
| Failure handling table | Each stage knows what to do when things go wrong |
