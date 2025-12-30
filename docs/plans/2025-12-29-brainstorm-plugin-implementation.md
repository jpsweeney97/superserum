# brainstorm-plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a plugin-focused brainstorming skill to plugin-dev that helps users design Claude Code plugins through collaborative dialogue.

**Architecture:** Command + Skill + Reference file. The command provides explicit `/plugin-dev:brainstorm` invocation. The skill triggers automatically on phrases like "design a plugin". The reference file provides the component decision framework.

**Tech Stack:** Markdown files with YAML frontmatter (Claude Code plugin format)

---

## Task 1: Create Command File

**Files:**
- Create: `plugins/plugin-dev/commands/brainstorm.md`

**Step 1: Create the command file**

```markdown
---
disable-model-invocation: true
---
Invoke the plugin-dev:brainstorming-plugins skill and follow it exactly as presented to you
```

**Step 2: Verify file exists and has correct frontmatter**

Run: `head -5 plugins/plugin-dev/commands/brainstorm.md`
Expected: Shows frontmatter with `disable-model-invocation: true`

**Step 3: Commit**

```bash
git add plugins/plugin-dev/commands/brainstorm.md
git commit -m "feat(plugin-dev): add brainstorm command"
```

---

## Task 2: Create Skill Directory Structure

**Files:**
- Create: `plugins/plugin-dev/skills/brainstorming-plugins/`
- Create: `plugins/plugin-dev/skills/brainstorming-plugins/references/`

**Step 1: Create directories**

```bash
mkdir -p plugins/plugin-dev/skills/brainstorming-plugins/references
```

**Step 2: Verify structure**

Run: `ls -la plugins/plugin-dev/skills/brainstorming-plugins/`
Expected: Shows `references/` directory

---

## Task 3: Create SKILL.md

**Files:**
- Create: `plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md`

**Step 1: Create the skill file**

```markdown
---
name: brainstorming-plugins
description: >
  Designs Claude Code plugins through collaborative dialogue before
  implementation. Use when user wants to "build a plugin", "create a
  plugin", "design a plugin for X", or asks what components they need.
  Explores problem, selects component types (Skills vs Commands vs
  Agents vs Hooks vs MCP), and outputs plugin design document.
---

# Brainstorming Plugins

Design Claude Code plugins through collaborative dialogue before implementation.

## Overview

This skill turns plugin ideas into well-formed designs through natural conversation. The goal: understand the problem, select the right components, and produce a design document for `/plugin-dev:create-plugin`.

## The Process

1. **Understand the idea** — Ask questions one at a time to clarify purpose, users, and constraints
2. **Explore approaches** — Propose 2-3 approaches with trade-offs; lead with your recommendation
3. **Present the design** — Show design in 200-300 word sections; validate each
4. **Document and handoff** — Write to `docs/plans/`, offer implementation paths

## Starting the Conversation

Before asking questions:
- Check project context (existing plugins, patterns, conventions)
- Read any existing docs the user mentions
- Understand if this extends an existing plugin or creates a new one

Then ask one question at a time. Prefer multiple choice when possible.

## Key Questions

### 1. Problem Clarity

- What problem does this plugin solve?
- Who uses it? (The user explicitly? Claude automatically? Both?)
- When does it activate? (Explicit command? Automatic trigger? Event-driven?)

### 2. Component Selection

Use the decision framework in [references/component-decision-guide.md](references/component-decision-guide.md).

Quick reference:

| User Need | Component | Why |
|-----------|-----------|-----|
| "Claude needs to know about X" | **Skill** | Knowledge that loads on trigger |
| "User runs action X explicitly" | **Command** | `/plugin:action` invocation |
| "Delegate to separate context" | **Agent** | Isolated execution, custom tools |
| "X must ALWAYS happen on event Y" | **Hook** | Deterministic, guaranteed |
| "Connect to external service X" | **MCP Server** | Provides tools for external APIs |
| "Code intelligence for language X" | **LSP Server** | Diagnostics, go-to-definition |

### 3. Hook Events (if using hooks)

Which events matter?
- `PreToolUse` / `PostToolUse` — Before/after tool execution
- `UserPromptSubmit` — When user sends a message
- `SessionStart` / `SessionEnd` — Session lifecycle
- `Stop` / `SubagentStop` — When execution stops

Hook types: `command` (shell), `prompt` (LLM), `agent` (tools)

### 4. Distribution & Scope

- Who uses this? (Personal, team, community?)
- Installation scope: `user`, `project`, `local`, or `managed`?
- Needs marketplace distribution?

### 5. Simplicity Check

- What's the minimum that solves the problem?
- Can one component type handle it, or multiple needed?
- YAGNI: What can we remove and still succeed?

## Exploring Approaches

Before presenting a design, propose 2-3 approaches with trade-offs.

**How to present options:**
- Lead with your recommended approach and explain why
- Present options conversationally, not as a dry list
- Include concrete trade-offs for each approach
- For plugins: trade-offs often involve component choice

**Example:**
> "I'd recommend a **Skill + Command** combination. The Skill gives Claude
> the knowledge automatically, and the Command lets users invoke it explicitly
> when needed.
>
> Alternative approaches:
> - **Agent only**: More isolated, but overkill if we don't need separate context
> - **Hook-based**: Would run automatically, but you said this should be optional"

## Presenting the Design

Once you've agreed on an approach, present the design incrementally.

### Structure

Present in 200-300 word sections. After each section, ask: "Does this look right so far?"

Sections to cover:
1. **Problem & Users** — What it solves, who uses it
2. **Component Architecture** — Which components, why each one
3. **Trigger Strategy** — How/when things activate
4. **Data Flow** — How components interact (if multiple)
5. **Error Handling** — What can go wrong, how to handle it
6. **Testing approach** — How to verify it works

Be ready to go back and clarify if something doesn't make sense.

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<plugin-name>-design.md`
- Use `elements-of-style:writing-clearly-and-concisely` skill if available
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use `superpowers:using-git-worktrees` to create isolated workspace
- Use `superpowers:writing-plans` for detailed implementation plan
- Or use `/plugin-dev:create-plugin` for guided implementation

