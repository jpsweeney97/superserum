# Agents Pipeline (Slice 3) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create brainstorming-agents and implementing-agents skills to complete Slice 3 of the plugin development pipeline.

**Architecture:** Two workflow skills following the pattern established in Slice 1 (Skills) and Slice 2 (Hooks). brainstorming-agents guides design using the official 6-step process from agent-creation-system-prompt.md; implementing-agents guides validation using triggering-first TDD derived from agent-development skill ordering.

**Tech Stack:** Markdown skills with YAML frontmatter. No scripts or external dependencies.

---

## Key References

Before implementing, familiarize yourself with these files:

| File | Purpose |
|------|---------|
| `plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md` | Official 6-step agent creation process |
| `plugins/plugin-dev/skills/agent-development/references/triggering-examples.md` | Example crafting guide + failure modes |
| `plugins/plugin-dev/skills/brainstorming-skills/SKILL.md` | Pattern to follow for brainstorming skill |
| `plugins/plugin-dev/skills/implementing-skills/SKILL.md` | Pattern to follow for implementing skill |

---

## Task 1: Create brainstorming-agents SKILL.md

**Files:**
- Replace: `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md`

**Step 1: Read the existing stub**

```bash
cat plugins/plugin-dev/skills/brainstorming-agents/SKILL.md
```

Expected: "[COMING SOON]" placeholder content.

**Step 2: Write the complete skill**

Replace the file with:

```markdown
---
name: brainstorming-agents
description: Use when designing a new agent, "design an agent for X",
  "what should this agent do", "agent delegation", "agent persona",
  or after brainstorming-plugins identifies an agent is needed.
  Guides collaborative agent design through 6-step process.
---

# Agent Design

Turn agent ideas into design documents through collaborative dialogue.

## Quick Start

```
User: "I need an agent for X"
Claude: Uses 6-step process (from official agent-creation-system-prompt.md)

