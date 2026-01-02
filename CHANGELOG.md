# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Marketplace**: Removed persistent-tasks from marketplace (not yet committed to repository)
- **doc-auditor**: Fixed `agents` manifest field to use explicit file paths

---

## Plugin: plugin-dev

### [1.4.0] - 2025-12-30

#### Added

- **Skills**:
  - `skillforge`: Intelligent skill creation with 5-phase methodology
  - `create-skill`: SkillForge-powered skill generation

#### Changed

- Version bump to 1.4.0

### [1.2.0] - 2025-12-29

#### Added

- **Skills**:
  - `brainstorming-plugins`: Design plugins through collaborative dialogue before implementation

- **Commands**:
  - `/plugin-dev:brainstorm`: Guided plugin design exploration with component decision framework

- **References**:
  - `component-decision-guide.md`: Decision flowchart for choosing Skills vs Commands vs Agents vs Hooks vs MCP

### [1.0.0] - 2025-12-29

Initial release of the plugin development toolkit.

#### Added

- **Skills** (10 total):
  - `hook-development`: Advanced hooks API with validation scripts
  - `mcp-integration`: Model Context Protocol server configuration
  - `plugin-structure`: Plugin organization and manifest patterns
  - `plugin-settings`: Configuration via `.claude/plugin-name.local.md`
  - `command-development`: Slash commands with frontmatter
  - `agent-development`: Autonomous agents with AI-assisted generation
  - `skill-development`: Skill creation with progressive disclosure
  - `plugin-audit`: 50+ validation rules across 8 categories
  - `writing-skills`: TDD methodology for documentation
  - `optimizing-plugins`: Six-lens analysis for plugin improvement

- **Commands**:
  - `/plugin-dev:create-plugin`: 8-phase guided plugin creation workflow
  - `/plugin-dev:audit-plugin`: Comprehensive validation with severity ratings
  - `/plugin-dev:fix-plugin`: Interactive repair with auto-fixes
  - `/plugin-dev:optimize-plugin`: Systematic improvement analysis

- **Agents**:
  - `agent-creator`: AI-assisted agent generation
  - `plugin-validator`: Proactive quality validation
  - `skill-reviewer`: Skill best practices review

- **Utilities**:
  - `validate-hook-schema.sh`: Hook JSON schema validation
  - `validate-agent.sh`: Agent frontmatter validation
  - `test-hook.sh`: Hook testing with sample input
  - `hook-linter.sh`: Hook script best practices linter
  - `parse-frontmatter.sh`: YAML frontmatter extraction
  - `validate-settings.sh`: Settings file validation

---

## Plugin: deep-analysis

### [0.1.0] - 2025-12-29

Initial release of structured decision analysis with MCP integration.

#### Added

- **MCP Server**: Semantic search over indexed analysis documents
  - `search_analyses`: Natural language search
  - `index_analysis`: Add/update analysis documents
  - `remove_analysis`: Remove from index
  - `rebuild_index`: Full index rebuild
  - `list_analyses`: Filter by domain/date

- **Skills**:
  - `deep-analysis:analyze`: Structured analysis session

- **Frameworks** (6):
  - Trade-off analysis
  - Architecture decisions
  - Risk assessment
  - Stakeholder impact
  - Implementation complexity
  - Long-term maintainability

---

## Plugin: doc-auditor

### [1.0.0] - 2025-12-29

Initial release of the documentation auditing toolkit.

#### Added

- **Commands**:
  - `/doc-auditor:scan`: Scan docs for issues across 15 categories
  - `/doc-auditor:fix`: Interactive repair session
  - `/doc-auditor:report`: Coherence analysis report

- **Agents**:
  - `coherence-analyzer`: Documentation design coherence analysis
  - `issue-detector`: Multi-category issue detection

- **Issue Categories** (15):
  - Structural issues, broken links, outdated content
  - Inconsistent terminology, missing sections
  - Template non-compliance, accessibility issues
  - And 8 more categories

---

## Plugin: ecosystem-builder

### [0.1.0] - 2026-01-01

Initial release of multi-project orchestration for Claude Code.

#### Added

- **Skills**:
  - Orchestration skills for multi-project coordination

- **Commands**:
  - Project orchestration commands

- **Library**:
  - Python library for cross-project coordination
  - Mock mode for testing (`--mock` flag)

---

## Versioning Notes

Each plugin maintains independent versioning:

| Plugin | Version | Status |
|--------|---------|--------|
| plugin-dev | 1.4.0 | Stable |
| deep-analysis | 0.1.0 | Alpha |
| doc-auditor | 1.0.0 | Stable |
| ecosystem-builder | 0.1.0 | Alpha |

[Unreleased]: https://github.com/jpsweeney97/superserum/compare/main...HEAD
[1.4.0]: https://github.com/jpsweeney97/superserum/releases/tag/plugin-dev-v1.4.0
[1.2.0]: https://github.com/jpsweeney97/superserum/releases/tag/plugin-dev-v1.2.0
[1.0.0]: https://github.com/jpsweeney97/superserum/releases/tag/plugin-dev-v1.0.0
[0.1.0]: https://github.com/jpsweeney97/superserum/releases/tag/deep-analysis-v0.1.0
