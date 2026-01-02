# Hooks Pipeline Slice 2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace stub skills with full implementations for `brainstorming-hooks` and `implementing-hooks`.

**Architecture:** Both skills follow the pattern established by Slice 1 (`brainstorming-skills` / `implementing-skills`). The existing `hook-development` skill remains as structural reference. Content comes from the design document at `docs/plans/2026-01-02-hooks-pipeline-slice2-design.md`.

**Tech Stack:** Markdown skills with YAML frontmatter.

---

## Task 1: Replace brainstorming-hooks Stub

**Files:**
- Modify: `plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md`

**Step 1: Read the design document**

Read: `docs/plans/2026-01-02-hooks-pipeline-slice2-design.md` (Section: "Skill 1: brainstorming-hooks")

**Step 2: Write the full skill**

Replace the stub with the full implementation. The skill should:
- Have proper frontmatter (name, description with triggers)
- Include the 6-step workflow from design
- Reference `hook-development` for structural details
- Include pipeline context section
- Have anti-patterns and verification checklist

```markdown
---
name: brainstorming-hooks
description: Use when designing a hook, "I need X to always happen",
  "hook vs skill", "prevent Claude from Y", or after brainstorming-plugins
  identifies hooks. Guides collaborative hook design through 6-step process.
---

# Hook Design

Turn hook ideas into design documents through collaborative dialogue.

## Quick Start

```
User: "I need a hook for X"
Claude: Uses 6-step workflow

