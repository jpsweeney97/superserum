# Plugin-Dev Optimization Implementation Plan

> **⚠️ PARTIALLY SUPERSEDED (2025-12-31):** References to `skillcreator` in this plan should read `skillforge` following the upstream rename.
>
> - Migration documentation: [`plugins/plugin-dev/docs/migrations/skillcreator-to-skillforge.md`](../../plugins/plugin-dev/docs/migrations/skillcreator-to-skillforge.md)
>
> *The optimization recommendations remain valid; only the skill name has changed.*

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve plugin-dev trigger fidelity, resilience, and coherence through 12 targeted changes across 18 files.

**Architecture:** All changes are documentation/configuration updates to YAML frontmatter and markdown content. No code logic changes. Each task is a single file edit with validation.

**Tech Stack:** Markdown, YAML frontmatter, Bash scripts

---

## Task 1: Update plugin-audit Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -10 plugins/plugin-dev/skills/plugin-audit/SKILL.md
```

**Step 2: Edit description to third-person format**

Change:
```yaml
description: Use when "auditing a plugin", "validating plugin structure", "checking plugin quality", or "linting plugin". Covers 50+ validation rules across 8 categories.
```

To:
```yaml
description: This skill validates Claude Code plugins with 50+ rules across 8 categories. Invoked by `/plugin-dev:audit-plugin` command. Use when "auditing a plugin", "validating plugin structure", "checking plugin quality", or "linting plugin".
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/plugin-audit/SKILL.md
```

Expected: Description starts with "This skill validates..."

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/SKILL.md
git commit -m "docs(plugin-audit): use third-person description format"
```

---

## Task 2: Update hook-development Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/hook-development/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -10 plugins/plugin-dev/skills/hook-development/SKILL.md
```

**Step 2: Edit description to third-person format**

Change:
```yaml
description: Use when "creating a hook", "adding a PreToolUse hook", "validating tool use", or "implementing prompt-based hooks". Also for hook events (PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification).
```

To:
```yaml
description: This skill guides hook creation for Claude Code plugins. Use when "creating a hook", "adding a PreToolUse hook", "validating tool use", or "implementing prompt-based hooks". Covers all events: PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification.
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/hook-development/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/hook-development/SKILL.md
git commit -m "docs(hook-development): use third-person description format"
```

---

## Task 3: Update skill-development Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/skill-development/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -10 plugins/plugin-dev/skills/skill-development/SKILL.md
```

**Step 2: Edit description with third-person format and fixed quotes**

Change:
```yaml
description: Use for "skill file structure", "SKILL.md format", "progressive disclosure" patterns, or organizing skill directories. For creation process and testing, see writing-skills.
```

To:
```yaml
description: This skill provides structural reference for building skills in Claude Code plugins. Use for "skill file structure", "SKILL.md format", "progressive disclosure patterns", "organizing skill directories", or "skill anatomy". This is the WHERE and WHAT of skills. For HOW to test, see writing-skills. For rigorous creation, see skillcreator.
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/skill-development/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/skill-development/SKILL.md
git commit -m "docs(skill-development): improve description with cross-references"
```

---

## Task 4: Update writing-skills Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/writing-skills/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -10 plugins/plugin-dev/skills/writing-skills/SKILL.md
```

**Step 2: Edit description to clarify scope (testing, not creating)**

Change:
```yaml
description: Use when "creating skills", "testing skills", "skill TDD"
```

To:
```yaml
description: This skill applies TDD methodology to skill development. Use when "testing skills", "skill TDD", "pressure testing skills", or "validating skill effectiveness". For skill structure, see skill-development. For full creation methodology, see skillcreator.
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/writing-skills/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/writing-skills/SKILL.md
git commit -m "docs(writing-skills): clarify scope as testing, add cross-references"
```

---

## Task 5: Update skillcreator Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/skillcreator/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -15 plugins/plugin-dev/skills/skillcreator/SKILL.md
```

**Step 2: Edit description to clarify when to use**

Change:
```yaml
description: "Use when creating production-grade skills that need rigorous analysis, evolution scoring, and multi-agent review. Triggers: 'SkillCreator:', 'ultimate skill', 'best possible skill', 'rigorous skill creation'. For simple skill structure, see skill-development. For TDD testing, see writing-skills."
```

To:
```yaml
description: "This skill creates production-grade skills using rigorous 4-phase methodology with 11 thinking lenses and multi-agent synthesis. Use when 'SkillCreator:', 'ultimate skill', 'best possible skill', 'rigorous skill creation', or when creating complex/critical skills. For simple skills, use skill-development (structure) + writing-skills (testing)."
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/skillcreator/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/skillcreator/SKILL.md
git commit -m "docs(skillcreator): clarify as full methodology with cross-references"
```

