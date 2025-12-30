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

| User Need                          | Component      | Why                              |
| ---------------------------------- | -------------- | -------------------------------- |
| "Claude needs to know about X"     | **Skill**      | Knowledge that loads on trigger  |
| "User runs action X explicitly"    | **Command**    | `/plugin:action` invocation      |
| "Delegate to separate context"     | **Agent**      | Isolated execution, custom tools |
| "X must ALWAYS happen on event Y"  | **Hook**       | Deterministic, guaranteed        |
| "Connect to external service X"    | **MCP Server** | Provides tools for external APIs |
| "Code intelligence for language X" | **LSP Server** | Diagnostics, go-to-definition    |

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
>
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
- Use `elements-of-style:writing-clearly-and-concisely` skill
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
