# Plugin Development Pipeline — Slice 2: Hooks

## Overview

This design specifies two skills for the hooks pipeline:

| Skill | Purpose |
|-------|---------|
| `brainstorming-hooks` | Design hooks through collaborative dialogue |
| `implementing-hooks` | Build hooks using test-driven development |

These skills parallel Slice 1's `brainstorming-skills` and `implementing-skills`. The existing `hook-development` skill remains as structural reference.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ TRIAGE: brainstorming-plugins                               │
│ Identifies that hooks are needed                            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ DESIGN: brainstorming-hooks                                 │
│ 6-step workflow → design document                           │
│ Reference: hook-development (structural details)            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ IMPLEMENT: implementing-hooks                               │
│ TDD: RED → GREEN → REFACTOR                                 │
│ Reference: hook-development (structural details)            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ optimizing-plugins   │
              │ or deploying-plugins │
              └──────────────────────┘
```

---

## Skill 1: brainstorming-hooks

### Metadata

```yaml
name: brainstorming-hooks
description: >
  Design hooks through collaborative dialogue. Use when "design a hook",
  "I need X to always happen", "hook vs skill", "prevent Claude from Y",
  or after brainstorming-plugins identifies hooks.
```

### Triggers

- `design a hook for {purpose}`
- `I need {behavior} to always happen`
- `hook vs skill`
- `prevent Claude from {action}`
- After `brainstorming-plugins` identifies hooks

### Pipeline Context

| Aspect | Value |
|--------|-------|
| Stage | Design |
| Prerequisite | `brainstorming-plugins` or direct request |
| Hands off to | `implementing-hooks` |
| Reference | `hook-development` for technical details |

### Core Principle

Hooks provide deterministic control. They guarantee behavior—unlike skills, which Claude can choose to ignore.

**Decision rule:**
- Guidance Claude should consider → Skill
- Behavior that must always happen → Hook

### The 6-Step Workflow

#### Step 1: Problem Definition

Ask one question at a time:

| Question | Purpose |
|----------|---------|
| What must ALWAYS happen? | Confirms deterministic need |
| When should it trigger? | Maps to event selection |
| What breaks if this fails? | Determines security rigor |

**Output:** "When {event}, {action} must always happen because {reason}."

#### Step 2: Event Selection

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

**Output:** Selected event with rationale.

#### Step 2b: Matcher Selection

For events that support matchers:

| Event | Matcher Type | Examples |
|-------|--------------|----------|
| PreToolUse | Tool name (regex) | `Bash`, `Write\|Edit`, `mcp__.*` |
| PermissionRequest | Tool name (regex) | Same as PreToolUse |
| PostToolUse | Tool name (regex) | Same as PreToolUse |
| Notification | Notification type | `permission_prompt`, `idle_prompt` |
| SessionStart | Source | `startup`, `resume`, `clear`, `compact` |
| PreCompact | Trigger | `manual`, `auto` |

**MCP tool pattern:** `mcp__<server>__<tool>`

#### Step 2c: Special Capabilities

| Event | Capability | Use Case |
|-------|------------|----------|
| PreToolUse | `updatedInput` | Modify tool args before execution |
| PermissionRequest | `updatedInput` | Modify and auto-approve |
| SessionStart | `CLAUDE_ENV_FILE` | Persist env vars for session |
| UserPromptSubmit | `additionalContext` | Inject context for Claude |
| SessionStart | `additionalContext` | Load project context |

#### Step 3: Type Decision

| Factor | Command Hook | Prompt Hook |
|--------|--------------|-------------|
| Logic | Deterministic rules | Context-aware judgment |
| Speed | Fast (local) | Slower (API call) |
| Setup | Requires script | Configure prompt only |
| Best for | File checks, formatting | Completion validation |

**Decision:**
- Express as code? → Command hook
- Requires understanding conversation? → Prompt hook

#### Step 4: Architecture Constraints

| Constraint | Implication |
|------------|-------------|
| Hooks run in parallel | Cannot depend on another hook's output |
| 60-second default timeout | Keep hooks fast |
| Hooks load at startup | Changes require restart |
| JSON via stdin | Must parse input |
| Exit codes matter | 0=success, 2=block |

#### Step 5: Security Review

**Mandatory checklist:**

| Check | Implementation |
|-------|----------------|
| Validate inputs | Never trust `tool_input` blindly |
| Quote variables | `"$VAR"` not `$VAR` |
| Block path traversal | Check for `..` in paths |
| Use absolute paths | `$CLAUDE_PROJECT_DIR` or `$CLAUDE_PLUGIN_ROOT` |
| Skip sensitive files | `.env`, `.git/`, credentials |

#### Step 6: Output Design

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

### Output

Write design to: `docs/plans/YYYY-MM-DD-<hook-name>-design.md`

**Sections:**
1. Problem — What must always happen
2. Event — Selected event and matchers
3. Type — Command or prompt
4. Output design — Exit codes, JSON fields
5. Security — Risks and mitigations
6. Test plan — Scenarios for RED phase

### Handoff

```
/implementing-hooks docs/plans/[design-file].md
```

---

## Skill 2: implementing-hooks

### Metadata

```yaml
name: implementing-hooks
description: >
  Build hooks using test-driven development. Use when "implement this hook",
  "build the hook", "test my hook", or after brainstorming-hooks produces
  a design.
