# superserum

Plugins that enhance Claude Code capabilities.

## Installation

Add the marketplace:

```
/plugin marketplace add jpsweeney97/superserum
```

Install plugins:

```
/plugin install plugin-dev@superserum
/plugin install deep-analysis@superserum
/plugin install doc-auditor@superserum
/plugin install ecosystem-builder@superserum
```

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| **[plugin-dev](plugins/plugin-dev/)** | 1.4.0 | Plugin development toolkit with validation, creation, and optimization |
| **[deep-analysis](plugins/deep-analysis/)** | 0.1.0 | Structured decision analysis with MCP semantic search |
| **[doc-auditor](plugins/doc-auditor/)** | 1.0.0 | Documentation auditing with 15 issue categories |
| **[ecosystem-builder](plugins/ecosystem-builder/)** | 0.1.0 | Multi-project orchestration for Claude Code |

## Plugin Highlights

### plugin-dev

The toolkit for building Claude Code plugins:

- **12 skills** covering hooks, MCP, commands, agents, settings, validation, and SkillForge
- **50+ validation rules** with severity ratings (CRITICAL/WARNING/INFO)
- **Utility scripts** for schema validation, hook testing, and linting
- **Guided workflows** for plugin creation, repair, and design exploration

```
/plugin-dev:create-plugin           # 8-phase guided creation
/plugin-dev:audit-plugin [path]     # Comprehensive validation
/plugin-dev:fix-plugin [path]       # Interactive repair
```

### deep-analysis

Structured decision-making:

- **6 analytical frameworks**: trade-offs, architecture, risk, stakeholders, complexity, maintainability
- **MCP server**: semantic search over past analyses using txtai
- **Persistent index**: build organizational knowledge over time

```
/deep-analysis:analyze              # Start analysis session
```

### doc-auditor

Documentation quality assurance:

- **15 issue categories**: broken links, outdated content, inconsistencies, accessibility
- **Coherence analysis**: understand what documentation describes as a unified design
- **Interactive repair**: guided fixes with before/after comparison

```
/doc-auditor:scan path/to/docs      # Scan for issues
/doc-auditor:repair                 # Interactive repair
```

### ecosystem-builder

Multi-project orchestration:

- **Project registry**: track related repositories and their relationships
- **Cross-project coordination**: manage dependencies between projects
- **Orchestration agents**: coordinate work across multiple codebases

## Dependencies

| Component | Requirements |
|-----------|--------------|
| All plugins | Claude Code |
| deep-analysis MCP | Python 3.12+, uv, mcp>=1.0.0, txtai>=7.0.0 |
| ecosystem-builder | Python 3.12+, uv |
| Hook scripts | Bash, jq |

### Setting Up MCP Servers

```bash
# deep-analysis
cd plugins/deep-analysis/mcp
uv sync && uv run python -m server
```

### Setting Up ecosystem-builder

```bash
cd plugins/ecosystem-builder
uv sync
```

## Development

### Local Testing

```bash
claude --plugin-dir ./plugins/plugin-dev    # Load single plugin
claude --debug                               # Debug loading issues
```

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
- Structure skills with progressive disclosure: metadata -> SKILL.md -> references/
- Store plugin settings in `.claude/plugin-name.local.md`
- Write strong trigger phrases in skill descriptions

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make changes following the plugin conventions
4. Run `/plugin-dev:audit-plugin` on modified plugins
5. Submit a pull request

## License

MIT

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
