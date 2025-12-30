# Plugin-Dev Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Optimize the plugin-dev plugin from "good" to "great" by improving skill descriptions, reducing token bloat, establishing complementary skill relationships, and updating documentation.

**Architecture:** Four phased implementation:
1. Quick fixes (scripts, rename)
2. Content restructuring (two large skills)
3. Description batch updates
4. Documentation (README)

**Tech Stack:** Markdown, YAML frontmatter, Bash (git operations)

---

## Phase 1: Independent Quick Wins

### Task 1: Fix Script References in plugin-validator Agent

**Files:**
- Modify: `plugins/plugin-dev/agents/plugin-validator.md:126-134`

**Step 1: Replace incorrect script references**

Replace lines 126-134:
```markdown
## Using Validation Scripts

Run scripts for deterministic checks:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/validate-json.sh <plugin-path>
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/validate-yaml-frontmatter.sh <plugin-path>
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/check-paths.sh <plugin-path>
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/check-file-references.sh <plugin-path>
```
```

With:
```markdown
## Using Validation Scripts

Run deterministic validation:
```bash
# Layer 1: Syntax validation (JSON/YAML)
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/check-syntax.sh <plugin-path>

# Layer 2: Structure validation (manifest, naming, required fields)
bash ${CLAUDE_PLUGIN_ROOT}/skills/plugin-audit/scripts/check-structure.sh <plugin-path>
```

For path and reference checks, analyze files directly using Read/Grep tools.
```

**Step 2: Verify the edit**

Run: `grep -A10 "Using Validation Scripts" plugins/plugin-dev/agents/plugin-validator.md`
Expected: Shows check-syntax.sh and check-structure.sh, no missing scripts

**Step 3: Commit**

```bash
git add plugins/plugin-dev/agents/plugin-validator.md
git commit -m "fix(plugin-validator): correct script references to existing files

- Remove references to non-existent validate-json.sh, validate-yaml-frontmatter.sh,
  check-paths.sh, check-file-references.sh
- Use actual scripts: check-syntax.sh, check-structure.sh
- Add guidance to use Read/Grep for path/reference checks"
```

---

### Task 2: Rename optimize Command to optimize-plugin

**Files:**
- Rename: `plugins/plugin-dev/commands/optimize.md` → `plugins/plugin-dev/commands/optimize-plugin.md`
- Modify: `plugins/plugin-dev/README.md` (if needed)

**Step 1: Rename the command file**

```bash
cd plugins/plugin-dev/commands
git mv optimize.md optimize-plugin.md
```

**Step 2: Verify the rename**

```bash
ls plugins/plugin-dev/commands/
```
Expected: Shows `audit-plugin.md`, `create-plugin.md`, `fix-plugin.md`, `optimize-plugin.md`

**Step 3: Commit**

```bash
git add -A plugins/plugin-dev/commands/
git commit -m "refactor(commands): rename optimize → optimize-plugin

Follow plugin-dev naming convention: verb-plugin (audit-plugin, fix-plugin, etc.)"
```

---

## Phase 2: Content Restructuring

### Task 3: Restructure skill-development as Structural Reference

**Files:**
- Modify: `plugins/plugin-dev/skills/skill-development/SKILL.md`

**Context:** This skill (3,196 words) overlaps heavily with writing-skills on process content. Restructure to focus exclusively on **structure** (WHAT goes in a skill) while writing-skills handles **process** (HOW to create a skill).

**Step 1: Read current skill-development**

```bash
wc -w plugins/plugin-dev/skills/skill-development/SKILL.md
```
Expected: ~3,196 words (baseline)

**Step 2: Rewrite skill-development with focused structural content**

Replace entire file with (~1,200 words):

```markdown
---
name: Skill Development
description: Use for "skill file structure", "SKILL.md format", "progressive disclosure" patterns, or organizing skill directories. For creation process and testing, see writing-skills.
---

# Skill Development for Claude Code Plugins

Structural reference for building skills in Claude Code plugins.

## Related

For the **creation process** (TDD, testing, validation workflow), see the `writing-skills` skill.

## About Skills