1. Extract Core Intent — What task is complex enough to delegate?
2. Design Expert Persona — What specialist would you hire?
3. Architect Comprehensive Instructions — What process should they follow?
4. Optimize for Performance — What quality checks and fallbacks?
5. Create Identifier — What's a clear, memorable name?
6. Define Triggering Examples — When exactly should Claude delegate?
```

## Triggers

- `design an agent for {purpose}`
- `what should this agent do`
- `agent delegation` / `when to delegate`
- `agent persona` / `expert identity`
- `brainstorm an agent` (after triage)

## Prerequisites

Before using this skill, you should:
- Know you need an agent (from `/brainstorming-plugins` or direct knowledge)
- Understand the task you want to delegate

No design document? This skill creates one.

## Pipeline Context

This skill is **Stage 2: Design** in the agent development pipeline.

| Aspect | Value |
|--------|-------|
| This stage | Design agent from requirements |
| Previous | `/brainstorming-plugins` (or direct request) |
| Next | `/implementing-agents` |

## Core Principle

> Description with examples is the most critical field. If Claude doesn't know when to delegate, the system prompt doesn't matter.

System prompts only run AFTER Claude decides to delegate. Beautiful system prompt + bad triggering = agent never used.

## Two-Phase Framing

| Phase | Question | Why |
|-------|----------|-----|
| **Delegation** | What complex work should Claude hand off? | Agents handle tasks too complex for inline execution |
| **Persona** | What specialist handles this work? | Expert identity guides agent behavior |

## The 6-Step Workflow

### Step 1 of 6: Extract Core Intent

**Ask one question at a time:**

- What specific task is complex enough to warrant delegation?
- Why can't Claude handle this inline in the main conversation?
- What are the success criteria for this task?

**Output:** Clear delegation rationale (1-2 sentences)

Example: "This agent handles PR code review, which requires reading multiple files, checking against project conventions, and producing structured feedback—too much for inline execution."

### Step 2 of 6: Design Expert Persona

| Aspect | Questions |
|--------|-----------|
| Identity | What specialist would you hire for this? |
| Expertise | What domain knowledge do they have? |
| Approach | How do they think about problems? |

**Output:** Agent role and expertise description

Example: "Senior code reviewer with expertise in code quality, security vulnerabilities, and project conventions. Approaches reviews methodically, checking each concern category."

### Step 3 of 6: Architect Comprehensive Instructions

This becomes the system prompt. Structure it as:

| Section | Content |
|---------|---------|
| Core responsibilities | What the agent MUST do |
| Methodology | How to approach the task |
| Quality checks | Self-verification steps |
| Output format | What to return |
| Boundaries | What NOT to do |

**Key principle:** Balance comprehensiveness with clarity—every instruction should add value.

### Step 4 of 6: Optimize for Performance

| Aspect | Questions |
|--------|-----------|
| Decision frameworks | How does the agent choose between options? |
| Quality control | How does it verify its own work? |
| Fallbacks | What happens when things go wrong? |
| Escalation | When should it ask for help? |

**Output:** Decision frameworks and quality mechanisms

### Step 5 of 6: Create Identifier

| Requirement | Guidance |
|-------------|----------|
| Format | lowercase, hyphens only (e.g., `code-reviewer`) |
| Length | 2-4 words |
| Content | Primary function, not generic terms |
| Avoid | "helper", "assistant", "manager" |

**Output:** Final `subagent_type` identifier

### Step 6 of 6: Define Triggering Examples

**This is the most critical step.**

Write 2-4 `<example>` blocks showing exactly when Claude should delegate:

```markdown
<example>
Context: [Situation when agent should be used]
user: "[User message that triggers delegation]"
assistant: "I'll use the [agent-name] agent to [purpose]."
<commentary>
[Explain WHY this triggers the agent]
</commentary>
</example>
```

**Include:**
- Explicit requests (user asks directly)
- Proactive triggering (agent should be used after certain events)
- Different phrasings of same intent

**Quality check:** Would these examples help Claude recognize when to delegate?

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| System prompt before triggering | Agent won't be used if triggering fails | Design examples FIRST |
| Generic examples | Claude won't know when to delegate | Specific, varied scenarios |
| Skipping proactive triggers | Misses when agent should fire automatically | Include both explicit and proactive |
| Too many responsibilities | Agent becomes unfocused | One clear purpose per agent |

## Verification

Before completing, confirm:

| Check | Status |
|-------|--------|
| Delegation rationale clear | Defined |
| Expert persona designed | Defined |
| System prompt structured | Drafted |
| Identifier follows format | Confirmed |
| 2-4 triggering examples | Written |
| Examples cover proactive use | Confirmed |
| Design document saved | Path confirmed |

## Output

Write validated design to: `docs/plans/YYYY-MM-DD-<agent-name>-design.md`

**Design document includes:**
- Agent identifier
- Delegation rationale
- Expert persona
- System prompt structure
- 2-4 triggering examples
- Tool restrictions (if any)
- Model/color choices

## Next Step

After saving the design document, run:

```
/implementing-agents docs/plans/YYYY-MM-DD-<agent-name>-design.md
```

Replace the path with your actual design document location.

## References

- agent-development — Structural reference (file format, frontmatter)
- agent-development/references/agent-creation-system-prompt.md — Official 6-step process
- agent-development/references/triggering-examples.md — Example crafting guide
- implementing-agents — Validation workflow (next stage)
```

**Step 3: Verify the file was created correctly**

```bash
head -20 plugins/plugin-dev/skills/brainstorming-agents/SKILL.md
```

Expected: YAML frontmatter with name and description fields.

**Step 4: Commit the change**

```bash
git add plugins/plugin-dev/skills/brainstorming-agents/SKILL.md
git commit -m "feat(plugin-dev): add brainstorming-agents skill

Implements 6-step agent design workflow from official
agent-creation-system-prompt.md. Key insight: triggering
examples are the most critical output since system prompts
only run after delegation decision.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Create implementing-agents SKILL.md

**Files:**
- Replace: `plugins/plugin-dev/skills/implementing-agents/SKILL.md`

**Step 1: Read the existing stub**

```bash
cat plugins/plugin-dev/skills/implementing-agents/SKILL.md
```

Expected: "[COMING SOON]" placeholder content.

**Step 2: Write the complete skill**

Replace the file with:

```markdown
---
name: implementing-agents
description: Use when building an agent from a design, "implement this agent",
  "test agent triggering", "agent not triggering", "debug agent delegation",
  or "validate agent quality". For structure reference, see agent-development.
---

# Implementing Agents

Build agents using triggering-first development: verify Claude delegates before investing in system prompt quality.

## Pipeline Context

This skill is **Stage 3: Implement** in the agent development pipeline.

| Aspect | Value |
|--------|-------|
| This stage | Build agent from design, validate triggering |
| Previous | `/brainstorming-agents` (design document) |
| Next | `/optimizing-plugins` or personal use |

## Prerequisites Check

Before proceeding, verify:

