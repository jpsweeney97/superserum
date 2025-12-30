# SkillCreator Integration into Plugin-Dev

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate SkillCreator (v3.1) into plugin-dev to provide a rigorous, quality-gated skill creation methodology with 11 thinking lenses, evolution scoring, and multi-agent synthesis.

**Architecture:** SkillCreator becomes a new skill in plugin-dev that complements existing `skill-development` (structural reference) and `writing-skills` (TDD testing). A new `/create-skill` command provides the entry point. The existing `skill-reviewer` agent is enhanced with evolution/timelessness scoring criteria from SkillCreator. Validation scripts are added for pre-packaging checks.

**Tech Stack:** Claude Code plugins (skills, commands, agents), Python 3.8+ (validation scripts), Bash, YAML frontmatter

---

## Pre-Implementation Checklist

- [ ] Verify skillcreator directory exists at `/Users/jp/Projects/active/claude-code-plugin-development/skillcreator/`
- [ ] Verify plugin-dev manifest at `plugins/plugin-dev/.claude-plugin/plugin.json`
- [ ] Confirm current plugin-dev version is 1.2.0

---

## Task 1: Copy SkillCreator Skill to Plugin-Dev

**Files:**
- Create: `plugins/plugin-dev/skills/skillcreator/SKILL.md`
- Create: `plugins/plugin-dev/skills/skillcreator/references/multi-lens-framework.md`
- Create: `plugins/plugin-dev/skills/skillcreator/references/regression-questions.md`
- Create: `plugins/plugin-dev/skills/skillcreator/references/evolution-scoring.md`
- Create: `plugins/plugin-dev/skills/skillcreator/references/specification-template.md`
- Create: `plugins/plugin-dev/skills/skillcreator/references/synthesis-protocol.md`

**Step 1: Create skillcreator directory structure**

```bash
mkdir -p plugins/plugin-dev/skills/skillcreator/references
mkdir -p plugins/plugin-dev/skills/skillcreator/assets/templates
```

**Step 2: Copy SKILL.md with updated description**

Copy `skillcreator/SKILL.md` to `plugins/plugin-dev/skills/skillcreator/SKILL.md`

Modify the description to avoid trigger overlap with existing skills:

```yaml
---
name: skillcreator
description: "Use when creating production-grade skills that need rigorous analysis, evolution scoring, and multi-agent review. Triggers: 'SkillCreator:', 'ultimate skill', 'best possible skill', 'rigorous skill creation'. For simple skill structure, see skill-development. For TDD testing, see writing-skills."
license: MIT
metadata:
  version: 3.1.0
  model: claude-opus-4-5-20251101
  subagent_model: claude-opus-4-5-20251101
  domains: [meta-skill, automation, skill-creation, orchestration]
  type: orchestrator
  inputs: [user-goal, domain-hints]
  outputs: [SKILL.md, references/, SKILL_SPEC.md]
---
```

**Step 3: Copy all reference files**

```bash
cp skillcreator/references/multi-lens-framework.md plugins/plugin-dev/skills/skillcreator/references/
cp skillcreator/references/regression-questions.md plugins/plugin-dev/skills/skillcreator/references/
cp skillcreator/references/evolution-scoring.md plugins/plugin-dev/skills/skillcreator/references/
cp skillcreator/references/specification-template.md plugins/plugin-dev/skills/skillcreator/references/
cp skillcreator/references/synthesis-protocol.md plugins/plugin-dev/skills/skillcreator/references/
```

**Step 4: Copy template files**

```bash
cp skillcreator/assets/templates/skill-md-template.md plugins/plugin-dev/skills/skillcreator/assets/templates/
cp skillcreator/assets/templates/skill-spec-template.xml plugins/plugin-dev/skills/skillcreator/assets/templates/
```

**Step 5: Verify file structure**

```bash
find plugins/plugin-dev/skills/skillcreator -type f | sort
```

