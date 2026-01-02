# Superserum Marketplace Design

> **⚠️ SUPERSEDED (2026-01-02):** Implemented
>
> - Replacement: PR #5 https://github.com/jpsweeney97/superserum/pull/5
>
> *Original preserved for historical reference.*

**Date:** 2026-01-02
**Status:** Implemented

## Summary

Rename this repository to `superserum` and restructure it as a public plugin marketplace for Claude Code.

## Decisions

| Decision | Choice |
|----------|--------|
| Repository name | `superserum` |
| Distribution | Public GitHub marketplace |
| Versioning | SemVer strict |
| Categories | None (flat structure with keywords) |
| Metadata | Standard: name, description, version, keywords, author, license, homepage |

## Plugin Lineup

| Plugin | Version | Description |
|--------|---------|-------------|
| `plugin-dev` | 1.4.0 | Plugin development toolkit: validation, creation, optimization |
| `deep-analysis` | 0.1.0 | Structured decision analysis with MCP semantic search |
| `doc-auditor` | 1.0.0 | Documentation audit and repair |
| `ecosystem-builder` | 0.1.0 | Multi-project orchestration |
| `persistent-tasks` | 0.1.0 | Cross-session task persistence |

**Excluded:**
- `plugins/superpowers/` — Fork of obra's marketplace. Users install the official version.
- `docs-kb` — Lives in a separate repository.

## Marketplace Structure

**File:** `.claude-plugin/marketplace.json`

```json
{
  "name": "superserum",
  "owner": {
    "name": "JP Sweeney"
  },
  "metadata": {
    "description": "Plugins that enhance Claude Code capabilities",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "plugin-dev",
      "source": "plugin-dev",
      "description": "Plugin development toolkit: validation, creation, optimization",
      "version": "1.4.0",
      "keywords": ["development", "validation", "skills", "commands", "agents"],
      "author": { "name": "JP Sweeney" },
      "license": "MIT",
      "homepage": "https://github.com/jpsweeney97/superserum/tree/main/plugins/plugin-dev"
    },
    {
      "name": "deep-analysis",
      "source": "deep-analysis",
      "description": "Structured decision analysis with MCP semantic search",
      "version": "0.1.0",
      "keywords": ["analysis", "decisions", "mcp", "semantic-search"],
      "author": { "name": "JP Sweeney" },
      "license": "MIT",
      "homepage": "https://github.com/jpsweeney97/superserum/tree/main/plugins/deep-analysis"
    },
    {
      "name": "doc-auditor",
      "source": "doc-auditor",
      "description": "Documentation audit and repair",
      "version": "1.0.0",
      "keywords": ["documentation", "audit", "quality"],
      "author": { "name": "JP Sweeney" },
      "license": "MIT",
      "homepage": "https://github.com/jpsweeney97/superserum/tree/main/plugins/doc-auditor"
    },
    {
      "name": "ecosystem-builder",
      "source": "ecosystem-builder",
      "description": "Multi-project orchestration for Claude Code",
      "version": "0.1.0",
      "keywords": ["orchestration", "multi-project", "automation"],
      "author": { "name": "JP Sweeney" },
      "license": "MIT",
      "homepage": "https://github.com/jpsweeney97/superserum/tree/main/plugins/ecosystem-builder"
    },
    {
      "name": "persistent-tasks",
      "source": "persistent-tasks",
      "description": "Cross-session task persistence with dependency tracking",
      "version": "0.1.0",
      "keywords": ["tasks", "persistence", "mcp"],
      "author": { "name": "JP Sweeney" },
      "license": "MIT",
      "homepage": "https://github.com/jpsweeney97/superserum/tree/main/plugins/persistent-tasks"
    }
  ]
}
```

## Migration Steps

### Pre-flight

```bash
# Backup current state
cp -r ~/.claude/plugins ~/.claude/plugins.backup.$(date +%Y%m%d)
cp ~/.claude/settings.json ~/.claude/settings.json.backup.$(date +%Y%m%d)

# Commit pending work
git status
git push origin main
```

### Phase 1: Prepare Repository

```bash
# Remove superpowers fork (no custom skills)
rm -rf plugins/superpowers/

# Create marketplace.json
mkdir -p .claude-plugin
# Write marketplace.json as shown above

# Update documentation
sed -i '' 's/claude-code-plugin-development/superserum/g' CONTRIBUTING.md CHANGELOG.md

# Commit
git add -A
git commit -m "chore: prepare superserum marketplace"
git push origin main
```

### Phase 2: Rename on GitHub

1. GitHub → Settings → General → Repository name → `superserum`
2. GitHub redirects the old URL for approximately one year

### Phase 3: Update Local Environment

```bash
# Rename local directory
cd /Users/jp/Projects/active
mv claude-code-plugin-development superserum

# Update git remote
cd superserum
git remote set-url origin https://github.com/jpsweeney97/superserum.git
git fetch

# Recreate symlinks
cd ~/.claude/plugins
rm deep-analysis doc-auditor plugin-dev ecosystem-builder persistent-tasks

ln -s /Users/jp/Projects/active/superserum/plugins/deep-analysis deep-analysis
ln -s /Users/jp/Projects/active/superserum/plugins/doc-auditor doc-auditor
ln -s /Users/jp/Projects/active/superserum/plugins/plugin-dev plugin-dev
ln -s /Users/jp/Projects/active/superserum/plugins/ecosystem-builder ecosystem-builder
ln -s /Users/jp/Projects/active/superserum/plugins/persistent-tasks persistent-tasks
```

### Phase 4: Verify

```bash
# Validate marketplace
cd /Users/jp/Projects/active/superserum
claude plugin validate .

# Test GitHub installation
/plugin marketplace add jpsweeney97/superserum
/plugin install plugin-dev@superserum
```

## Rollback Procedure

If the migration fails after Phase 2:

```bash
# Restore directory name
cd /Users/jp/Projects/active
mv superserum claude-code-plugin-development

# Restore git remote
cd claude-code-plugin-development
git remote set-url origin https://github.com/jpsweeney97/claude-code-plugin-development.git

# Restore from backup
rm -rf ~/.claude/plugins
cp -r ~/.claude/plugins.backup.* ~/.claude/plugins
cp ~/.claude/settings.json.backup.* ~/.claude/settings.json

# Rename repository back on GitHub if needed
```

## README Template

```markdown
# superserum

Plugins that enhance Claude Code capabilities.

## Installation

Add the marketplace:

    /plugin marketplace add jpsweeney97/superserum

Install plugins:

    /plugin install plugin-dev@superserum
    /plugin install deep-analysis@superserum

## Plugins

| Plugin | Description |
|--------|-------------|
| **plugin-dev** | Plugin development toolkit |
| **deep-analysis** | Structured decision analysis with MCP |
| **doc-auditor** | Documentation audit and repair |
| **ecosystem-builder** | Multi-project orchestration |
| **persistent-tasks** | Cross-session task persistence |

See each plugin's README for details.

## License

MIT
```

## Version Sync Rule

The marketplace entry version must match the plugin's `plugin.json` version. Update both together. Use a release script to enforce this.

## Next Steps

1. Execute Phase 1 (prepare repository)
2. Execute Phase 2 (GitHub rename)
3. Execute Phase 3 (local updates)
4. Execute Phase 4 (verify)
5. Update README.md with installation instructions
6. Create release script for version synchronization
