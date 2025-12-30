# Contributing

Thanks for your interest in contributing to this plugin collection. This guide covers the workflow, conventions, and quality standards for contributions.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/claude-code-plugin-development.git
cd claude-code-plugin-development

# 2. Create a feature branch
git checkout -b feat/your-feature-name

# 3. Make changes, then validate
claude --plugin-dir ./plugins/plugin-dev
/plugin-dev:audit-plugin ./plugins/your-plugin

# 4. Commit and push
git add .
git commit -m "feat(plugin-name): add new capability"
git push origin feat/your-feature-name

# 5. Open a pull request
```

## Local Development Setup

Claude Code caches installed plugins for performance. During active development, this cache can become stale—your edits won't be visible until you clear it. This section covers the recommended setup for plugin development.

### Development Modes

| Mode | Command | Use When |
|------|---------|----------|
| Development | `claude-dev` | Actively editing plugin code |
| Normal | `claude` | Using plugins without modification |

### Initial Setup

#### 1. Symlink Plugins to ~/.claude/plugins/

This lets you use the plugins in normal `claude` sessions while keeping the source in the repo:

```bash
# Remove any existing directories (not symlinks)
rm -rf ~/.claude/plugins/plugin-dev ~/.claude/plugins/doc-auditor ~/.claude/plugins/deep-analysis

# Create symlinks
ln -s ~/Projects/active/claude-code-plugin-development/plugins/plugin-dev ~/.claude/plugins/plugin-dev
ln -s ~/Projects/active/claude-code-plugin-development/plugins/doc-auditor ~/.claude/plugins/doc-auditor
ln -s ~/Projects/active/claude-code-plugin-development/plugins/deep-analysis ~/.claude/plugins/deep-analysis
```

#### 2. Add the claude-dev Alias

Add to your shell config (`~/.zshrc` or `~/.config/zsh/aliases.zsh`):

```bash
alias claude-dev='claude --plugin-dir ~/Projects/active/claude-code-plugin-development/plugins/plugin-dev --plugin-dir ~/Projects/active/claude-code-plugin-development/plugins/doc-auditor --plugin-dir ~/Projects/active/claude-code-plugin-development/plugins/deep-analysis'
```

Then reload: `exec zsh`

### Development Workflow

```
┌──────────────────────────────────────────┐
│  $ claude-dev                            │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│  Test your plugin                        │
│  /plugin-dev:audit-plugin ./my-plugin    │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│  Edit source files                       │
│  (in repo, IDE, or same session)         │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│  Test again — changes visible instantly  │
│  (no restart, no cache clear)            │
└──────────────────────────────────────────┘
```

### Why This Works

- **`claude-dev`** uses `--plugin-dir` which bypasses the cache entirely, reading plugin files directly from disk
- **`claude`** (normal mode) uses installed plugins from `~/.claude/plugins/`, which are cached at `~/.claude/plugins/cache/`

### Clearing Cache (Normal Mode)

If you use normal `claude` after making changes, clear stale cache:

```bash
rm -rf ~/.claude/plugins/cache/jp-local
```

Claude will rebuild the cache from your symlinked sources on next session.

## What We Accept

| Contribution Type | Guidelines |
|-------------------|------------|
| Bug fixes | Include steps to reproduce, fix, and verification |
| New skills | Must follow progressive disclosure pattern |
| New commands | Include usage examples in command file |
| New agents | Use validate-agent.sh before submitting |
| Documentation | Keep it concise; update CHANGELOG.md |
| New plugins | Discuss in an issue first |

## Branch Naming

```
feat/description     # New features
fix/description      # Bug fixes
docs/description     # Documentation only
refactor/description # Code restructuring
```

Keep branch names lowercase, hyphenated, under 50 characters.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

# Examples:
feat(plugin-dev): add new validation rule for hooks
fix(superpowers): correct TDD skill trigger phrase
docs(deep-analysis): update MCP setup instructions
refactor(doc-auditor): simplify issue detection logic
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Scope:** Plugin name or component (e.g., `plugin-dev`, `superpowers`, `hooks`, `mcp`)

## Code Standards

### Plugin Structure

Every plugin must have:

```
plugin-name/
├── .claude-plugin/plugin.json    # Required: name, version, description
├── README.md                     # Required: overview and usage
└── [components]                  # commands/, agents/, skills/, hooks/, .mcp.json
```

### Manifest Requirements

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Clear, concise description under 120 chars",
  "author": { "name": "Your Name" }
}
```

### Skills

- **SKILL.md**: Self-contained, under 2000 words
- **Description**: Start with "Use when..." and include specific trigger phrases
- **Progressive disclosure**: Core content in SKILL.md, details in `references/`
- **No external dependencies**: Skills must work without fetching remote content