Expected output:
```
plugins/plugin-dev/skills/skillcreator/SKILL.md
plugins/plugin-dev/skills/skillcreator/assets/templates/skill-md-template.md
plugins/plugin-dev/skills/skillcreator/assets/templates/skill-spec-template.xml
plugins/plugin-dev/skills/skillcreator/references/evolution-scoring.md
plugins/plugin-dev/skills/skillcreator/references/multi-lens-framework.md
plugins/plugin-dev/skills/skillcreator/references/regression-questions.md
plugins/plugin-dev/skills/skillcreator/references/specification-template.md
plugins/plugin-dev/skills/skillcreator/references/synthesis-protocol.md
```

**Step 6: Commit**

```bash
git add plugins/plugin-dev/skills/skillcreator/
git commit -m "feat(plugin-dev): add skillcreator skill for rigorous skill creation"
```

---

## Task 2: Create /create-skill Command

**Files:**
- Create: `plugins/plugin-dev/commands/create-skill.md`

**Step 1: Write the command file**

Create `plugins/plugin-dev/commands/create-skill.md`:

```markdown
---
description: Create a new skill using SkillCreator's rigorous 4-phase methodology with analysis, specification, generation, and multi-agent review
allowed-tools: [Task, Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Skill]
model: claude-opus-4-5-20251101
---

# Create Skill

Create a production-ready Claude Code skill using SkillCreator methodology.

## Usage

```
/plugin-dev:create-skill <goal>
/plugin-dev:create-skill --quick <goal>
/plugin-dev:create-skill --plan-only <goal>
```

## Options

| Option | Effect |
|--------|--------|
| (none) | Full 4-phase methodology with synthesis panel |
| `--quick` | Streamlined creation (skip multi-lens deep dives) |
| `--plan-only` | Generate specification only, no generation |

## Process

This command invokes the `skillcreator` skill which executes:

1. **Phase 1: Deep Analysis** - 11 thinking lenses, regression questioning
2. **Phase 2: Specification** - XML spec with evolution scoring (≥7 required)
3. **Phase 3: Generation** - SKILL.md, references/, assets/
4. **Phase 4: Synthesis Panel** - 3 Opus agents must unanimously approve

## Execution

Load and follow the skillcreator skill:

**REQUIRED:** Use the `skillcreator` skill to create the requested skill.

Parse the user's goal from the command arguments. If `--quick` is specified, inform the skill to use reduced analysis depth. If `--plan-only` is specified, stop after Phase 2.

After completion, run validation:

```bash
python plugins/plugin-dev/scripts/quick_validate.py <skill-path>
```

## Related

- `skill-development` - Structural reference for skill anatomy
- `writing-skills` - TDD testing methodology
- `skill-reviewer` agent - Post-creation quality review
```

**Step 2: Verify command syntax**

```bash
head -20 plugins/plugin-dev/commands/create-skill.md
```

Expected: Valid YAML frontmatter with description, allowed-tools, model

**Step 3: Commit**

```bash
git add plugins/plugin-dev/commands/create-skill.md
git commit -m "feat(plugin-dev): add /create-skill command for SkillCreator workflow"
```

---

## Task 3: Enhance skill-reviewer Agent with Evolution Scoring

**Files:**
- Modify: `plugins/plugin-dev/agents/skill-reviewer.md`

**Step 1: Read current skill-reviewer**

```bash
cat plugins/plugin-dev/agents/skill-reviewer.md
```

**Step 2: Add evolution/timelessness evaluation section**

After the "Assess Content Quality" section (around line 70), add:

```markdown
5. **Evaluate Evolution/Timelessness**:
   - **Temporal Projection**: Will this skill be relevant in 6mo? 1yr? 2yr?
   - **Extension Points**: Are there clear places where skill can grow?
   - **Dependency Stability**: Does it depend on volatile implementations?
   - **WHY Documentation**: Are decisions explained, not just stated?
   - **Principle-Based**: Does it teach principles over specific implementations?

   **Scoring Rubric:**
   | Score | Description | Verdict |
   |-------|-------------|---------|
   | 1-3 | Transient, obsolete in months | Reject |
   | 4-6 | Moderate, depends on current tooling | Revise |
   | 7-8 | Solid, principle-based, extensible | Approve |
   | 9-10 | Timeless, addresses fundamental problem | Exemplary |

   **Minimum passing score: 7/10**
```

