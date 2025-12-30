# Plugin Design: brainstorm-plugin

A plugin-focused brainstorming skill for designing Claude Code plugins through collaborative dialogue.

## Problem Statement

Plugin developers need to explore ideas before implementation. The existing `/create-plugin` command jumps straight to building. Developers lack a structured way to:

- Clarify what problem their plugin solves
- Choose between component types (Skills, Commands, Agents, Hooks, MCP, LSP)
- Validate design decisions before writing code

This skill fills the gap between "I have an idea" and "let's build it."

## Component Architecture

| Component | Type | Purpose |
|-----------|------|---------|
| `brainstorm.md` | Command | Explicit invocation via `/plugin-dev:brainstorm` |
| `brainstorming-plugins/SKILL.md` | Skill | Automatic trigger on "design a plugin", "create a plugin for X" |
| `references/component-decision-guide.md` | Reference | Decision framework, patterns, anti-patterns |

## File Structure

```
plugins/plugin-dev/
├── commands/
│   └── brainstorm.md
└── skills/
    └── brainstorming-plugins/
        ├── SKILL.md
        └── references/
            └── component-decision-guide.md
```

## Trigger Strategy

**Command**: `/plugin-dev:brainstorm` invokes the skill explicitly.

**Skill triggers** on phrases:
- "build a plugin"
- "create a plugin"
- "design a plugin for X"
- "what components do I need"

## The Brainstorming Process

### Phase 1: Understand the Idea

1. Check project context (existing plugins, patterns)
2. Ask one question at a time
3. Prefer multiple choice over open-ended questions
4. Focus on: purpose, users, constraints

### Phase 2: Explore Approaches

1. Propose 2-3 different approaches with trade-offs
2. Lead with your recommendation
3. Explain why each approach fits or doesn't fit

### Phase 3: Present the Design

1. Break design into 200-300 word sections
2. After each section, ask: "Does this look right?"
3. Cover: components, triggers, data flow, error handling
4. Revise sections that need clarification

### Phase 4: Document and Handoff

1. Write validated design to `docs/plans/YYYY-MM-DD-<name>-design.md`
2. Commit the design document
3. Offer implementation paths:
   - `/plugin-dev:create-plugin` for guided implementation
   - `superpowers:writing-plans` for detailed planning
   - `superpowers:using-git-worktrees` for isolated workspace

## Component Decision Framework

The skill guides users through these decisions:

| User Need | Best Component | Why |
|-----------|----------------|-----|
| Claude needs specialized knowledge | **Skill** | Loads on trigger phrases |
| User runs action explicitly | **Command** | `/plugin:action` invocation |
| Task needs separate context | **Agent** | Isolated execution |
| Something must always happen on event | **Hook** | Deterministic, guaranteed |
| External service integration | **MCP Server** | Provides tools for APIs |
| Language-specific code intelligence | **LSP Server** | Diagnostics, navigation |

### Decision Flowchart

```
Does Claude need specialized KNOWLEDGE?
├─ Yes → Skill
└─ No → Does the USER invoke something explicitly?
         ├─ Yes → Command
         └─ No → Needs SEPARATE CONTEXT?
                  ├─ Yes → Agent
                  └─ No → Must ALWAYS happen on event?
                           ├─ Yes → Hook
                           └─ No → External API needed?
                                    ├─ Yes → MCP Server
                                    └─ No → Language code intelligence?
                                             ├─ Yes → LSP Server
                                             └─ No → Reconsider the problem
```

### Common Patterns

**Knowledge + Explicit Action**: Skill + Command
- Claude knows the domain; user invokes when ready
- Example: Code review guidelines (Skill) + `/review` command

**Automated Validation**: Hook (command or prompt type)
- Something must always happen after specific tool use
- Example: Lint after Write/Edit operations

**Complex Autonomous Task**: Agent + Skills
- Task needs isolation or different tool access
- Example: Security audit agent with restricted tools

**External Integration**: MCP Server + Skill
- External API plus knowledge of how to use it well
- Example: Database MCP + query patterns Skill

### Anti-Patterns

| Don't Do This | Do This Instead |
|---------------|-----------------|
| Agent when you just need knowledge | Use a Skill |
| Hook for optional behavior | Use a Skill with guidance |
| Multiple components when one suffices | Start minimal, add if needed |
| MCP for local file operations | Use built-in tools |
| Skill for explicit user actions | Use a Command |

## Implementation Notes

### Portable Paths

When the design includes hooks or MCP servers, use `${CLAUDE_PLUGIN_ROOT}`:

```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
```

### Directory Structure Rule

Components go at plugin root, not inside `.claude-plugin/`:

```
my-plugin/
├── .claude-plugin/plugin.json  ← Only manifest here
├── commands/                   ← At root
├── skills/                     ← At root
└── hooks/                      ← At root
```

## Key Principles

- **One question at a time**: Don't overwhelm with multiple questions
- **Multiple choice preferred**: Easier than open-ended when possible
- **Explore alternatives**: Always propose 2-3 approaches before settling
- **YAGNI ruthlessly**: Remove unnecessary features from all designs
- **Incremental validation**: Present design in sections, validate each
- **Be flexible**: Go back and clarify when something doesn't make sense

## Files to Create

### 1. `commands/brainstorm.md`

```markdown
---
disable-model-invocation: true
---
Invoke the plugin-dev:brainstorming-plugins skill and follow it exactly as presented to you
```

### 2. `skills/brainstorming-plugins/SKILL.md`

See [Appendix A: SKILL.md Content](#appendix-a-skillmd-content).

### 3. `skills/brainstorming-plugins/references/component-decision-guide.md`

See [Appendix B: Component Decision Guide](#appendix-b-component-decision-guide).

## Integration Points

- **Output**: Design document at `docs/plans/YYYY-MM-DD-<name>-design.md`
- **Handoff**: `/plugin-dev:create-plugin`, `superpowers:writing-plans`, `superpowers:using-git-worktrees`
- **Uses**: `elements-of-style:writing-clearly-and-concisely` for document writing

---

## Appendix A: SKILL.md Content

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

---

## Appendix B: Component Decision Guide

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