Skills are modular packages extending Claude's capabilities with specialized knowledge and tools. They transform Claude from general-purpose to specialized by providing procedural knowledge no model fully possesses.

### What Skills Provide

| Type | Purpose | Example |
|------|---------|---------|
| Workflows | Multi-step procedures | Hook creation flow |
| Integrations | File format / API guidance | MCP configuration |
| Domain expertise | Company-specific knowledge | Business rules, schemas |
| Bundled resources | Scripts, references, assets | Validation utilities |

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown body
└── Bundled Resources (optional)
    ├── scripts/      - Executable code (deterministic tasks)
    ├── references/   - Documentation loaded as needed
    ├── examples/     - Working code to copy/adapt
    └── assets/       - Files for output (templates, icons)
```

### SKILL.md (Required)

| Component | Purpose |
|-----------|---------|
| `name` | Letters, numbers, hyphens only |
| `description` | When to use (not what it does) |
| Body | Core workflow, quick reference |

### scripts/

Executable code for deterministic or frequently-repeated tasks.

- **When to include:** Same code rewritten repeatedly, deterministic reliability needed
- **Example:** `scripts/validate-hook-schema.sh`
- **Benefits:** Token efficient, may execute without loading into context

### references/

Documentation loaded into context as needed.

- **When to include:** Detailed info Claude should reference while working
- **Examples:** API docs, schemas, patterns, advanced techniques
- **Best practice:** If >10k words, include grep search patterns in SKILL.md

**Avoid duplication:** Content lives in SKILL.md OR references, not both. Prefer references for detail—keeps SKILL.md lean.

### examples/

Working code users copy and adapt.

- **When to include:** Common patterns worth demonstrating
- **Examples:** Complete hook scripts, config files, templates

### assets/

Files for output, not context loading.

- **When to include:** Files used in final output (not documentation)
- **Examples:** Templates, images, fonts, boilerplate

## Progressive Disclosure

Skills use three-level loading to manage context efficiently:

| Level | When Loaded | Size Target |
|-------|-------------|-------------|
| Metadata (name + description) | Always | ~100 words |
| SKILL.md body | When triggered | 1,500-2,000 words |
| Bundled resources | As needed | Unlimited |

**Key principle:** SKILL.md must be self-sufficient for executing the skill. References provide depth on concepts mentioned in the skill—they answer "tell me more about X," not "what's the next step."

## SKILL.md Structure

```markdown
---
name: Skill-Name
description: Use when [specific triggering conditions]
---

# Skill Name

## Overview
Core principle in 1-2 sentences.

## When to Use
Bullet list with symptoms and use cases.
When NOT to use.

## Core Pattern
Before/after comparison or quick reference table.

## [Workflow Sections]
Step-by-step procedures as needed.

## Common Mistakes
What goes wrong + fixes.

## Resources
Pointers to references/, examples/, scripts/
```

## Description Quality

Descriptions determine when Claude loads the skill. Include:

- Specific trigger phrases in quotes
- Concrete scenarios (symptoms, contexts)
- Related skills for cross-reference

**Format:** Start with "Use when" or "Use for"

```yaml
# Good
description: Use for "skill file structure", "SKILL.md format", "progressive disclosure" patterns, or organizing skill directories.

# Bad
description: Provides guidance for working with skills.
```

## Directory Structure Patterns

### Minimal Skill
```
skill-name/
└── SKILL.md
```
For: Simple knowledge, no complex resources

### Standard Skill
```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```
For: Most plugin skills

### Complete Skill
```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```
For: Complex domains with utilities

## Plugin-Specific Notes

### Location

```
my-plugin/
├── .claude-plugin/plugin.json
└── skills/
    └── my-skill/
        └── SKILL.md
```

### Auto-Discovery

Claude Code automatically:
1. Scans `skills/` directory
2. Finds subdirectories with SKILL.md
3. Loads metadata always, body when triggered

### Testing

```bash
cc --plugin-dir /path/to/plugin
# Ask questions that should trigger the skill
```

## Study These Examples

Plugin-dev's skills demonstrate best practices:

| Skill | Notable Pattern |
|-------|-----------------|
| `hook-development` | Progressive disclosure, 3 scripts |
| `agent-development` | AI-assisted creation refs |
| `mcp-integration` | Comprehensive references |
| `plugin-settings` | Real-world examples |
```