**Step 3: Add evolution section to output format**

In the "Output Format" section, add after "### Progressive Disclosure":

```markdown
### Evolution/Timelessness

**Score:** [X/10]

**Temporal Assessment:**
- 6 months: [projection]
- 1 year: [projection]
- 2 years: [projection]

**Extension Points:**
- [Extension point 1 or "None identified - add extension points"]
- [Extension point 2]

**WHY Documentation:** [Present/Missing - specific examples]

**Verdict:** [PASS (≥7) / NEEDS REVISION (<7)]
```

**Step 4: Update description to include timelessness triggers**

Update the description field to include new trigger phrases:

```yaml
description: |
  Use this agent when the user has created or modified a skill and needs quality review, asks to "review my skill", "check skill quality", "improve skill description", "evaluate skill timelessness", "check skill evolution score", or wants to ensure skill follows best practices. Trigger proactively after skill creation.
```

**Step 5: Commit**

```bash
git add plugins/plugin-dev/agents/skill-reviewer.md
git commit -m "feat(plugin-dev): enhance skill-reviewer with evolution/timelessness scoring"
```

---

## Task 4: Add Validation Scripts

**Files:**
- Create: `plugins/plugin-dev/scripts/validate-skill.py`
- Create: `plugins/plugin-dev/scripts/quick_validate.py`
- Create: `plugins/plugin-dev/scripts/package_skill.py`

**Step 1: Copy validation scripts from skillcreator**

```bash
mkdir -p plugins/plugin-dev/scripts
cp skillcreator/scripts/validate-skill.py plugins/plugin-dev/scripts/
cp skillcreator/scripts/quick_validate.py plugins/plugin-dev/scripts/
cp skillcreator/scripts/package_skill.py plugins/plugin-dev/scripts/
```

**Step 2: Make scripts executable**

```bash
chmod +x plugins/plugin-dev/scripts/validate-skill.py
chmod +x plugins/plugin-dev/scripts/quick_validate.py
chmod +x plugins/plugin-dev/scripts/package_skill.py
```

**Step 3: Test quick_validate on existing skill**

```bash
python plugins/plugin-dev/scripts/quick_validate.py plugins/plugin-dev/skills/skill-development/
```

Expected: PASS or specific validation feedback

**Step 4: Commit**

```bash
git add plugins/plugin-dev/scripts/
git commit -m "feat(plugin-dev): add skill validation and packaging scripts"
```

---

## Task 5: Update Plugin Manifest and README

**Files:**
- Modify: `plugins/plugin-dev/.claude-plugin/plugin.json`
- Modify: `plugins/plugin-dev/README.md`

**Step 1: Update plugin.json version**

Change version from `1.2.0` to `1.3.0`:

```json
{
  "name": "plugin-dev",
  "version": "1.3.0",
  "description": "Comprehensive toolkit for developing, validating, and maintaining high-quality Claude Code plugins",
  "author": { "name": "JP" },
  "keywords": [
    "plugin", "development", "toolkit", "validation", "audit",
    "skills", "commands", "agents", "hooks", "mcp", "skillcreator"
  ]
}
```

**Step 2: Update README.md - Add skillcreator to skills table**

In the Skills section, add:

```markdown
| skillcreator | Rigorous 4-phase skill creation with 11 thinking lenses, evolution scoring, and multi-agent synthesis panel |
```

**Step 3: Update README.md - Add /create-skill to commands table**

In the Commands section, add:

```markdown
| `/plugin-dev:create-skill` | Create skills using SkillCreator's rigorous methodology |
```

**Step 4: Update README.md - Add Skill Creation Workflow section**

Add new section after "Quick Start":