1. **Design document exists?**
   - If yes: "I see the design at `[path]`. Proceeding with implementation."
   - If no: "I don't see a design document. Should we start with `/brainstorming-agents`?"

2. **Design has required sections?**
   - Agent identifier
   - Triggering examples (2-4)
   - System prompt structure

If any section is missing, ask: "The design is missing [sections]. Should we complete it first?"

## Core Principle

> **TEST TRIGGERING BEFORE TUNING QUALITY.**
> If Claude won't delegate to your agent, perfecting the system prompt is wasted effort.

### Why This Order Matters

- System prompt only runs AFTER Claude decides to delegate
- Beautiful system prompt + bad triggering = agent never used
- Bad triggering is cheaper to fix than bad system prompt

## Three-Phase Validation

| Phase | What to Test | How to Test | Iterate On |
|-------|--------------|-------------|------------|
| **1. Triggering** | Does Claude delegate? | Ask tasks matching your examples | description/examples |
| **2. Quality** | Does agent produce good output? | Invoke agent explicitly by name | system prompt |
| **3. Harden** | Edge cases, false positives? | Various phrasings, edge scenarios | both |

## Phase 1: Triggering (RED/GREEN)

**Goal:** Verify Claude knows when to delegate to your agent.

### Step 1: Create the agent file

Create `agents/<agent-name>.md` with:
- Frontmatter (name, description with examples)
- System prompt body

### Step 2: Write triggering test cases

Based on your design examples, create test prompts:

```markdown
| Test Prompt | Expected Behavior |
|-------------|-------------------|
| [Prompt matching example 1] | Claude delegates to agent |
| [Prompt matching example 2] | Claude delegates to agent |
| [Prompt that should NOT trigger] | Claude handles directly |
```

### Step 3: Run triggering tests

