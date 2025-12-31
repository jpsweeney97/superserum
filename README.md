# Claude Code Plugin Development

A monorepo for developing and maintaining Claude Code plugins. Contains four production plugins plus official documentation.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| **[plugin-dev](plugins/plugin-dev/)** | 1.4.0 | Plugin development toolkit with 12 skills, validation scripts, and guided workflows |
| **[superpowers](plugins/superpowers/)** | 4.0.3 | Development workflows: TDD, debugging, planning, code review (fork of [obra/superpowers](https://github.com/obra/superpowers)) |
| **[doc-auditor](plugins/doc-auditor/)** | 1.0.0 | Documentation auditing with 15 issue categories and interactive repair |
| **[deep-analysis](plugins/deep-analysis/)** | 0.1.0 | Structured decision analysis with MCP-powered semantic search |

## Quick Start

### Install a Plugin

```bash
# From the marketplace (when published)
/install plugin-dev

# For local development
claude --plugin-dir ./plugins/plugin-dev
```

### Use Multiple Plugins

```bash
claude --plugin-dir ./plugins/plugin-dev \
       --plugin-dir ./plugins/superpowers \
       --plugin-dir ./plugins/doc-auditor
```

### Key Commands

```bash
# Create a new plugin with guided workflow
/plugin-dev:create-plugin

# Audit an existing plugin
/plugin-dev:audit-plugin path/to/plugin

# Scan documentation for issues
/doc-auditor:scan path/to/docs

# Start a structured analysis session
/deep-analysis:analyze
```

## Architecture

```
├── plugins/
│   ├── plugin-dev/           # Plugin development toolkit
│   │   ├── commands/         # create, audit, fix, optimize, brainstorm
│   │   ├── agents/           # creator, validator, reviewer
│   │   └── skills/           # 12 skills with examples and scripts
│   │
│   ├── superpowers/          # Workflow skills
│   │   ├── commands/         # brainstorm, write-plan, execute-plan
│   │   └── skills/           # 14 workflow skills
│   │
│   ├── doc-auditor/          # Documentation auditing
│   │   ├── commands/         # report, scan, fix
│   │   └── agents/           # coherence-analyzer, issue-detector
│   │
│   └── deep-analysis/        # Decision analysis
│       ├── mcp/              # Python MCP server (txtai)
│       └── skills/           # 6 analytical frameworks
│
└── docs/
    └── claude-code-documentation/   # Official Claude Code docs
```

## Plugin Highlights

### plugin-dev

The toolkit for building Claude Code plugins:

- **12 skills** covering hooks, MCP, commands, agents, settings, validation, brainstorming, and SkillForge
- **50+ validation rules** with severity ratings (CRITICAL/WARNING/INFO)
- **Utility scripts** for schema validation, hook testing, and linting
- **Guided workflows** for plugin creation, repair, and design exploration

```bash
# Validate a hooks.json file
./plugins/plugin-dev/skills/hook-development/scripts/validate-hook-schema.sh hooks.json

# Test a hook with sample input
./plugins/plugin-dev/skills/hook-development/scripts/test-hook.sh my-hook.sh input.json
```

### superpowers

Development workflow enforcement:

- **TDD methodology** with test-first verification
- **Systematic debugging** requiring root cause analysis before fixes
- **Plan execution** with review checkpoints
- **Code review** protocols for both giving and receiving feedback

### doc-auditor

Documentation quality assurance:

- **15 issue categories**: broken links, outdated content, inconsistencies, accessibility
- **Coherence analysis**: understand what documentation describes as a unified design
- **Interactive repair**: guided fixes with before/after comparison

### deep-analysis

Structured decision-making:

- **6 analytical frameworks**: trade-offs, architecture, risk, stakeholders, complexity, maintainability
- **MCP server**: semantic search over past analyses using txtai
- **Persistent index**: build organizational knowledge over time

## Dependencies

| Component | Requirements |
|-----------|--------------|
| All plugins | Claude Code |
| deep-analysis MCP | Python 3.12+, uv, mcp>=1.0.0, txtai>=7.0.0 |
| Hook scripts | Bash, jq |

### Setting Up deep-analysis MCP

```bash
cd plugins/deep-analysis/mcp
uv sync                    # Install dependencies
uv run python -m server    # Test locally
```

## Documentation

Official Claude Code documentation is in `docs/claude-code-documentation/`:

- [Plugins Overview](docs/claude-code-documentation/plugins-overview.md)
- [Skills Reference](docs/claude-code-documentation/skills-overview.md)
- [Hooks Guide](docs/claude-code-documentation/hooks-overview.md)
- [Subagents](docs/claude-code-documentation/subagents-overview.md)

## Development

### Plugin Structure

```
plugin-name/
├── .claude-plugin/plugin.json    # Required manifest
├── commands/                     # Slash commands (markdown)
├── agents/                       # Agent definitions
├── skills/                       # SKILL.md + resources
├── hooks/hooks.json              # Event handlers
└── .mcp.json                     # MCP server config
```

### Key Conventions

- Use `${CLAUDE_PLUGIN_ROOT}` for portable paths in hooks and MCP configs
- Structure skills with progressive disclosure: metadata → SKILL.md → references/
- Store plugin settings in `.claude/plugin-name.local.md`
- Write strong trigger phrases in skill descriptions

### Running Validation

```bash
# Audit any plugin
/plugin-dev:audit-plugin ./plugins/my-plugin

# Or use the validation scripts directly
./plugins/plugin-dev/skills/hook-development/scripts/validate-hook-schema.sh path/to/hooks.json
./plugins/plugin-dev/skills/agent-development/scripts/validate-agent.sh path/to/agent.md
```

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make changes following the plugin conventions above
4. Run `/plugin-dev:audit-plugin` on modified plugins
5. Submit a pull request

## License

- **plugin-dev**, **doc-auditor**, **deep-analysis**: MIT
- **superpowers**: MIT (fork of [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
