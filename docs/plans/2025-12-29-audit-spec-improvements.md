# Audit Spec Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update audit-spec.yaml to align with official Claude Code documentation, eliminating false positives and adding missing validation rules.

**Architecture:** Modify the existing YAML specification file incrementally, organized by component type (hooks, agents, skills, LSP). Each task fixes one category of issues to keep changes reviewable.

**Tech Stack:** YAML specification format, validation rules derived from official Claude Code documentation.

---

## Task 1: Fix Hook Events and Types

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml:317-341`

**Step 1: Add missing hook events to valid_events list**

Add these three missing events documented in hooks-technical-reference.md:
- `PostToolUseFailure` - After Claude tool execution fails
- `PermissionRequest` - When permission dialog is shown
- `SubagentStart` - When a subagent is started

```yaml
    schema:
      valid_events:
        - PreToolUse
        - PostToolUse
        - PostToolUseFailure
        - PermissionRequest
        - Stop
        - SubagentStop
        - SubagentStart
        - SessionStart
        - SessionEnd
        - UserPromptSubmit
        - PreCompact
        - Notification
      evidence:
        source: "Claude Code Documentation - Hooks Technical Reference"
        quote: "Available events: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, Stop, SubagentStop, SubagentStart, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification"
        note: "Any other event name is silently ignored"
```

**Step 2: Add missing hook type `agent`**

Locate the `type` field validation (around line 351) and add `agent`:

```yaml
      type:
        rule_id: H-FIELD-002
        required: true
        severity: critical
        valid_values:
          - command
          - prompt
          - agent
        evidence:
          source: "Claude Code Documentation - Hooks Technical Reference"
          quote: "Hook types: command (execute shell commands), prompt (evaluate with LLM), agent (run agentic verifier with tools)"
```

**Step 3: Add hook description field**

Add new optional field for plugin hooks:

```yaml
      description:
        rule_id: H-FIELD-006
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Hooks Technical Reference"
          quote: "Plugin hooks use the same format as regular hooks with an optional description field"
        derivation: |
          Description field explains hook purpose. Optional but recommended for plugin hooks.
```

**Step 4: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 5: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "fix(audit-spec): add missing hook events and agent type"
```

---

## Task 2: Fix Agent Frontmatter Fields

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml:227-295`

**Step 1: Add `name` as required field**

The documentation shows `name` is required for agents. Add it before `description`:

```yaml
    frontmatter:
      fields:
        name:
          required: true
          severity: critical
          evidence:
            source: "Claude Code Documentation - Subagents Overview"
            quote: "name: Yes - Unique identifier using lowercase letters and hyphens"
          derivation: |
            Agent name is REQUIRED for identification in /agents interface.
          validation:
            pattern: "^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
            pattern_description: "lowercase letters and hyphens only"
            min_length: 2
            max_length: 64
```

**Step 2: Fix `tools` field - change to NOT required**

Change tools from required to optional (this is the critical false positive fix):

```yaml
        tools:
          required: false
          severity: info
          evidence:
            source: "Claude Code Documentation - Subagents Overview"
            quote: "Omit the tools field to inherit all tools from the main thread (default)"
          derivation: |
            Tools field is OPTIONAL. When omitted, agent inherits all tools
            from the parent context. Only specify when restricting access.
          validation:
            type: array_or_csv
            valid_values:
              - Read
              - Write
              - Edit
              - Glob
              - Grep
              - Bash
              - WebFetch
              - WebSearch
              - AskUserQuestion
              - TodoWrite
              - Task
              - NotebookEdit
              - Skill
              - KillShell
```

**Step 3: Add `permissionMode` field**

```yaml
        permissionMode:
          required: false
          severity: info
          evidence:
            source: "Claude Code Documentation - Subagents Overview"
            quote: "Permission mode for the subagent. Valid values: default, acceptEdits, bypassPermissions, plan, ignore"
          validation:
            valid_values:
              - default
              - acceptEdits
              - bypassPermissions
              - plan
              - ignore