---

## Task 6: Update optimizing-plugins Skill Description

**Files:**
- Modify: `plugins/plugin-dev/skills/optimizing-plugins/SKILL.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -10 plugins/plugin-dev/skills/optimizing-plugins/SKILL.md
```

**Step 2: Edit description with symptom-based triggers**

Change:
```yaml
description: Systematically improves Claude Code plugins through 6 analytical lenses. Use after audit confirms no broken issues, when asked to optimize, improve, or enhance a plugin, or when refining trigger phrases, token efficiency, or structural clarity.
```

To:
```yaml
description: "This skill guides systematic plugin improvement from 'good' to 'great' using 6 analytical lenses. Use after 'audit passes', when plugin 'works but feels rough', 'triggers aren't firing reliably', 'skills overlap confusingly', or when asked to 'optimize plugin', 'improve plugin quality', 'refine descriptions'. Distinct from audit (which fixes broken to working)."
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/skills/optimizing-plugins/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/optimizing-plugins/SKILL.md
git commit -m "docs(optimizing-plugins): add symptom-based triggers"
```

---

## Task 7: Update Remaining Skill Descriptions (Batch)

**Files:**
- Modify: `plugins/plugin-dev/skills/mcp-integration/SKILL.md:1-5`
- Modify: `plugins/plugin-dev/skills/plugin-settings/SKILL.md:1-5`
- Modify: `plugins/plugin-dev/skills/command-development/SKILL.md:1-5`
- Modify: `plugins/plugin-dev/skills/agent-development/SKILL.md:1-5`
- Modify: `plugins/plugin-dev/skills/brainstorming-plugins/SKILL.md:1-5`

**Step 1: Read each current description**

```bash
for skill in mcp-integration plugin-settings command-development agent-development brainstorming-plugins; do
  echo "=== $skill ===" && head -5 plugins/plugin-dev/skills/$skill/SKILL.md
done
```

**Step 2: Update each to third-person format**

For each skill, prepend "This skill..." before "Use when...":

- **mcp-integration**: "This skill guides MCP server integration for Claude Code plugins. Use when..."
- **plugin-settings**: "This skill teaches configuration patterns using .local.md files. Use when..."
- **command-development**: "This skill guides slash command creation. Use when..."
- **agent-development**: "This skill guides autonomous agent creation. Use when..."
- **brainstorming-plugins**: "This skill guides plugin design through collaborative dialogue. Use when..."

**Step 3: Verify changes**

```bash
for skill in mcp-integration plugin-settings command-development agent-development brainstorming-plugins; do
  echo "=== $skill ===" && head -4 plugins/plugin-dev/skills/$skill/SKILL.md
done
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/*/SKILL.md
git commit -m "docs(skills): apply third-person description format to remaining skills"
```

---

## Task 8: Update README Skill List to Table

**Files:**
- Modify: `plugins/plugin-dev/README.md:7-27`

**Step 1: Read current skill list**

```bash
sed -n '7,27p' plugins/plugin-dev/README.md
```

**Step 2: Replace numbered list with table**

Replace lines 7-20 (the numbered list) with:

```markdown
The plugin-dev toolkit provides **12 specialized skills** to help you build high-quality Claude Code plugins:

| # | Skill | Directory | Purpose |
|---|-------|-----------|---------|
| 1 | Hook Development | `hook-development` | Event-driven automation |
| 2 | MCP Integration | `mcp-integration` | Model Context Protocol servers |
| 3 | Plugin Structure | `plugin-structure` | Organization and manifest |
| 4 | Plugin Settings | `plugin-settings` | Configuration patterns |
| 5 | Command Development | `command-development` | Slash commands |
| 6 | Agent Development | `agent-development` | Autonomous agents |
| 7 | Skill Development | `skill-development` | Skill structure reference |
| 8 | Plugin Audit | `plugin-audit` | 50+ validation rules |
| 9 | Writing Skills | `writing-skills` | TDD methodology |
| 10 | Plugin Optimization | `optimizing-plugins` | Six-lens improvement |
| 11 | Plugin Brainstorming | `brainstorming-plugins` | Design before implementation |
| 12 | SkillCreator | `skillcreator` | Rigorous 4-phase creation |
```

**Step 3: Verify table renders correctly**

```bash
sed -n '7,25p' plugins/plugin-dev/README.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/README.md
git commit -m "docs(readme): convert skill list to table with directories"
```

---

## Task 9: Add Command-Skill Relationship Table to README

**Files:**
- Modify: `plugins/plugin-dev/README.md` (after skill list, before "Skill relationships")

**Step 1: Find insertion point**

