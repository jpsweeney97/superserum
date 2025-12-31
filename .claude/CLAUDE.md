# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

- Claude Code plugin development monorepo with four plugins plus official documentation
- Each plugin extends Claude Code via skills, commands, agents, hooks, and/or MCP integrations
- Plugin-specific details in each plugin's README: @plugins/plugin-dev/README.md, @plugins/superpowers/README.md, @plugins/doc-auditor/README.md, @plugins/deep-analysis/README.md

## Plugins

| Plugin | Purpose |
|--------|---------|
| **plugin-dev** | Plugin development toolkit (12 skills, 6 commands, 50+ validation rules) |
| **superpowers** | Development workflow: TDD, brainstorming, planning, code review (14 skills) |
| **doc-auditor** | Documentation audit/repair with 15 issue categories |
| **deep-analysis** | Structured decision analysis with 6 frameworks and MCP semantic search |

## Commands

### Deep Analysis MCP Server

```bash
cd plugins/deep-analysis/mcp && uv sync     # Install dependencies
uv run python -m server                      # Test server locally
```

### Plugin Validation Scripts

```bash
# Validate hooks.json schema
./plugins/plugin-dev/skills/hook-development/scripts/validate-hook-schema.sh path/to/hooks.json

# Validate agent frontmatter
./plugins/plugin-dev/skills/agent-development/scripts/validate-agent.sh path/to/agent.md

# Test hook with sample input
./plugins/plugin-dev/skills/hook-development/scripts/test-hook.sh hook.sh input.json
```

### Plugin Development

```
/plugin-dev:create-plugin           # 8-phase guided creation workflow
/plugin-dev:create-skill            # SkillForge 5-phase skill creation
/plugin-dev:audit-plugin [path]     # Comprehensive validation (50+ rules)
/plugin-dev:fix-plugin [path]       # Interactive repair with auto-fixes
/plugin-dev:optimize-plugin [path]  # Six-lens improvement analysis
/plugin-dev:brainstorm              # Design exploration before implementation
```

## Architecture

```
plugins/
├── plugin-dev/           # Plugin development toolkit
│   ├── .claude-plugin/plugin.json
│   ├── commands/         # create-plugin, create-skill, audit, fix, optimize, brainstorm
│   ├── agents/           # creator, reviewer, validator
│   └── skills/           # 12 skills with references/, examples/, scripts/
├── superpowers/          # Workflow skills (obra/superpowers fork)
│   ├── commands/         # brainstorm, write-plan, execute-plan
│   └── skills/           # 14 workflow skills
├── doc-auditor/          # Documentation auditing
│   ├── commands/         # report, scan, repair
│   └── hooks/            # Optional pre-commit validation
└── deep-analysis/        # Decision analysis + MCP
    ├── .mcp.json         # MCP server config
    ├── mcp/              # Python server (txtai, mcp>=1.0)
    └── skills/           # 6 analytical frameworks
```

## Plugin Conventions

### Standard Directory Structure

```
plugin-name/
├── .claude-plugin/plugin.json    # Required: name, version, description
├── commands/                     # Markdown with YAML frontmatter
├── agents/                       # Agent definitions
├── skills/                       # SKILL.md + references/
├── hooks/hooks.json              # Event handlers (optional)
└── .mcp.json                     # MCP server config (optional)
```

### Key Patterns

- **Portable paths**: Always use `${CLAUDE_PLUGIN_ROOT}` in hooks.json and .mcp.json, never absolute paths
- **Progressive disclosure**: Skills structure as metadata → SKILL.md → references/examples/scripts
- **Settings files**: Store plugin config in `.claude/plugin-name.local.md` (YAML frontmatter + markdown)
- **Trigger phrases**: Write strong, specific trigger phrases in skill descriptions for reliable activation