```

**Step 4: Add `skills` field**

```yaml
        skills:
          required: false
          severity: info
          evidence:
            source: "Claude Code Documentation - Subagents Overview"
            quote: "Comma-separated list of skill names to auto-load when the subagent starts"
          derivation: |
            Subagents do not inherit Skills from parent conversation.
            Use this field to preload specific skills.
          validation:
            type: array_or_csv
```

**Step 5: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 6: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "fix(audit-spec): correct agent frontmatter - name required, tools optional"
```

---

## Task 3: Fix Skill Name and Description Constraints

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml:148-176`

**Step 1: Update skill `name` field with strict constraints**

Replace the permissive name validation with documented constraints:

```yaml
        name:
          required: true
          severity: critical
          evidence:
            source: "Claude Code Documentation - Skills Overview"
            quote: "name: Maximum 64 characters, must contain only lowercase letters, numbers, and hyphens, cannot contain XML tags, cannot contain reserved words: anthropic, claude"
          derivation: |
            Skill names have strict validation rules enforced by Claude Code.
            Using invalid names will cause skill loading to fail.
          validation:
            pattern: "^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
            pattern_description: "lowercase letters, numbers, and hyphens only"
            min_length: 1
            max_length: 64
            forbidden_patterns:
              - "anthropic"
              - "claude"
              - "<[^>]+>"
            forbidden_reason: "Reserved words and XML tags not allowed"
```

**Step 2: Update skill `description` field constraints**

```yaml
        description:
          required: true
          severity: critical
          evidence:
            source: "Claude Code Documentation - Skills Overview"
            quote: "description: Must be non-empty, maximum 1024 characters, cannot contain XML tags"
          derivation: |
            Description is the TRIGGERING MECHANISM for skills.
            Claude uses it to decide when to load the skill.
            Must follow strict formatting rules.
          validation:
            min_length: 10
            max_length: 1024
            should_contain_triggers: true
            forbidden_patterns:
              - "<[^>]+>"
            forbidden_reason: "XML tags not allowed in description"
```

**Step 3: Add new content rule for third-person descriptions**

Add to the skill content rules section:

```yaml
        - id: SK-DESC-002
          name: "Description uses third person"
          severity: warning
          description: "Description should be written in third person, not first or second person"
          evidence:
            source: "Claude Code Documentation - Skill Best Practices"
            quote: "Always write in third person. The description is injected into the system prompt."
          detection:
            patterns:
              - "^I can"
              - "^I will"
              - "^You can"
              - "^You should"
              - "\\bI help\\b"
            context_exemptions:
              - "within example blocks"
```

**Step 4: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 5: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "fix(audit-spec): add strict skill name/description validation per docs"
```

---

## Task 4: Add Skill Body Best Practice Rules

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml:184-226`

**Step 1: Update body length rule to use lines instead of words**

Replace the word-based check with line-based (per best practices doc):

```yaml
        - id: SK-BODY-002
          name: "Body length appropriate"
          severity: warning
          description: "SKILL.md body should not exceed 500 lines; move details to separate files"
          evidence:
            source: "Claude Code Documentation - Skill Best Practices"
            quote: "Keep SKILL.md body under 500 lines for optimal performance"
          detection:
            max_lines: 500
            recommended_lines: 300
```

**Step 2: Add rule for reference depth**

```yaml
        - id: SK-REF-001
          name: "References one level deep"
          severity: warning
          description: "Referenced files should be directly from SKILL.md, not nested"
          evidence:
            source: "Claude Code Documentation - Skill Best Practices"
            quote: "Keep references one level deep from SKILL.md... All reference files should link directly from SKILL.md"
          detection:
            check_reference_depth: true
            max_depth: 1
```

**Step 3: Add rule for table of contents in long files**

```yaml
        - id: SK-REF-002
          name: "Long reference files have TOC"
          severity: info
          description: "Reference files over 100 lines should have a table of contents"
          evidence:
            source: "Claude Code Documentation - Skill Best Practices"
            quote: "For reference files longer than 100 lines, include a table of contents at the top"
          detection:
            applies_to: "reference files over 100 lines"
            should_contain:
              - "## Contents"
              - "## Table of Contents"