```markdown
## Skill Creation Workflow

Plugin-dev provides three levels of skill creation support:

| Approach | Use When | Tool |
|----------|----------|------|
| **Reference** | Understanding skill structure | `skill-development` skill |
| **TDD Testing** | Validating skill effectiveness | `writing-skills` skill |
| **Full Methodology** | Creating production-grade skills | `/plugin-dev:create-skill` + `skillcreator` |

### Decision Tree

```
Need to create a skill?
├── Simple skill (< 500 words, straightforward)
│   └── Use `skill-development` skill directly
├── Standard skill (need to ensure quality)
│   └── Use `writing-skills` TDD + `skill-development`
└── Complex/critical skill (needs rigorous analysis)
    └── Use `/plugin-dev:create-skill` (SkillCreator methodology)
```

### Validation Scripts

```bash
# Quick validation (required before packaging)
python scripts/quick_validate.py path/to/skill/

# Full structural validation
python scripts/validate-skill.py path/to/skill/

# Package for distribution
python scripts/package_skill.py path/to/skill/ ./dist
```
```

**Step 5: Update README.md - Update version in header**

Update version reference to 1.3.0

**Step 6: Commit**

```bash
git add plugins/plugin-dev/.claude-plugin/plugin.json plugins/plugin-dev/README.md
git commit -m "docs(plugin-dev): update manifest to v1.3.0 and document skillcreator integration"
```

---

## Task 6: Add Cross-References to Existing Skills

**Files:**
- Modify: `plugins/plugin-dev/skills/skill-development/SKILL.md`
- Modify: `plugins/plugin-dev/skills/writing-skills/SKILL.md`

**Step 1: Update skill-development with skillcreator reference**

Add to the "Related" section at the top:

```markdown
## Related

For the **creation process** (TDD, testing, validation workflow), see the `writing-skills` skill.

For **rigorous skill creation** with analysis, evolution scoring, and multi-agent review, use the `skillcreator` skill or `/plugin-dev:create-skill` command.
```

**Step 2: Update writing-skills with skillcreator reference**

Add to the "Related" section:

```markdown
## Related

For **file structure** (directories, SKILL.md format, progressive disclosure), see the `skill-development` skill.

For **full autonomous creation** with 11 thinking lenses, evolution scoring, and synthesis panel, use the `skillcreator` skill.
```

**Step 3: Commit**

```bash
git add plugins/plugin-dev/skills/skill-development/SKILL.md plugins/plugin-dev/skills/writing-skills/SKILL.md
git commit -m "docs(plugin-dev): add cross-references to skillcreator in related skills"
```

---

## Task 7: Final Verification

**Step 1: Verify all files exist**

```bash
echo "=== Skills ===" && ls -la plugins/plugin-dev/skills/skillcreator/
echo "=== Commands ===" && ls -la plugins/plugin-dev/commands/create-skill.md
echo "=== Scripts ===" && ls -la plugins/plugin-dev/scripts/*.py
```

**Step 2: Validate plugin structure**

```bash
cat plugins/plugin-dev/.claude-plugin/plugin.json | python -m json.tool
```

Expected: Valid JSON with version 1.3.0

**Step 3: Test plugin loading**

```bash
claude --plugin-dir plugins/plugin-dev --help
```

Expected: Plugin loads without errors

**Step 4: Run validation on new skillcreator skill**

```bash
python plugins/plugin-dev/scripts/quick_validate.py plugins/plugin-dev/skills/skillcreator/
```

Expected: PASS

**Step 5: View git log**

```bash
git log --oneline -6
```

Expected: 6 commits for this integration

---

## Post-Implementation

After all tasks complete:

1. **Test trigger phrases**: Verify `skillcreator` triggers on "SkillCreator:", "ultimate skill", "best possible skill"
2. **Test `/create-skill`**: Run command and verify it invokes skillcreator skill
3. **Test skill-reviewer**: Review a skill and verify evolution scoring appears in output
4. **Test validation scripts**: Run all three scripts on various skills

## Rollback

If issues arise:

```bash
git revert HEAD~6..HEAD  # Revert all 6 commits
# Or selectively revert specific commits
```