```

### Triggers

- `implement this hook`
- `build the hook from design`
- `test my hook`
- After `brainstorming-hooks`

### Pipeline Context

| Aspect | Value |
|--------|-------|
| Stage | Implement |
| Prerequisite | `brainstorming-hooks` (design document) |
| Hands off to | `optimizing-plugins` or `deploying-plugins` |
| Reference | `hook-development` for structural details |

### The Iron Law

```
NO HOOK CODE WITHOUT OBSERVING UNDESIRED BEHAVIOR FIRST
```

Wrote hook before testing? Delete it. Start over.

### The TDD Process

#### Phase 1: RED — Observe Undesired Behavior

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

#### Phase 2: GREEN — Minimal Hook

| Step | Action |
|------|--------|
| 1 | Write minimal hook addressing observed problem |
| 2 | Test with real input: `echo '<json>' \| ./hook.sh` |
| 3 | Verify output matches expectation |
| 4 | Integration test: `claude --debug` |
| 5 | Observe: Problem now blocked |

**Minimal means minimal.** Only what passes the test.

#### Phase 3: REFACTOR — Harden

| Test | Input |
|------|-------|
| Empty input | `echo '{}' \| ./hook.sh` |
| Malformed JSON | `echo 'not json' \| ./hook.sh` |
| Missing fields | `echo '{"tool_name":"Write"}' \| ./hook.sh` |
| Path traversal | Paths containing `../` |

After each change: re-run all tests. Stay green.

### Verification Checklist

Before marking complete:

- [ ] Observed undesired behavior without hook
- [ ] Hook addresses that specific behavior
- [ ] Tested with real captured input
- [ ] Watched hook block/allow correctly
- [ ] Integration tested with `claude --debug`
- [ ] Edge cases tested and handled
- [ ] Security checklist passed
- [ ] JSON output valid (if using JSON output)

**Cannot check all boxes? Start over.**

### Handoff

| Situation | Next Step |
|-----------|-----------|
| More components | `brainstorming-{component}` |
| Plugin complete, want polish | `optimizing-plugins` |
| Ready to publish | `deploying-plugins` |
| Personal use | Done |

---

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Hook for everything | Adds complexity and latency | Skills for guidance, hooks for guarantees |
| Writing hook before observing problem | Cannot verify it solves real issue | RED phase first |
| Hardcoded paths | Breaks after installation | `$CLAUDE_PROJECT_DIR` or `$CLAUDE_PLUGIN_ROOT` |
| Unquoted variables | Shell injection risk | Always `"$VAR"` |
| Exit code 0 with error intent | Wrong behavior | Exit 2 for blocking |
| Complex prompt for simple rules | Slow, unpredictable | Command hooks for deterministic checks |
| Skipping security review | Data exfiltration risk | Always apply checklist |

---

## The 5 Canonical Hook Patterns

From official Anthropic documentation:

| Pattern | Event | Example |
|---------|-------|---------|
| Notifications | Notification | Desktop alert when Claude waits |
| Formatting | PostToolUse | Run prettier after edit |
| Logging | PreToolUse | Track all commands |
| Feedback | PostToolUse | Validate code conventions |
| Permissions | PreToolUse | Block sensitive files |

---

## Implementation Notes

### File Locations

| Skill | Path |
|-------|------|
| brainstorming-hooks | `plugins/plugin-dev/skills/brainstorming-hooks/SKILL.md` |
| implementing-hooks | `plugins/plugin-dev/skills/implementing-hooks/SKILL.md` |

### Relationship to Existing Skills

- `hook-development` remains as structural reference
- New skills handle workflow; reference `hook-development` for details
- Mirrors the `skill-development` → `brainstorming-skills` → `implementing-skills` pattern

### Dependencies

Both skills reference:
- `hook-development` — Technical details (events, formats, schemas)
- Official Anthropic hooks documentation — Authoritative source