1. Problem definition (what must ALWAYS happen?)
2. Event selection (10 events, matchers, capabilities)
3. Type decision (command vs prompt)
4. Architecture constraints (parallel execution, timeouts)
5. Security review (5-point checklist)
6. Output design (exit codes, JSON fields)
7. Write design document → handoff to implementing-hooks
```

## Triggers

- `design a hook for {purpose}`
- `I need {behavior} to always happen`
- `hook vs skill` / `when should I use hooks`
- `prevent Claude from {action}`
- After `brainstorming-plugins` identifies hooks

## Prerequisites

Before using this skill:
- Know you need a hook (from `/brainstorming-plugins` or direct need)
- Understand hooks = deterministic control (ALWAYS happens, not guidance)

No design document? This skill creates one.

## Pipeline Context

This skill is **Stage 2: Design** in the hooks pipeline.

| Aspect | Value |
|--------|-------|
| This stage | Design hook from requirements |
| Previous | `/brainstorming-plugins` (or direct request) |
| Next | `/implementing-hooks` |
| Reference | `hook-development` (structural details) |

## Core Principle

Hooks provide deterministic control—behavior that MUST always happen, not guidance Claude can ignore.

**Decision rule:**
| Need | Use |
|------|-----|
| Guidance Claude should consider | Skill |
| Behavior that must always happen | Hook |

## The 6-Step Workflow

### Step 1: Problem Definition

Ask one question at a time:

| Question | Purpose |
|----------|---------|
| What must ALWAYS happen? | Confirms deterministic need |
| When should it trigger? | Maps to event selection |
| What breaks if this fails? | Determines security rigor |

**Output:** "When {event}, {action} must always happen because {reason}."

### Step 2: Event Selection

| Event | Fires When | Blocks? | Use For |
|-------|------------|---------|---------|
| PreToolUse | Before tool runs | Yes (allow/deny/ask) | Validation, permissions |
| PermissionRequest | Permission dialog shown | Yes (allow/deny) | Auto-approve/deny |
| PostToolUse | After tool completes | No | Formatting, logging, feedback |
| UserPromptSubmit | User submits prompt | Yes | Context injection, validation |
| Notification | Claude notifies | No | Desktop alerts, logging |
| Stop | Agent finishes | Yes | Completion validation |
| SubagentStop | Subagent finishes | Yes | Task validation |
| SessionStart | Session begins | No | Load context, set env vars |
| SessionEnd | Session ends | No | Cleanup, logging |
| PreCompact | Before compaction | No | Preserve context |

**Matchers** (for events that support them):

| Event | Matcher Type | Examples |
|-------|--------------|----------|
| PreToolUse | Tool name (regex) | `Bash`, `Write\|Edit`, `mcp__.*` |
| PermissionRequest | Tool name (regex) | Same as PreToolUse |
| PostToolUse | Tool name (regex) | Same as PreToolUse |
| Notification | Notification type | `permission_prompt`, `idle_prompt` |
| SessionStart | Source | `startup`, `resume`, `clear`, `compact` |
| PreCompact | Trigger | `manual`, `auto` |

**Special capabilities:**

| Event | Capability | Use Case |
|-------|------------|----------|
| PreToolUse | `updatedInput` | Modify tool args before execution |
| PermissionRequest | `updatedInput` | Modify and auto-approve |
| SessionStart | `CLAUDE_ENV_FILE` | Persist env vars for session |
| UserPromptSubmit | `additionalContext` | Inject context for Claude |

### Step 3: Type Decision

| Factor | Command Hook | Prompt Hook |
|--------|--------------|-------------|
| Logic | Deterministic rules | Context-aware judgment |
| Speed | Fast (local) | Slower (API call) |
| Setup | Requires script | Configure prompt only |
| Best for | File checks, formatting | Completion validation |

**Decision:**
- Express as code? → Command hook
- Requires understanding conversation? → Prompt hook

### Step 4: Architecture Constraints

| Constraint | Implication |
|------------|-------------|
| Hooks run in parallel | Cannot depend on another hook's output |
| 60-second default timeout | Keep hooks fast |
| Hooks load at startup | Changes require restart |
| JSON via stdin | Must parse input |
| Exit codes matter | 0=success, 2=block |

### Step 5: Security Review

**Mandatory checklist:**

| Check | Implementation |
|-------|----------------|
| Validate inputs | Never trust `tool_input` blindly |
| Quote variables | `"$VAR"` not `$VAR` |
| Block path traversal | Check for `..` in paths |
| Use absolute paths | `$CLAUDE_PROJECT_DIR` or `$CLAUDE_PLUGIN_ROOT` |
| Skip sensitive files | `.env`, `.git/`, credentials |

### Step 6: Output Design

**Exit code behavior per event:**

| Event | Exit Code 2 |
|-------|-------------|
| PreToolUse | Blocks tool, stderr → Claude |
| PermissionRequest | Denies permission, stderr → Claude |
| PostToolUse | stderr → Claude (tool already ran) |
| UserPromptSubmit | Blocks prompt, stderr → user |
| Stop/SubagentStop | Blocks stopping, stderr → Claude |
| Others | stderr → user only |

**JSON output fields:**

| Event | Decision | Context | Modification |
|-------|----------|---------|--------------|
| PreToolUse | `permissionDecision`, `permissionDecisionReason` | — | `updatedInput` |
| PermissionRequest | `decision.behavior`, `message` | — | `updatedInput` |
| PostToolUse | `decision`, `reason` | `additionalContext` | — |
| Stop/SubagentStop | `decision`, `reason` | — | — |
| UserPromptSubmit | `decision`, `reason` | `additionalContext` | — |
| SessionStart | — | `additionalContext` | — |

**Common fields (all events):** `continue`, `stopReason`, `suppressOutput`, `systemMessage`

## Output

Write design to: `docs/plans/YYYY-MM-DD-<hook-name>-design.md`

**Sections:**
1. Problem — What must always happen
2. Event — Selected event and matchers
3. Type — Command or prompt
4. Output design — Exit codes, JSON fields
5. Security — Risks and mitigations
6. Test plan — Scenarios for RED phase

## Next Step

After saving the design document:

```
/implementing-hooks docs/plans/[design-file].md
```

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Hook for everything | Adds complexity and latency | Skills for guidance, hooks for guarantees |
| Skipping security review | Data exfiltration risk | Always apply checklist |
| Vague problem statement | Can't verify hook solves issue | "When X, Y must happen" |
| Designing in isolation | May duplicate or conflict | Check hook-development first |

## Verification

Before completing:

| Check | Status |
|-------|--------|
| Problem statement (When X, Y must happen) | Defined |
| Event selected with rationale | Confirmed |
| Matchers specified (if applicable) | Listed |
| Type decision (command/prompt) | Made |
| Security checklist reviewed | Done |
| Design document saved | Path confirmed |

## References

- hook-development — Structural reference (file format, events, scripts)
- implementing-hooks — TDD implementation (next stage)
- Official hooks docs — `docs/claude-code-documentation/hooks-*.md`
```

**Step 3: Verify the skill loads**

Run: `head -20 plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md`
Expected: See frontmatter with name and description

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md
git commit -m "feat(plugin-dev): implement brainstorming-hooks skill