```bash
grep -n "Skill relationships" plugins/plugin-dev/README.md
```

**Step 2: Insert command-skill table before "Skill relationships" line**

Add this block:

```markdown
**Command ↔ Skill Relationships:**

| Command | Invokes Skill | When to Use |
|---------|---------------|-------------|
| `/audit-plugin` | `plugin-audit` | On-demand structured audit |
| `/optimize-plugin` | `optimizing-plugins` | Guided improvement session |
| `/fix-plugin` | `plugin-audit` | Interactive repair |
| `/create-plugin` | Multiple skills | End-to-end creation |
| `/create-skill` | `skillcreator` | Rigorous skill creation |
| `/brainstorm` | `brainstorming-plugins` | Design exploration |

```

**Step 3: Verify insertion**

```bash
grep -A 10 "Command ↔ Skill" plugins/plugin-dev/README.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/README.md
git commit -m "docs(readme): add command-skill relationship table"
```

---

## Task 10: Add Error Handling to validate-write.sh

**Files:**
- Modify: `plugins/plugin-dev/skills/hook-development/examples/validate-write.sh:8-12`

**Step 1: Read current input handling**

```bash
sed -n '1,20p' plugins/plugin-dev/skills/hook-development/examples/validate-write.sh
```

**Step 2: Add JSON validation after `input=$(cat)`**

After line 8 (`input=$(cat)`), insert:

```bash
# Validate JSON input
if ! echo "$input" | jq empty 2>/dev/null; then
  echo '{"continue": true, "systemMessage": "Hook received malformed JSON input, skipping validation"}' >&2
  exit 0
fi
```

**Step 3: Update jq calls with error handling**

Change:
```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
```

To:
```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")
```

**Step 4: Test script syntax**

```bash
bash -n plugins/plugin-dev/skills/hook-development/examples/validate-write.sh && echo "Syntax OK"
```

**Step 5: Commit**

```bash
git add plugins/plugin-dev/skills/hook-development/examples/validate-write.sh
git commit -m "fix(hooks): add error handling to validate-write example"
```

---

## Task 11: Add Error Handling to validate-bash.sh

**Files:**
- Modify: `plugins/plugin-dev/skills/hook-development/examples/validate-bash.sh:8-12`

**Step 1: Read current input handling**

```bash
sed -n '1,20p' plugins/plugin-dev/skills/hook-development/examples/validate-bash.sh
```

**Step 2: Add JSON validation after `input=$(cat)`**

After line 8, insert same pattern as Task 10:

```bash
# Validate JSON input
if ! echo "$input" | jq empty 2>/dev/null; then
  echo '{"continue": true, "systemMessage": "Hook received malformed JSON input, skipping validation"}' >&2
  exit 0
fi
```

**Step 3: Update jq calls with error handling**

Change:
```bash
command=$(echo "$input" | jq -r '.tool_input.command // empty')
```

To:
```bash
command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")
```

**Step 4: Test script syntax**

```bash
bash -n plugins/plugin-dev/skills/hook-development/examples/validate-bash.sh && echo "Syntax OK"
```

**Step 5: Commit**

```bash
git add plugins/plugin-dev/skills/hook-development/examples/validate-bash.sh
git commit -m "fix(hooks): add error handling to validate-bash example"
```

---

## Task 12: Add Error Handling to load-context.sh

**Files:**
- Modify: `plugins/plugin-dev/skills/hook-development/examples/load-context.sh`

**Step 1: Read current script**

```bash
cat plugins/plugin-dev/skills/hook-development/examples/load-context.sh
```

**Step 2: Add JSON validation if script reads JSON input**

Apply same pattern if applicable. If script doesn't read JSON, add a comment explaining why validation isn't needed.

**Step 3: Test script syntax**

```bash
bash -n plugins/plugin-dev/skills/hook-development/examples/load-context.sh && echo "Syntax OK"
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/hook-development/examples/load-context.sh
git commit -m "fix(hooks): add error handling to load-context example"
```

---

## Task 13: Fix Skill References in skill-reviewer Agent

**Files:**
- Modify: `plugins/plugin-dev/agents/skill-reviewer.md:44,217`

**Step 1: Read current references**

```bash
grep -n "skill-creator\|plugin-dev's own" plugins/plugin-dev/agents/skill-reviewer.md
```

**Step 2: Update line 44**

Change: "skill-creator best practices"
To: "`skillcreator` skill best practices"

**Step 3: Update line 217**

Change: "plugin-dev's own skills"
To: "plugin-dev's skills (see `skill-development`, `writing-skills`, `skillcreator`)"

**Step 4: Verify changes**

```bash
grep -n "skillcreator\|skill-development" plugins/plugin-dev/agents/skill-reviewer.md
```