### Commands

- **Frontmatter**: Include `description` and `allowed-tools` if restricting
- **Arguments**: Document with `argument-hint` field
- **Examples**: Show common usage patterns in the command body

### Hooks

- **Portable paths**: Use `${CLAUDE_PLUGIN_ROOT}`, never absolute paths
- **Timeouts**: Always specify (default: 30000ms)
- **Validation**: Run `validate-hook-schema.sh` before submitting

### Agents

- **Description format**: Include `<example>` blocks for reliable triggering
- **Tool restrictions**: Specify minimal required tools
- **Validation**: Run `validate-agent.sh` before submitting

## Validation Checklist

Before submitting a PR, run these checks:

```bash
# Audit the plugin (catches 50+ issues)
/plugin-dev:audit-plugin ./plugins/your-plugin

# Validate specific components
./plugins/plugin-dev/skills/hook-development/scripts/validate-hook-schema.sh path/to/hooks.json
./plugins/plugin-dev/skills/agent-development/scripts/validate-agent.sh path/to/agent.md

# Test hooks with sample input
./plugins/plugin-dev/skills/hook-development/scripts/test-hook.sh your-hook.sh test-input.json
```

All validation must pass with no CRITICAL issues.

## Pull Request Process

1. **Title**: Use conventional commit format (`feat(scope): description`)

2. **Description**: Include:
   - What changed and why
   - How to test the changes
   - Screenshots/examples if applicable

3. **Checklist**:
   ```
   - [ ] Ran /plugin-dev:audit-plugin with no CRITICAL issues
   - [ ] Updated CHANGELOG.md
   - [ ] Updated relevant README if adding features
   - [ ] Tested changes locally with claude --plugin-dir
   ```

4. **Review**: Address feedback promptly; we aim for quick turnaround

## Testing Your Changes

See [Local Development Setup](#local-development-setup) for the full workflow. Quick reference:

```bash
# Development mode (live reload)
claude-dev

# Or load specific plugins manually
claude --plugin-dir ./plugins/your-plugin

# Debug mode
claude --debug --plugin-dir ./plugins/your-plugin
```

## Adding a New Plugin

1. **Open an issue first** to discuss the plugin's purpose and scope
2. **Use the guided workflow**:
   ```bash
   claude --plugin-dir ./plugins/plugin-dev
   /plugin-dev:create-plugin
   ```
3. **Follow the 8-phase process**: Discovery → Planning → Design → Structure → Implementation → Validation → Testing → Documentation
4. **Ensure no overlap** with existing plugins' functionality

## Updating Dependencies

### deep-analysis MCP Server

```bash
cd plugins/deep-analysis/mcp
uv add package-name    # Add dependency
uv lock                # Update lockfile
uv sync                # Install
```

### Documentation

When updating official Claude Code documentation in `docs/claude-code-documentation/`:
- Keep formatting consistent with existing files
- Note the source/version if pulling from official docs
- Don't modify upstream content without clear reason

## Releasing

Each plugin maintains independent versioning. Use the release script to ensure all version references stay in sync.

### Release Process

```bash
# 1. Preview what will change (recommended first step)
./scripts/release.sh plugin-dev 1.3.0 --dry-run

# 2. Run the release
./scripts/release.sh plugin-dev 1.3.0

# 3. Edit CHANGELOG.md to fill in release notes
# 4. Amend the commit with your changes
git commit --amend

# 5. Push with tags
git push origin main --tags
```

### What the Script Does

1. **Validates** plugin name, semver format, and preconditions
2. **Updates** version in all locations:
   - `plugins/<name>/.claude-plugin/plugin.json`
   - `plugins/<name>/README.md` (if has `## Version` section)
   - `README.md` (root version table)
   - `CHANGELOG.md` (new section + version table)
   - `plugins/<name>/mcp/pyproject.toml` (deep-analysis only)
3. **Creates** a commit and tag

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying |
| `--yes` | Skip confirmation prompt |
| `--force` | Allow dirty tree, same version, etc. |
| `--verbose` | Show detailed output |

### Version Guidelines

- Follow [Semantic Versioning](https://semver.org/)
- **Major (X.0.0)**: Breaking changes, removed features
- **Minor (x.Y.0)**: New features, backwards compatible
- **Patch (x.y.Z)**: Bug fixes, documentation updates

### Tag Format

Tags follow the pattern `<plugin>-v<version>`:
- `plugin-dev-v1.3.0`
- `superpowers-v4.1.0`
- `deep-analysis-v0.2.0`

## Getting Help

- **Questions**: Open a GitHub issue with the `question` label
- **Bugs**: Open an issue with reproduction steps
- **Ideas**: Open an issue with the `enhancement` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