Replace stub with full 6-step hook design workflow:
- Event selection with matchers and capabilities
- Type decision (command vs prompt)
- Security review checklist
- Output design (exit codes, JSON fields)"
```

---

## Task 2: Replace implementing-hooks Stub

**Files:**
- Modify: `plugins/plugin-dev/skills/implementing-hooks/SKILL.md`

**Step 1: Read the design document**

Read: `docs/plans/2026-01-02-hooks-pipeline-slice2-design.md` (Section: "Skill 2: implementing-hooks")

**Step 2: Write the full skill**

Replace the stub with the full implementation:

```markdown
---
name: implementing-hooks
description: Use when building a hook from a design, "implement this hook",
  "write the hook", "test my hook", or "TDD for hooks". For structure reference,
  see hook-development.
---

# Implementing Hooks

Build hooks using test-driven development: observe undesired behavior first, then write the hook to fix it.

## Pipeline Context

This skill is **Stage 3: Implement** in the hooks pipeline.

| Aspect | Value |
|--------|-------|
| This stage | Build hook from design using TDD |
| Previous | `/brainstorming-hooks` (design document) |
| Next | `/optimizing-plugins` or personal use |
| Reference | `hook-development` (structural details) |

## Prerequisites Check

Before proceeding, verify:

1. **Design document exists?**
   - If yes: "I see the design at `[path]`. Proceeding with implementation."
   - If no: "No design found. Should we start with `/brainstorming-hooks`?"

2. **Design has required sections?**
   - Problem statement
   - Event selection
   - Type decision (command/prompt)
   - Security checklist

If missing: "The design is missing [sections]. Complete it first?"

## The Iron Law

```
NO HOOK CODE WITHOUT OBSERVING UNDESIRED BEHAVIOR FIRST
```

Wrote hook before testing? Delete it. Start over.

**No exceptions:** Not for "simple hooks" or "obvious fixes."

## The TDD Process

### RED: Observe Undesired Behavior

| Step | Action |
|------|--------|
| 1 | Create realistic test scenario |
| 2 | Run Claude Code WITHOUT the hook |
| 3 | Document what actually happens |
| 4 | Confirm: "This is the problem" |

**Critical:** If you cannot observe the problem, you do not understand it.

**Example:**
```bash
# Scenario: Claude writes to .env file
# Run claude --debug, ask it to edit .env
# Observe: It writes without restriction
# Document: "Without hook, Claude modifies sensitive files"
```

### GREEN: Minimal Hook

| Step | Action |
|------|--------|
| 1 | Write minimal hook addressing observed problem |
| 2 | Test with real input: `echo '<json>' \| ./hook.sh` |
| 3 | Verify output matches expectation |
| 4 | Integration test: `claude --debug` |
| 5 | Observe: Problem now blocked |

**Minimal means minimal.** Only what passes the test.

**For plugin hooks:**
- Use `${CLAUDE_PLUGIN_ROOT}` for paths
- Place in `hooks/hooks.json` with wrapper format

### REFACTOR: Harden

| Test | Input |
|------|-------|
| Empty input | `echo '{}' \| ./hook.sh` |
| Malformed JSON | `echo 'not json' \| ./hook.sh` |
| Missing fields | `echo '{"tool_name":"Write"}' \| ./hook.sh` |
| Path traversal | Paths containing `../` |

After each change: re-run all tests. Stay green.

## Testing Workflow

**Integration test with Claude Code:**

1. Register hook via `/hooks` or edit settings
2. Restart Claude Code (hooks load at startup)
3. Run `claude --debug`
4. Trigger the event
5. Verify debug output shows hook execution

**Sample input templates:**

```json
// PreToolUse
{
  "session_id": "test",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/path/to/file.txt", "content": "..." }
}

// PostToolUse
{
  "session_id": "test",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/path/to/file.txt" },
  "tool_response": { "success": true }
}

// UserPromptSubmit
{
  "session_id": "test",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "User's prompt text"
}
```

## Checklist

**Use TodoWrite to track progress.**

**RED Phase:**
- [ ] Create realistic test scenario
- [ ] Run WITHOUT hook — document baseline
- [ ] Confirm observed problem matches design

**GREEN Phase:**
- [ ] Write minimal hook addressing problem
- [ ] Test with sample input
- [ ] Verify exit code and output
- [ ] Integration test with `claude --debug`
- [ ] Problem is now blocked/handled

**REFACTOR Phase:**
- [ ] Test empty input
- [ ] Test malformed JSON
- [ ] Test missing fields
- [ ] Test path traversal (if applicable)
- [ ] Security checklist passed

**Deployment:**
- [ ] Hook in correct location (settings or plugin hooks.json)
- [ ] Scripts executable (`chmod +x`)
- [ ] Commit to git