```

**Step 4: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 5: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "feat(audit-spec): add skill body best practice rules from docs"
```

---

## Task 5: Add LSP Server Component Type

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml` (add after MCP section, ~line 430)

**Step 1: Add complete LSP component definition**

Add new component type after the `mcp` section:

```yaml
  lsp:
    description: "LSP servers (.lsp.json)"
    discovery:
      pattern: ".lsp.json"
      entry_file: ".lsp.json"

    schema:
      root_key: null  # Keys are language server names

    fields:
      command:
        rule_id: L-FIELD-001
        required: true
        severity: critical
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "command: The LSP binary to execute (must be in PATH)"
        validation:
          must_be_accessible: true

      extensionToLanguage:
        rule_id: L-FIELD-002
        required: true
        severity: critical
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "extensionToLanguage: Maps file extensions to language identifiers"
        validation:
          type: object
          key_pattern: "^\\.[a-z0-9]+$"

      args:
        rule_id: L-FIELD-003
        required: false
        severity: info
        validation:
          type: array

      transport:
        rule_id: L-FIELD-004
        required: false
        severity: info
        validation:
          valid_values:
            - stdio
            - socket
          default: stdio

      env:
        rule_id: L-FIELD-005
        required: false
        severity: info
        validation:
          type: object

      initializationOptions:
        rule_id: L-FIELD-006
        required: false
        severity: info

      settings:
        rule_id: L-FIELD-007
        required: false
        severity: info

      workspaceFolder:
        rule_id: L-FIELD-008
        required: false
        severity: info

      startupTimeout:
        rule_id: L-FIELD-009
        required: false
        severity: info
        validation:
          type: integer
          min: 1000

      shutdownTimeout:
        rule_id: L-FIELD-010
        required: false
        severity: info
        validation:
          type: integer
          min: 1000

      restartOnCrash:
        rule_id: L-FIELD-011
        required: false
        severity: info
        validation:
          type: boolean

      maxRestarts:
        rule_id: L-FIELD-012
        required: false
        severity: info
        validation:
          type: integer
          min: 0

      loggingConfig:
        rule_id: L-FIELD-013
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "Debug logging configuration enabled with --enable-lsp-logging"
        validation:
          type: object
          allowed_keys:
            - args
            - env
```

**Step 2: Add LSP to rule_id_prefixes**

Update the rule_id_prefixes section:

```yaml
rule_id_prefixes:
  S: "Structure"
  C: "Command"
  SK: "Skill"
  A: "Agent"
  H: "Hook"
  M: "MCP"
  L: "LSP"
  SEC: "Security"
  X: "Cross-cutting"
```

**Step 3: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "feat(audit-spec): add LSP server component validation"
```

---