**Step 5: Commit**

```bash
git add plugins/plugin-dev/agents/skill-reviewer.md
git commit -m "docs(skill-reviewer): use exact skill directory names"
```

---

## Task 14: Add Partial Failure Handling to plugin-validator Agent

**Files:**
- Modify: `plugins/plugin-dev/agents/plugin-validator.md:69-70`

**Step 1: Find Comprehensive Mode section**

```bash
grep -n "Comprehensive Mode" plugins/plugin-dev/agents/plugin-validator.md
```

**Step 2: Add partial failure handling after step 5**

Insert after line ~69:

```markdown

**Handling Partial Failures:**
- If validation scripts fail to run: Fall back to manual checks using Read/Grep. Note in report: "Script validation unavailable — manual checks performed."
- If a category can't be assessed: Mark as "⚠️ Skipped" with reason, don't silently omit.
- If findings are incomplete: Explicitly state what was NOT checked and why.
- Never report "all clear" unless all categories were actually validated.
```

**Step 3: Add incomplete check output format**

Find Output Format section and add:

```markdown
### For Incomplete Checks
```
## Plugin Audit Summary (Partial)

**Note:** Some checks could not be completed:
- [Category]: [Reason]

| Category | Status |
|----------|--------|
| Structure | ✅ |
| Skills | ⚠️ Skipped |

**Recommendation:** Resolve blockers and re-run.
```
```

**Step 4: Verify additions**

```bash
grep -A 5 "Partial Failures" plugins/plugin-dev/agents/plugin-validator.md
```

**Step 5: Commit**

```bash
git add plugins/plugin-dev/agents/plugin-validator.md
git commit -m "docs(plugin-validator): add partial failure handling guidance"
```

---

## Task 15: Update audit-plugin Command Description

**Files:**
- Modify: `plugins/plugin-dev/commands/audit-plugin.md:1-5`

**Step 1: Read current frontmatter**

```bash
head -15 plugins/plugin-dev/commands/audit-plugin.md
```

**Step 2: Update description to reference skill**

Change:
```yaml
description: Run comprehensive plugin audit with detailed report, severity ratings, and fix suggestions
```

To:
```yaml
description: Run comprehensive plugin audit. Invokes the `plugin-audit` skill with structured output, severity ratings, and fix suggestions. Use this command for on-demand audits; the skill loads automatically when discussing audit topics.
```

**Step 3: Verify change**

```bash
head -5 plugins/plugin-dev/commands/audit-plugin.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/commands/audit-plugin.md
git commit -m "docs(audit-plugin): reference skill in command description"
```

---

## Task 16: Add Fallback Instructions to plugin-audit Skill

**Files:**
- Modify: `plugins/plugin-dev/skills/plugin-audit/SKILL.md` (after Quick Start section)

**Step 1: Find Quick Start section end**

```bash
grep -n "Quick Start\|## Pipeline" plugins/plugin-dev/skills/plugin-audit/SKILL.md
```

**Step 2: Add fallback note after Quick Start**

Insert before "## Pipeline Overview":

```markdown
**If scripts unavailable:** Perform manual checks — verify JSON syntax with `jq`, check required fields exist, scan for hardcoded paths using Grep.

```

**Step 3: Verify insertion**

```bash
grep -B 2 -A 2 "scripts unavailable" plugins/plugin-dev/skills/plugin-audit/SKILL.md
```

**Step 4: Commit**

```bash
git add plugins/plugin-dev/skills/plugin-audit/SKILL.md
git commit -m "docs(plugin-audit): add fallback instructions when scripts unavailable"
```

---

## Task 17: Final Validation

**Step 1: Run syntax validation on plugin**

```bash
bash plugins/plugin-dev/skills/plugin-audit/scripts/check-syntax.sh plugins/plugin-dev
echo "Exit code: $?"
```

Expected: Exit code 0

**Step 2: Run structure validation**

```bash
bash plugins/plugin-dev/skills/plugin-audit/scripts/check-structure.sh plugins/plugin-dev
echo "Exit code: $?"
```

Expected: Exit code 0

**Step 3: Verify all commits**

```bash
git log --oneline -20
```

Expected: 16 commits for optimization work

**Step 4: Review changes summary**

```bash
git diff main --stat
```

---

## Task 18: Prepare for Merge

**Step 1: Ensure all changes committed**

```bash
git status
```

Expected: "nothing to commit, working tree clean"

**Step 2: Push branch (if desired)**

```bash
git push -u origin feat/plugin-dev-optimization-2025-12-30
```

**Step 3: Report completion**

Notify user: "Optimization complete. 16 commits across 18 files. Ready to merge or create PR."