For each test prompt:
1. Send the prompt to Claude
2. Observe: Does Claude delegate to the agent?
3. Record result: PASS (delegated) or FAIL (didn't delegate)

### Step 4: Iterate on description/examples

**If Claude doesn't delegate (FAIL):**
- Add more examples covering the phrasing you used
- Make existing examples more specific
- Check that keywords from test prompt appear in examples

**If Claude delegates when it shouldn't (false positive):**
- Make examples more specific
- Add negative examples showing when NOT to use
- Narrow the description scope

**Continue until all triggering tests pass.**

## Phase 2: Quality

**Goal:** Verify the agent produces good output.

### Step 1: Invoke agent explicitly

Bypass triggering by invoking directly:
```
Use the <agent-name> agent to [specific task]
```

### Step 2: Evaluate output

| Check | Question |
|-------|----------|
| Completeness | Did it do everything requested? |
| Correctness | Is the output accurate? |
| Format | Is output structured as expected? |
| Boundaries | Did it stay within scope? |

### Step 3: Iterate on system prompt

**Common fixes:**
- Add missing instructions
- Clarify ambiguous guidance
- Add examples within system prompt
- Strengthen quality checks

**Continue until output quality is acceptable.**

## Phase 3: Harden

**Goal:** Ensure robustness across edge cases.

### Step 1: Test varied phrasings

Same intent, different words:
- "Review this code" vs "Check my code" vs "Look at this PR"
- All should trigger (or not trigger) consistently

### Step 2: Test edge cases

| Edge Case | Test |
|-----------|------|
| Boundary conditions | Tasks at the edge of agent's scope |
| Ambiguous requests | Tasks that could go either way |
| Combined requests | Tasks mixing agent's domain with others |

### Step 3: Document hardening results

Record any issues found and fixes applied.

## Three Triggering Failure Modes

| Failure Mode | Symptom | Fix |
|--------------|---------|-----|
| **Not triggering** | Claude ignores agent | Add more examples covering different phrasings |
| **Triggering too often** | Agent fires inappropriately | Make examples more specific, add negative examples |
| **Wrong scenarios** | Agent fires for wrong tasks | Revise examples to show only correct scenarios |

## Checklist

**Use TodoWrite to create todos for each item.**

**Phase 1: Triggering**
- [ ] Create agent file with frontmatter and system prompt
- [ ] Write triggering test cases (3+ scenarios)
- [ ] Run triggering tests
- [ ] All triggering tests pass

**Phase 2: Quality**
- [ ] Invoke agent explicitly (bypass triggering)
- [ ] Evaluate output against expectations
- [ ] Iterate on system prompt until quality acceptable

**Phase 3: Harden**
- [ ] Test with varied phrasings (3+ variations)
- [ ] Test edge cases at scope boundaries
- [ ] Check for false positives

**Deployment**
- [ ] Commit to git
- [ ] Verify agent appears in agent list

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Tuning system prompt first | Wasted if triggering fails | Test triggering FIRST |
| Testing only happy path | Misses false positives | Include negative cases |
| Generic test prompts | Don't match real usage | Use actual user phrasings |
| Skipping Phase 3 | Fragile agent | Always harden |

## Output

Working agent file in correct location:
- Plugin agent: `plugin-name/agents/<agent-name>.md`

Plus any updates to description/examples from triggering iteration.

## Next Step

Choose one and run:

| Situation | Command |
|-----------|---------|
| More components to build | `/brainstorming-{component}` for next component |
| Plugin complete, want polish | `/optimizing-plugins` |
| Personal use only | Done — agent is active |

## References

- agent-development — Structural reference (file format, frontmatter, tools)
- agent-development/references/triggering-examples.md — Example crafting guide
- brainstorming-agents — Design phase (if design needed)
```

**Step 3: Verify the file was created correctly**

```bash
head -20 plugins/plugin-dev/skills/implementing-agents/SKILL.md
```

Expected: YAML frontmatter with name and description fields.

**Step 4: Commit the change**

```bash
git add plugins/plugin-dev/skills/implementing-agents/SKILL.md
git commit -m "feat(plugin-dev): add implementing-agents skill

Implements triggering-first validation workflow for agents.
Core principle: TEST TRIGGERING BEFORE TUNING QUALITY.
Three phases: Triggering (RED/GREEN) → Quality → Harden.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Update design document with implementation marker

**Files:**
- Modify: `docs/plans/2026-01-02-agents-pipeline-slice3-design.md`

**Step 1: Add superseded marker to design document**

Add at the top of the file (after the title):

```markdown
> **⚠️ SUPERSEDED (2026-01-02):** Implementation complete
>
> - Replacement: `plugins/plugin-dev/skills/brainstorming-agents/SKILL.md` and `plugins/plugin-dev/skills/implementing-agents/SKILL.md`
>
> *Original preserved for historical reference.*
```

**Step 2: Commit the change**

```bash
git add docs/plans/2026-01-02-agents-pipeline-slice3-design.md
git commit -m "docs: mark agents pipeline slice 3 design as superseded

Implementation complete in skills:
- brainstorming-agents: 6-step design workflow
- implementing-agents: triggering-first validation

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Verify skills load correctly

**Step 1: Check frontmatter validity**

```bash
head -10 plugins/plugin-dev/skills/brainstorming-agents/SKILL.md
head -10 plugins/plugin-dev/skills/implementing-agents/SKILL.md
```

Expected: Valid YAML frontmatter with `name` and `description` fields.

**Step 2: Verify skill count**

```bash
ls plugins/plugin-dev/skills/*/SKILL.md | wc -l
```

Expected: Should be at least 12 skills (the number mentioned in CLAUDE.md).

**Step 3: Check for YAML syntax errors**

```bash
# Quick validation that frontmatter parses
python3 -c "
import yaml
import sys

for path in ['plugins/plugin-dev/skills/brainstorming-agents/SKILL.md',
             'plugins/plugin-dev/skills/implementing-agents/SKILL.md']:
    with open(path) as f:
        content = f.read()
    # Extract frontmatter between --- markers
    if content.startswith('---'):
        end = content.find('---', 3)
        frontmatter = content[3:end]
        try:
            data = yaml.safe_load(frontmatter)
            assert 'name' in data, f'{path}: missing name'
            assert 'description' in data, f'{path}: missing description'
            print(f'{path}: OK')
        except Exception as e:
            print(f'{path}: FAIL - {e}')
            sys.exit(1)
"
```

Expected: Both files show "OK".

---

## Task 5: Merge to main

**Use `superpowers:finishing-a-development-branch` skill.**

If working in a worktree:
1. Ensure all commits are pushed
2. Create PR or merge directly based on skill guidance
3. Clean up worktree after merge

If working directly on main:
1. Verify all changes committed
2. Push to remote

---

## Success Criteria

- [ ] brainstorming-agents skill follows 6-step workflow from official docs
- [ ] implementing-agents skill follows triggering-first validation (TEST TRIGGERING BEFORE TUNING QUALITY)
- [ ] Both skills have valid frontmatter (name, description)
- [ ] Both skills reference agent-development for structural details
- [ ] Design document marked as superseded
- [ ] All commits follow conventional format