**Step 3: Verify word count**

```bash
wc -w plugins/plugin-dev/skills/skill-development/SKILL.md
```
Expected: ~1,100-1,300 words

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/skill-development/SKILL.md
git commit -m "refactor(skill-development): focus on structure, remove process duplication

- Reduce from ~3,200 to ~1,200 words
- Remove: Skill Creation Process, Writing Style, Validation Checklist
  (all duplicated in writing-skills)
- Keep: Anatomy of a Skill, Progressive Disclosure, Directory Structure
- Add cross-reference to writing-skills for process guidance"
```

---

### Task 4: Restructure writing-skills Hierarchy and Tighten

**Files:**
- Modify: `plugins/plugin-dev/skills/writing-skills/SKILL.md`

**Context:** This skill (3,202 words) has a flat 29-section structure and redundant content. Restructure into 7 H2 sections and reduce to ~2,200 words while keeping all essential workflow content.

**Step 1: Read current word count**

```bash
wc -w plugins/plugin-dev/skills/writing-skills/SKILL.md
```
Expected: ~3,202 words (baseline)

**Step 2: Rewrite with hierarchical structure**

Replace entire file with (~2,200 words):

```markdown
---
name: Writing Skills
description: Use when "creating skills", "testing skills", "skill TDD", or applying TDD methodology to documentation. For structure and file organization, see skill-development.
---

# Writing Skills

**Writing skills IS Test-Driven Development applied to process documentation.**

## Related

For **file structure** (directories, SKILL.md format, progressive disclosure), see the `skill-development` skill.

## Overview

Write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill, watch tests pass (agents comply), refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**Skill Architecture Principle:**
- SKILL.md = Complete workflow, self-sufficient for using the skill
- References = Deep knowledge on elemental concepts mentioned in the skill
- If Claude must read a reference to execute the skill, that content belongs in SKILL.md

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious
- You'd reference this again across projects
- Pattern applies broadly (not project-specific)
- Others would benefit

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in CLAUDE.md)
- Mechanical constraints enforceable with validation

### Skill Types

| Type | What It Is | Test Approach |
|------|------------|---------------|
| **Technique** | Concrete method with steps | Application scenarios |
| **Pattern** | Way of thinking about problems | Recognition + counter-examples |
| **Reference** | API docs, syntax guides | Retrieval + gap testing |
| **Discipline** | Rules/requirements to follow | Pressure scenarios |

## The TDD Process

### The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills. Write skill before testing? Delete it. Start over.

**No exceptions:** Not for "simple additions," "just adding a section," or "documentation updates."

### RED: Write Failing Test (Baseline)

Run pressure scenario with subagent WITHOUT the skill. Document:
- What choices did they make?
- What rationalizations did they use (verbatim)?
- Which pressures triggered violations?

This is "watch the test fail"—see what agents naturally do before writing the skill.

### GREEN: Write Minimal Skill

Write skill addressing those specific rationalizations. Don't add content for hypothetical cases.

Run same scenarios WITH skill. Agent should now comply.

### REFACTOR: Close Loopholes

Agent found new rationalization? Add explicit counter. Re-test until bulletproof.

**Testing methodology:** See `references/testing-skills-with-subagents.md` for pressure scenarios, pressure types, and systematic hole-plugging.

## Writing the Skill

### Claude Search Optimization (CSO)

**Critical:** Future Claude needs to FIND your skill.

#### Description Field

| Aspect | Guidance |
|--------|----------|
| Format | Start with "Use when..." |
| Content | Triggering conditions only |
| Avoid | Summarizing workflow (Claude will follow description instead of reading skill) |
| Person | Third person (injected into system prompt) |

```yaml
# Bad - summarizes workflow
description: Use when executing plans - dispatches subagent per task with code review

# Good - just triggers
description: Use when executing implementation plans with independent tasks
```

#### Keywords