## Key Principles

- **One question at a time** — Don't overwhelm with multiple questions
- **Multiple choice preferred** — Easier to answer than open-ended when possible
- **Explore alternatives** — Always propose 2-3 approaches before settling
- **YAGNI ruthlessly** — Remove unnecessary features from all designs
- **Incremental validation** — Present design in sections, validate each
- **Be flexible** — Go back and clarify when something doesn't make sense
```

**Step 2: Verify frontmatter is valid**

Run: `head -10 plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md`
Expected: Shows YAML frontmatter with `name` and `description`

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md
git commit -m "feat(plugin-dev): add brainstorming-plugins skill"
```

---

## Task 4: Create Component Decision Guide

**Files:**
- Create: `plugins/plugin-dev/skills/brainstorming-plugins/references/component-decision-guide.md`

**Step 1: Create the reference file**

```markdown
# Plugin Component Decision Guide

Detailed guidance for selecting the right plugin components.

## Component Comparison Matrix

| Aspect | Skill | Command | Agent | Hook | MCP | LSP |
|--------|-------|---------|-------|------|-----|-----|
| **Invoked by** | Claude (automatic) | User (`/cmd`) | Claude or user | Events | Claude (as tool) | Claude (as tool) |
| **Context** | Shared | Shared | Separate | N/A | Shared | Shared |
| **Purpose** | Knowledge | Actions | Isolated tasks | Guarantees | External tools | Code intelligence |
| **Trigger** | Description match | Explicit | Task match | Event fires | Tool call | File type |

## Decision Flowchart

```
Does Claude need specialized KNOWLEDGE?
├─ Yes → Skill
└─ No → Does the USER invoke something explicitly?
         ├─ Yes → Command
         └─ No → Needs SEPARATE CONTEXT or different tools?
                  ├─ Yes → Agent
                  └─ No → Must ALWAYS happen on an event?
                           ├─ Yes → Hook
                           └─ No → External API/service needed?
                                    ├─ Yes → MCP Server
                                    └─ No → Language-specific code intelligence?
                                             ├─ Yes → LSP Server
                                             └─ No → Reconsider the problem