### Manifest Format

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Concise description",
  "author": { "name": "Author Name" },
  "commands": "./commands/",
  "agents": "./agents/"
}
```

## Critical Constraints

### Plugin Isolation

Claude Code copies plugins to a cache directory. Installed plugins cannot access files outside their root—path traversal fails silently. Each plugin must be self-contained.

**Workaround**: Symlinks are followed during copy. To share code between plugins, symlink it into each plugin directory.

### Path Portability

Use `${CLAUDE_PLUGIN_ROOT}` for all paths in:
- `hooks/hooks.json` (script commands)
- `.mcp.json` (server commands, args, env, cwd)
- `plugin.json` (custom component paths)

Absolute paths break after installation.

### Directory Structure

Only `plugin.json` belongs in `.claude-plugin/`. Place all other directories at the plugin root:

```
plugin-name/
├── .claude-plugin/plugin.json   ← manifest only
├── commands/                    ← at root
├── agents/                      ← at root
├── skills/                      ← at root
├── hooks/                       ← at root
└── .mcp.json                    ← at root
```

Components inside `.claude-plugin/` will not load.

## Development Workflow

### Testing

```bash
claude --plugin-dir ./plugins/my-plugin    # Load plugin for testing
claude --debug                              # Debug loading issues
```

### Validation Checklist

| Component | Required |
|-----------|----------|
| Skills | `name` and `description` in SKILL.md frontmatter |
| Agents | `description` field with `<example>` blocks |
| Hooks | Executable scripts (`chmod +x`); case-sensitive event names |
| Commands | `description` in frontmatter |

### Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Plugin won't load | Invalid JSON | Validate `plugin.json` syntax |
| Commands missing | Wrong location | Move `commands/` to plugin root |
| Hooks don't fire | Script not executable | Run `chmod +x script.sh` |
| MCP server fails | Absolute path | Use `${CLAUDE_PLUGIN_ROOT}` |

## Versioning

Update version in all locations:
1. `.claude-plugin/plugin.json`
2. `README.md`
3. `CHANGELOG.md`
4. `pyproject.toml` (if Python MCP server)

Run `scripts/release.sh plugin-name X.Y.Z` for atomic updates.

## Installation Scopes

| Scope | File | Purpose |
|-------|------|---------|
| `user` | `~/.claude/settings.json` | Personal plugins |
| `project` | `.claude/settings.json` | Team plugins (committed to VCS) |
| `local` | `.claude/settings.local.json` | Project-specific (gitignored) |

## Documentation

Official Claude Code documentation: @docs/claude-code-documentation/plugins-overview.md

- Plugins: `docs/claude-code-documentation/plugins-*.md`
- Skills: `docs/claude-code-documentation/skills-*.md`, `skill-best-practices.md`
- Hooks: `docs/claude-code-documentation/hooks-*.md`
- Subagents: `docs/claude-code-documentation/subagents-overview.md`

## Dependencies

- **deep-analysis MCP**: Python 3.12+, uv, mcp>=1.0.0, txtai>=7.0.0
- **Hook scripts**: Bash, jq
- **All plugins**: Claude Code

## Documentation Lifecycle

### Plan Documents (`docs/plans/`)

**Naming:** `YYYY-MM-DD-description.md`

**Lifecycle states:**

| State | Meaning | Action |
|-------|---------|--------|
| **Active** | Being implemented or still relevant | None |
| **Superseded** | Replaced by newer approach | Add marker (see below) |
| **Archived** | Historical reference only | Move to `docs/plans/archive/` (optional) |

**Superseded marker format:**

```markdown
> **⚠️ SUPERSEDED (YYYY-MM-DD):** [Brief reason]
>
> - Replacement: [link to new doc/code]
>
> *Original preserved for historical reference.*
```

**When to supersede vs delete:**

| Action | When |
|--------|------|
| **Supersede** | Decision history is valuable (why we changed approach) |
| **Delete** | Trivial plans, false starts with no lessons learned |

**After implementation:** Mark completed plans as superseded, pointing to the implemented code or documentation.