Use words Claude would search for:
- Error messages: "Hook timed out", "race condition"
- Symptoms: "flaky", "hanging", "pollution"
- Synonyms: "timeout/hang/freeze", "cleanup/teardown"
- Tools: Actual commands, library names

#### Naming

- Active voice, verb-first: `creating-skills` not `skill-creation`
- Gerunds work well: `debugging-with-logs`, `testing-skills`
- Name by what you DO: `condition-based-waiting` not `async-helpers`

### Skill Content Guidelines

**One excellent example beats many mediocre ones.** Choose most relevant language:
- Testing → TypeScript/JavaScript
- System debugging → Shell/Python
- Data processing → Python

**Cross-referencing other skills:**
- Use: `**REQUIRED SUB-SKILL:** Use superpowers:test-driven-development`
- Avoid: `@skills/path/SKILL.md` (force-loads, burns context)

**Flowcharts:** Use ONLY for non-obvious decision points or "when to use A vs B" decisions. Never for reference material, code examples, or linear instructions.

## Testing by Skill Type

### Discipline Skills (rules/requirements)

Test with pressure scenarios combining multiple pressures:
- Time pressure
- Sunk cost
- Authority signals
- Exhaustion cues

**Success:** Agent follows rule under maximum pressure.

### Technique Skills (how-to guides)

Test with application scenarios:
- Can they apply correctly?
- Do they handle edge cases?
- Are instructions complete?

**Success:** Agent successfully applies technique to new scenario.

### Pattern/Reference Skills

Test with recognition and retrieval:
- Do they recognize when pattern applies?
- Can they find the right information?
- Are common use cases covered?

## Bulletproofing Against Rationalization

Skills enforcing discipline need to resist rationalization under pressure.

### Close Every Loophole Explicitly

```markdown
Write code before test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete
```

### Build Rationalization Table

Capture rationalizations from baseline testing:

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Skill is obviously clear" | Clear to you ≠ clear to other agents. Test it. |

### Create Red Flags List

```markdown
## Red Flags - STOP and Start Over

- Code before test
- "I already manually tested it"
- "This is different because..."

**All of these mean: Delete. Start over.**
```

## Checklist

**Use TodoWrite to create todos for each item.**

**RED Phase:**
- [ ] Create pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Run WITHOUT skill - document baseline verbatim
- [ ] Identify rationalization patterns

**GREEN Phase:**
- [ ] Name uses only letters, numbers, hyphens
- [ ] Description starts "Use when..." with specific triggers
- [ ] Description in third person
- [ ] Address specific baseline failures
- [ ] Run WITH skill - verify compliance

**REFACTOR Phase:**
- [ ] Identify NEW rationalizations
- [ ] Add explicit counters
- [ ] Build rationalization table
- [ ] Re-test until bulletproof

**Quality:**
- [ ] Quick reference table included
- [ ] Common mistakes section
- [ ] No narrative storytelling
- [ ] Supporting files only for tools or heavy reference

**Deployment:**
- [ ] Commit to git
- [ ] STOP after each skill - don't batch without testing

## The Bottom Line

**Creating skills IS TDD for process documentation.**

Same Iron Law: No skill without failing test first.
Same cycle: RED (baseline) → GREEN (write skill) → REFACTOR (close loopholes).
Same benefits: Better quality, fewer surprises, bulletproof results.

## References

- `references/testing-skills-with-subagents.md` - Pressure scenario methodology
- `references/persuasion-principles.md` - Psychology of rationalization resistance
- `references/graphviz-conventions.dot` - Flowchart style rules
- `references/anthropic-best-practices.md` - Official Anthropic guidance
```

**Step 3: Verify word count**

```bash
wc -w plugins/plugin-dev/skills/writing-skills/SKILL.md
```
Expected: ~2,000-2,400 words

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/writing-skills/SKILL.md
git commit -m "refactor(writing-skills): restructure hierarchy and reduce verbosity

- Reduce from ~3,200 to ~2,200 words
- Restructure from 29 flat H2 sections to 7 H2 with H3 subsections
- Add Skill Architecture Principle (SKILL.md = self-sufficient)
- Consolidate CSO section using tables
- Remove structural content (defer to skill-development)
- Add cross-reference to skill-development"
```