```

## Common Patterns

### Knowledge + Explicit Action
**Components:** Skill + Command
**Use when:** Claude should know something AND user wants explicit invocation
**Example:** Code review guidelines (Skill) + `/review` command

### Automated Validation
**Components:** Hook (command or prompt type)
**Use when:** Something must ALWAYS happen after specific tool use
**Example:** Lint after Write/Edit operations

### Complex Autonomous Task
**Components:** Agent + Skills (via `skills:` field)
**Use when:** Task needs isolation, different tools, or extensive autonomy
**Example:** Security audit agent with restricted tools

### External Integration
**Components:** MCP Server + Skill
**Use when:** Need external API AND Claude needs to know how to use it well
**Example:** Database MCP + query patterns Skill

## Anti-Patterns to Avoid

| Don't Do This | Do This Instead |
|---------------|-----------------|
| Agent when you just need knowledge | Use a Skill |
| Hook for optional behavior | Use a Skill with guidance |
| Multiple components when one suffices | Start minimal, add if needed |
| MCP for local file operations | Use built-in tools |
| Skill for explicit user actions | Use a Command |

## Implementation Notes

### Portable Paths

When designing plugins with hooks or MCP servers, always use `${CLAUDE_PLUGIN_ROOT}`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
      }]
    }]
  }
}
```

### Directory Structure Rule

Components go at plugin root, NOT inside `.claude-plugin/`:

```
my-plugin/
├── .claude-plugin/plugin.json  ← Only manifest here
├── commands/                   ← At root
├── skills/                     ← At root
├── agents/                     ← At root
└── hooks/                      ← At root
```

### Hook Events Reference

| Event | When it fires |
|-------|---------------|
| `PreToolUse` | Before Claude uses any tool |
| `PostToolUse` | After successful tool use |
| `PostToolUseFailure` | After tool execution fails |
| `UserPromptSubmit` | When user sends a message |
| `SessionStart` | At session beginning |
| `SessionEnd` | At session end |
| `Stop` | When Claude attempts to stop |
| `SubagentStop` | When a subagent attempts to stop |
| `PreCompact` | Before conversation history compaction |

### Hook Types

| Type | Use for |
|------|---------|
| `command` | Shell scripts, deterministic operations |
| `prompt` | LLM evaluation, flexible decisions |
| `agent` | Complex verification with tool access |
```

**Step 2: Verify file exists**

Run: `ls -la plugins/plugin-dev/skills/brainstorming-plugins/references/`
Expected: Shows `component-decision-guide.md`

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/brainstorming-plugins/references/component-decision-guide.md
git commit -m "feat(plugin-dev): add component decision guide reference"
```

---

## Task 5: Verify Plugin Structure

**Files:**
- Verify: `plugins/plugin-dev/` structure

**Step 1: Check complete structure**

Run: `find plugins/plugin-dev/skills/brainstorming-plugins plugins/plugin-dev/commands/brainstorm.md -type f 2>/dev/null | sort`

Expected output:
```
plugins/plugin-dev/commands/brainstorm.md
plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md
plugins/plugin-dev/skills/brainstorming-plugins/references/component-decision-guide.md
```

**Step 2: Verify skill is discoverable**

Run: `grep -l "brainstorming-plugins" plugins/plugin-dev/skills/*/SKILL.md`
Expected: `plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md`

---

## Task 6: Update Plugin README (Optional)

**Files:**
- Modify: `plugins/plugin-dev/README.md`

**Step 1: Add brainstorm command to README**

Add to the Commands section:
```markdown
| `/brainstorm` | Design a plugin through collaborative dialogue |
```

Add to the Skills section:
```markdown
| `brainstorming-plugins` | Plugin design through dialogue |
```

**Step 2: Commit**

```bash
git add plugins/plugin-dev/README.md
git commit -m "docs(plugin-dev): add brainstorm to README"
```

---

## Task 7: Final Commit and Summary

**Step 1: Verify all changes committed**

Run: `git status`
Expected: `nothing to commit, working tree clean`

**Step 2: View commit history**

Run: `git log --oneline -5`
Expected: Shows commits for command, skill, reference, and docs

**Step 3: Summary**

Files created:
- `plugins/plugin-dev/commands/brainstorm.md` — Command wrapper
- `plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md` — Main skill
- `plugins/plugin-dev/skills/brainstorming-plugins/references/component-decision-guide.md` — Decision framework

Usage:
- Explicit: `/plugin-dev:brainstorm`
- Automatic: Say "design a plugin for X" or "create a plugin"