## Task 6: Add Missing Plugin Manifest Fields

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml` (add new component or section for manifest validation)

**Step 1: Add manifest component type if not present**

Add plugin manifest validation (this may need to be added to a manifest section or created):

```yaml
  manifest:
    description: "Plugin manifest (.claude-plugin/plugin.json)"
    discovery:
      directory: ".claude-plugin"
      pattern: "plugin.json"
      entry_file: "plugin.json"

    fields:
      name:
        rule_id: MF-FIELD-001
        required: true
        severity: critical
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "name: Unique identifier (kebab-case, no spaces)"
        validation:
          pattern: "^[a-z][a-z0-9]*(-[a-z0-9]+)*$"

      version:
        rule_id: MF-FIELD-002
        required: false
        severity: warning
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "version: Semantic version"
        validation:
          pattern: "^\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9.]+)?$"

      description:
        rule_id: MF-FIELD-003
        required: false
        severity: warning
        validation:
          min_length: 10
          max_length: 500

      author:
        rule_id: MF-FIELD-004
        required: false
        severity: info
        validation:
          type: object
          allowed_keys:
            - name
            - email
            - url

      homepage:
        rule_id: MF-FIELD-005
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "homepage: Documentation URL"
        validation:
          pattern: "^https?://"

      repository:
        rule_id: MF-FIELD-006
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "repository: Source code URL"
        validation:
          pattern: "^https?://"

      license:
        rule_id: MF-FIELD-007
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "license: License identifier (MIT, Apache-2.0, etc.)"

      keywords:
        rule_id: MF-FIELD-008
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "keywords: Discovery tags"
        validation:
          type: array

      commands:
        rule_id: MF-FIELD-009
        required: false
        severity: info
        validation:
          type: string_or_array
          must_start_with: "./"

      agents:
        rule_id: MF-FIELD-010
        required: false
        severity: info
        validation:
          type: string_or_array
          must_start_with: "./"

      skills:
        rule_id: MF-FIELD-011
        required: false
        severity: info
        validation:
          type: string_or_array
          must_start_with: "./"

      hooks:
        rule_id: MF-FIELD-012
        required: false
        severity: info
        validation:
          type: string_or_object

      mcpServers:
        rule_id: MF-FIELD-013
        required: false
        severity: info
        validation:
          type: string_or_object

      lspServers:
        rule_id: MF-FIELD-014
        required: false
        severity: info
        evidence:
          source: "Claude Code Documentation - Plugins Technical Reference"
          quote: "lspServers: Language Server Protocol config"
        validation:
          type: string_or_object

      outputStyles:
        rule_id: MF-FIELD-015
        required: false
        severity: info
        validation:
          type: string_or_array
          must_start_with: "./"
```

**Step 2: Add MF prefix to rule_id_prefixes**

```yaml
rule_id_prefixes:
  S: "Structure"
  C: "Command"
  SK: "Skill"
  A: "Agent"
  H: "Hook"
  M: "MCP"
  L: "LSP"
  MF: "Manifest"
  SEC: "Security"
  X: "Cross-cutting"
```

**Step 3: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "feat(audit-spec): add plugin manifest field validation"
```

---

## Task 7: Update Meta and Documentation

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml:12-24`

**Step 1: Update last_verified date and add new sources**

```yaml
meta:
  version: "1.1.0"
  last_verified: "2025-12-29"
  verification_sources:
    - name: "Claude Code Documentation - Plugins Technical Reference"
      type: official
      authority: primary
      url: "https://code.claude.com/docs/en/plugins-reference"
    - name: "Claude Code Documentation - Skills Overview"
      type: official
      authority: primary
      url: "https://code.claude.com/docs/en/skills"
    - name: "Claude Code Documentation - Skill Best Practices"
      type: official
      authority: primary
      url: "https://code.claude.com/docs/en/skill-best-practices"
    - name: "Claude Code Documentation - Hooks Technical Reference"
      type: official
      authority: primary
      url: "https://code.claude.com/docs/en/hooks"
    - name: "Claude Code Documentation - Subagents Overview"
      type: official
      authority: primary
      url: "https://code.claude.com/docs/en/sub-agents"
    - name: "Anthropic Engineering Blog"
      type: official
      authority: secondary
    - name: "Claude Code Source (observed behavior)"
      type: empirical
      authority: tertiary
```

**Step 2: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/specification/audit-spec.yaml
git commit -m "docs(audit-spec): update version and verification sources"
```

---

## Summary of Changes

| Task | Type | Impact |
|------|------|--------|
| 1 | Bug fix | Prevents false negatives for valid hook events/types |
| 2 | Bug fix | **Critical** - Prevents false positives for valid agents |
| 3 | Bug fix | Prevents false negatives for invalid skill names |
| 4 | Enhancement | Adds best practice rules from official docs |
| 5 | New feature | Adds LSP server validation (missing component) |
| 6 | New feature | Adds manifest field validation |
| 7 | Documentation | Updates metadata and sources |

**Total commits:** 7
**Estimated time:** 30-45 minutes