## Output

Working hook in correct location:
- **Settings hook:** `~/.claude/settings.json` or `.claude/settings.json`
- **Plugin hook:** `plugin-name/hooks/hooks.json`

Plus any scripts in `hooks/` or `scripts/` directories.

## Next Step

| Situation | Command |
|-----------|---------|
| More components to build | `/brainstorming-{component}` |
| Plugin complete, want polish | `/optimizing-plugins` |
| Personal use only | Done — hook is active |

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Writing hook before observing | Can't verify it solves real issue | RED phase first |
| Hardcoded paths | Breaks after installation | `$CLAUDE_PROJECT_DIR` or `$CLAUDE_PLUGIN_ROOT` |
| Unquoted variables | Shell injection risk | Always `"$VAR"` |
| Exit code 0 with error intent | Wrong behavior | Exit 2 for blocking |
| Skipping edge case tests | Breaks on unexpected input | REFACTOR phase required |

## Verification

Before marking complete:

| Check | Evidence |
|-------|----------|
| Observed undesired behavior | Documented baseline |
| Hook addresses that behavior | Test passes |
| Tested with real input | Command and output shown |
| Integration tested | `claude --debug` output |
| Edge cases handled | All REFACTOR tests pass |
| Security checklist passed | 5 checks confirmed |

## References

- hook-development — Structural reference (file format, events, scripts)
- brainstorming-hooks — Design phase (if design needed)
- Official hooks docs — `docs/claude-code-documentation/hooks-*.md`
```

**Step 3: Verify the skill loads**

Run: `head -20 plugins/plugin-dev/skills/implementing-hooks/SKILL.md`
Expected: See frontmatter with name and description

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/implementing-hooks/SKILL.md
git commit -m "feat(plugin-dev): implement implementing-hooks skill

Replace stub with full TDD hook implementation workflow:
- Iron Law: observe undesired behavior first
- RED/GREEN/REFACTOR phases adapted for hooks
- Sample input templates for testing
- Edge case and security verification"
```

---

## Task 3: Update Design Document Status

**Files:**
- Modify: `docs/plans/2026-01-02-hooks-pipeline-slice2-design.md`

**Step 1: Add superseded marker**

Add at the top of the design document:

```markdown
> **✅ IMPLEMENTED (2026-01-02):** Skills created per this design.
>
> - `plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md`
> - `plugins/plugin-dev/skills/implementing-hooks/SKILL.md`
```

**Step 2: Commit**

```bash
git add docs/plans/2026-01-02-hooks-pipeline-slice2-design.md
git commit -m "docs: mark hooks pipeline design as implemented"
```

---

## Task 4: Verify Skills Load Correctly

**Step 1: Test skill discovery**

Run from main project directory:
```bash
cd /Users/jp/Projects/active/superserum/.worktrees/hooks-slice2
grep -r "brainstorming-hooks" plugins/plugin-dev/skills/*/SKILL.md
grep -r "implementing-hooks" plugins/plugin-dev/skills/*/SKILL.md
```

Expected: Skills reference each other correctly

**Step 2: Validate frontmatter**

Run:
```bash
head -5 plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md
head -5 plugins/plugin-dev/skills/implementing-hooks/SKILL.md
```

Expected: Valid YAML frontmatter with `name` and `description`

**Step 3: Final commit with branch summary**

```bash
git log --oneline feat/hooks-pipeline-slice2 ^main
```

Expected: 3-4 commits implementing the slice

---

## Task 5: Merge to Main

**Step 1: Return to main worktree**

```bash
cd /Users/jp/Projects/active/superserum
```

**Step 2: Merge the feature branch**

```bash
git merge feat/hooks-pipeline-slice2 --no-ff -m "feat(plugin-dev): complete hooks pipeline slice 2

Implements brainstorming-hooks and implementing-hooks skills:
- 6-step hook design workflow
- TDD implementation with RED/GREEN/REFACTOR
- Event selection, matchers, security review
- Integration with existing hook-development reference"
```

**Step 3: Clean up worktree**

```bash
git worktree remove .worktrees/hooks-slice2
git branch -d feat/hooks-pipeline-slice2
```

---

## Summary

| Task | Files | Commits |
|------|-------|---------|
| 1 | brainstorming-hooks/SKILL.md | feat: implement brainstorming-hooks |
| 2 | implementing-hooks/SKILL.md | feat: implement implementing-hooks |
| 3 | design document | docs: mark as implemented |
| 4 | — | Verification only |
| 5 | — | Merge to main |