---

### Task 5: Add Cross-References for Complementary Peer Relationship

**Files:**
- Verify: Cross-references already added in Tasks 3 and 4

**Step 1: Verify skill-development has cross-reference**

```bash
grep -A2 "## Related" plugins/plugin-dev/skills/skill-development/SKILL.md
```
Expected: Shows reference to writing-skills for process

**Step 2: Verify writing-skills has cross-reference**

```bash
grep -A2 "## Related" plugins/plugin-dev/skills/writing-skills/SKILL.md
```
Expected: Shows reference to skill-development for structure

**Step 3: No commit needed**

Cross-references were added in Tasks 3 and 4.

---

## Phase 3: Description Updates (Batch)

### Task 6: Update Skill Descriptions

**Files:**
- Modify: 8 skill SKILL.md files (all except writing-skills and optimizing-plugins)

**Pattern:** Change from "This skill should be used when the user asks to" to "Use when" and quote trigger phrases.

**Step 1: Update hook-development description**

In `plugins/plugin-dev/skills/hook-development/SKILL.md`, replace line 3:
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", "${CLAUDE_PLUGIN_ROOT}", "block dangerous commands", or work with hook events (PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification). Also trigger when the user mentions event-driven automation or hook debugging.
```

With:
```yaml
description: Use when "creating a hook", "adding a PreToolUse hook", "validating tool use", or "implementing prompt-based hooks". Also for hook events (PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification) or debugging hooks.
```

**Step 2: Update mcp-integration description**

In `plugins/plugin-dev/skills/mcp-integration/SKILL.md`, replace line 3:
```yaml
description: This skill should be used when the user asks to "add MCP server", "integrate MCP", "configure MCP in plugin", "use .mcp.json", "set up Model Context Protocol", "connect external service", mentions "${CLAUDE_PLUGIN_ROOT} with MCP", or discusses MCP server types (SSE, stdio, HTTP, WebSocket). Provides comprehensive guidance for integrating Model Context Protocol servers into Claude Code plugins for external tool and service integration.
```

With:
```yaml
description: Use when "adding MCP server", "integrating MCP", "configuring .mcp.json", or "connecting external service". Also for MCP server types (SSE, stdio, HTTP, WebSocket) or "${CLAUDE_PLUGIN_ROOT}" with MCP.
```

**Step 3: Update plugin-settings description**

In `plugins/plugin-dev/skills/plugin-settings/SKILL.md`, replace line 3:
```yaml
description: This skill should be used when the user asks about "plugin settings", "store plugin configuration", "user-configurable plugin", ".local.md files", "plugin state files", "read YAML frontmatter", "per-project plugin settings", or wants to make plugin behavior configurable. Documents the .claude/plugin-name.local.md pattern for storing plugin-specific configuration with YAML frontmatter and markdown content.
```

With:
```yaml
description: Use for "plugin settings", "storing plugin configuration", ".local.md files", "YAML frontmatter parsing", or "per-project settings". Documents the .claude/plugin-name.local.md pattern.
```

**Step 4: Update agent-development description**

In `plugins/plugin-dev/skills/agent-development/SKILL.md`, replace line 3:
```yaml
description: This skill should be used when the user asks to "create an agent", "add an agent", "write a subagent", "agent frontmatter", "when to use description", "agent examples", "agent tools", "agent colors", "autonomous agent", or needs guidance on agent structure, system prompts, triggering conditions, or agent development best practices for Claude Code plugins.
```

With:
```yaml
description: Use when "creating an agent", "adding an agent", "writing a subagent", or configuring agent frontmatter (description, tools, colors). Also for system prompt design or triggering conditions.
```

**Step 5: Update command-development description**

In `plugins/plugin-dev/skills/command-development/SKILL.md`, replace line 3:
```yaml
description: This skill should be used when the user asks to "create a slash command", "add a command", "write a custom command", "define command arguments", "use command frontmatter", "organize commands", "create command with file references", "interactive command", "use AskUserQuestion in command", or needs guidance on slash command structure, YAML frontmatter fields, dynamic arguments, bash execution in commands, user interaction patterns, or command development best practices for Claude Code plugins.
```

With:
```yaml
description: Use when "creating a slash command", "adding a command", "defining command arguments", or "using command frontmatter". Also for command structure, dynamic arguments, bash execution, or AskUserQuestion patterns.
```

**Step 6: Update plugin-structure description**

First read the current file to check its description:
```bash
head -5 plugins/plugin-dev/skills/plugin-structure/SKILL.md
```

Then update if needed to follow pattern:
```yaml
description: Use for "plugin structure", "plugin.json manifest", "auto-discovery", or "component organization". Also for directory layout, file naming conventions, or ${CLAUDE_PLUGIN_ROOT} usage.
```

**Step 7: Update plugin-audit description**

In `plugins/plugin-dev/skills/plugin-audit/SKILL.md`, update lines 3-7:
```yaml
description: >
  Use when the user asks to "audit a plugin", "validate plugin structure",
  "check plugin quality", "lint plugin", "review plugin for issues", or
  "verify plugin correctness". Documents the 5-phase auditing methodology
  with 50+ validation rules across 8 categories.
```

With:
```yaml
description: Use when "auditing a plugin", "validating plugin structure", "checking plugin quality", or "linting plugin". Covers 50+ validation rules across 8 categories (structure, skills, commands, agents, hooks, MCP, security, cross-component).
```

**Step 8: Update skill-development description**

Already updated in Task 3. Verify:
```bash
grep "^description:" plugins/plugin-dev/skills/skill-development/SKILL.md
```
Expected: `description: Use for "skill file structure"...`

**Step 9: Commit all description updates**

```bash
git add plugins/plugin-dev/skills/*/SKILL.md
git commit -m "refactor(skills): standardize descriptions to 'Use when' format

Apply consistent description pattern across 8 skills:
- Start with 'Use when' or 'Use for'
- Quote trigger phrases
- Remove verbose preambles ('This skill should be used when the user asks to')
- Keep under ~200 characters where possible"
```

---

## Phase 4: Documentation

### Task 7: Update README to Document All 10 Skills

**Files:**
- Modify: `plugins/plugin-dev/README.md`

**Step 1: Update overview section**

Replace line 7:
```markdown
The plugin-dev toolkit provides nine specialized skills to help you build high-quality Claude Code plugins:
```

With:
```markdown
The plugin-dev toolkit provides **ten specialized skills** to help you build high-quality Claude Code plugins:
```

**Step 2: Add missing skills to list (after skill 7)**

After the current skill 7 (Skill Development) at line 16, add:

```markdown
8. **Plugin Audit** - Comprehensive validation with 50+ rules across 8 categories
9. **Writing Skills** - TDD methodology for creating skills (process-focused)
10. **Plugin Optimization** - Six-lens analysis for improving plugins from good to great
```

**Step 3: Add skill relationship note**

After the list of 10 skills (around line 20), add:

```markdown
**Note on skill relationships:**
- **Writing Skills** (process) ↔ **Skill Development** (structure): Complementary peers for skill creation
- **Plugin Audit** (problems) → **Plugin Optimization** (refinement): Run audit first, then optimize
```

**Step 4: Add Writing Skills section**

After the current "### 7. Skill Development" section (around line 230), add:

```markdown
### 8. Plugin Audit

**Trigger phrases:** "audit a plugin", "validate plugin structure", "check plugin quality", "lint plugin"

**What it covers:**
- 5-phase auditing methodology
- 50+ validation rules across 8 categories
- Severity classification (CRITICAL/WARNING/INFO)
- Validation scripts for deterministic checks
- Report generation (markdown and JSON)

**Resources:**
- Core SKILL.md (~9,000 words comprehensive reference)
- 8 reference files with all validation rules
- 4 validation scripts

**Use when:** Validating plugins before testing/publishing or enforcing best practices.

### 9. Writing Skills

**Trigger phrases:** "creating skills", "testing skills", "skill TDD"

**What it covers:**
- TDD methodology for documentation
- Pressure testing with subagents
- Claude Search Optimization (CSO)
- Bulletproofing against rationalization
- Skill Architecture Principle (SKILL.md self-sufficiency)

**Resources:**
- Core SKILL.md (~2,200 words)
- 4 reference files (testing methodology, persuasion, graphviz, Anthropic best practices)

**Related:** For structure (directories, SKILL.md format), see Skill Development.

**Use when:** Creating new skills or applying TDD to process documentation.

### 10. Plugin Optimization

**Trigger phrases:** "optimize plugin", "improve plugin quality", "enhance plugin"

**What it covers:**
- Six analytical lenses for improvement
- Prioritized design document generation
- Quick wins vs. high-value changes
- Token efficiency analysis
- Description quality assessment

**Resources:**
- Core SKILL.md (~1,500 words)
- References: optimization lenses, examples

**Use when:** Plugin passes audit and needs refinement. Run audit first to fix issues.
```

**Step 5: Add agents section**

After the "## Skills" section ends (before "## Installation"), add:

```markdown
## Agents

The plugin-dev toolkit includes three specialized agents:

### agent-creator

AI-assisted agent generation using Claude Code's proven prompt. Creates agents with proper frontmatter, description format, and system prompts.

### plugin-validator

Proactive quality validation for plugins. Runs targeted checks after component changes and comprehensive audits before testing/publishing.

### skill-reviewer

Reviews skills for best practices including description quality, content organization, progressive disclosure, and trigger phrase effectiveness.
```

**Step 6: Update version note**

Replace line 450:
```markdown
1.0.0 - Enhanced with plugin-auditor integration: 9 skills, 3 agents, 3 commands, 50+ validation rules
```

With:
```markdown
1.1.0 - Full toolkit: 10 skills, 3 agents, 4 commands, 50+ validation rules
```

**Step 7: Verify changes**

```bash
grep -c "specialized skills" plugins/plugin-dev/README.md
```
Expected: Shows "ten specialized skills"

```bash
grep "### 9. Writing Skills" plugins/plugin-dev/README.md
grep "### 10. Plugin Optimization" plugins/plugin-dev/README.md
```
Expected: Both found

**Step 8: Commit**

```bash
git add plugins/plugin-dev/README.md
git commit -m "docs(README): document all 10 skills, add agents section

- Update from 'nine' to 'ten specialized skills'
- Add entries for Writing Skills, Plugin Audit, Plugin Optimization
- Add note about skill relationships (writing-skills ↔ skill-development)
- Add Agents section documenting all 3 agents
- Update version to 1.1.0"
```

---

## Phase 5: Verification

### Task 8: Run Audit and Verify Changes

**Step 1: Check word counts for restructured skills**

```bash
wc -w plugins/plugin-dev/skills/writing-skills/SKILL.md
wc -w plugins/plugin-dev/skills/skill-development/SKILL.md
```
Expected:
- writing-skills: ~2,000-2,400 words (down from 3,202)
- skill-development: ~1,100-1,300 words (down from 3,196)

**Step 2: Verify all skills have proper descriptions**

```bash
for skill in plugins/plugin-dev/skills/*/SKILL.md; do
  echo "=== $skill ==="
  head -4 "$skill" | grep "^description:"
done
```
Expected: All start with "Use when" or "Use for"

**Step 3: Run plugin audit**

```bash
/plugin-dev:audit-plugin plugins/plugin-dev
```
Expected: No new critical issues introduced

**Step 4: Final commit (if any fixes needed)**

If audit reveals issues, fix and commit:
```bash
git add -A plugins/plugin-dev/
git commit -m "fix: address issues from post-optimization audit"
```

---

## Summary

| Phase | Tasks | Key Changes |
|-------|-------|-------------|
| 1 | 1-2 | Fix script refs, rename command |
| 2 | 3-5 | Restructure two skills, add cross-refs |
| 3 | 6 | Update 8 skill descriptions |
| 4 | 7 | Update README with all 10 skills |
| 5 | 8 | Verify and audit |

**Total commits:** 7-8 focused commits following the optimization phases.
