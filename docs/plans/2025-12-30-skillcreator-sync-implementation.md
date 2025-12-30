# SkillCreator Sync Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a GitHub Actions workflow that automatically syncs `plugins/plugin-dev/skills/skillcreator/` from upstream releases.

**Architecture:** Scheduled workflow polls GitHub Releases API every 48 hours, compares versions, syncs files with rsync (excluding repo-level files), runs validation, and creates a PR for human review.

**Tech Stack:** GitHub Actions, bash, rsync, GitHub API, peter-evans/create-pull-request action

**Design Document:** `docs/plans/2025-12-30-skillcreator-sync-design.md`

---

## Pre-Implementation Checklist

- [ ] Working in worktree: `.worktrees/skillcreator-sync`
- [ ] On branch: `feat/skillcreator-sync`
- [ ] Design document committed: `docs/plans/2025-12-30-skillcreator-sync-design.md`

---

## Task 1: Create Workflows Directory

**Files:**
- Create: `.github/workflows/` (directory)

**Step 1: Create directory structure**

```bash
mkdir -p .github/workflows
```

**Step 2: Verify directory exists**

Run: `ls -la .github/`
Expected: `workflows` directory listed

**Step 3: Commit**

```bash
git add .github/
git commit -m "chore: add .github/workflows directory"
```

---

## Task 2: Create Sync Workflow File

**Files:**
- Create: `.github/workflows/sync-skillcreator.yml`

**Step 1: Create the workflow file**

Create `.github/workflows/sync-skillcreator.yml` with this exact content:

```yaml
name: Sync SkillCreator
on:
  schedule:
    - cron: '0 6 */2 * *'  # Every 48 hours at 6 AM UTC
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Sync even if versions match'
        type: boolean
        default: false

permissions:
  contents: write
  pull-requests: write

env:
  UPSTREAM_REPO: tripleyak/skill-creator-and-improver
  TARGET_PATH: plugins/plugin-dev/skills/skillcreator

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Check upstream release exists
        id: release_check
        run: |
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://api.github.com/repos/${{ env.UPSTREAM_REPO }}/releases/latest")

          if [[ "$HTTP_CODE" != "200" ]]; then
            echo "::warning::No releases found upstream (HTTP $HTTP_CODE)"
            echo "exists=false" >> $GITHUB_OUTPUT
          else
            echo "exists=true" >> $GITHUB_OUTPUT
          fi

      - name: Get latest upstream release
        if: steps.release_check.outputs.exists == 'true'
        id: upstream
        run: |
          RELEASE_JSON=$(curl -s "https://api.github.com/repos/${{ env.UPSTREAM_REPO }}/releases/latest")

          TAG=$(echo "$RELEASE_JSON" | jq -r '.tag_name')
          VERSION=$(echo "$TAG" | sed 's/^v//' | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' || echo "$TAG")
          NOTES=$(echo "$RELEASE_JSON" | jq -r '.body // "No release notes"')

          echo "tag=$TAG" >> $GITHUB_OUTPUT
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "notes<<EOF" >> $GITHUB_OUTPUT
          echo "$NOTES" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Get local version
        if: steps.release_check.outputs.exists == 'true'
        id: local
        run: |
          SKILL_FILE="${{ env.TARGET_PATH }}/SKILL.md"
          if [[ -f "$SKILL_FILE" ]]; then
            VERSION=$(grep -oP 'version:\s*\K[\d.]+' "$SKILL_FILE" | head -1)
          else
            VERSION="0.0.0"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Check if sync needed
        if: steps.release_check.outputs.exists == 'true'
        id: check
        run: |
          if [[ "${{ steps.upstream.outputs.version }}" != "${{ steps.local.outputs.version }}" ]] || \
             [[ "${{ inputs.force_sync }}" == "true" ]]; then
            echo "needed=true" >> $GITHUB_OUTPUT
            echo "Sync needed: ${{ steps.local.outputs.version }} → ${{ steps.upstream.outputs.version }}"
          else
            echo "needed=false" >> $GITHUB_OUTPUT
            echo "Already at version ${{ steps.local.outputs.version }}"
          fi

      - name: Sync from upstream
        if: steps.check.outputs.needed == 'true'
        run: |
          # Clone upstream at specific tag
          git clone --depth 1 --branch "${{ steps.upstream.outputs.tag }}" \
            "https://github.com/${{ env.UPSTREAM_REPO }}.git" /tmp/upstream

          # Clean target directory
          rm -rf "${{ env.TARGET_PATH }}"
          mkdir -p "${{ env.TARGET_PATH }}"

          # Sync with exclusions
          rsync -av \
            --exclude='.git' \
            --exclude='.github' \
            --exclude='.gitignore' \
            --exclude='README.md' \
            --exclude='LICENSE' \
            --exclude='assets/images' \
            /tmp/upstream/ "${{ env.TARGET_PATH }}/"

          # Record sync metadata
          cat > "${{ env.TARGET_PATH }}/.sync-metadata" << EOF
          upstream_repo: https://github.com/${{ env.UPSTREAM_REPO }}
          upstream_version: ${{ steps.upstream.outputs.version }}
          upstream_tag: ${{ steps.upstream.outputs.tag }}
          synced_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          EOF

      - name: Validate synced skill
        if: steps.check.outputs.needed == 'true'
        id: validate
        run: |
          SCRIPT="plugins/plugin-dev/scripts/quick_validate.py"

          if [[ -f "$SCRIPT" ]]; then
            set +e
            OUTPUT=$(python "$SCRIPT" "${{ env.TARGET_PATH }}" 2>&1)
            EXIT_CODE=$?
            set -e

            echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
            if [[ $EXIT_CODE -eq 0 ]]; then
              echo "status=✅ PASSED" >> $GITHUB_OUTPUT
            else
              echo "status=⚠️ FAILED (exit code $EXIT_CODE)" >> $GITHUB_OUTPUT
            fi

            echo "output<<EOF" >> $GITHUB_OUTPUT
            echo "$OUTPUT" >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
          else
            echo "status=⏭️ SKIPPED (script not found)" >> $GITHUB_OUTPUT
            echo "output=Validation script not found at $SCRIPT" >> $GITHUB_OUTPUT
            echo "exit_code=0" >> $GITHUB_OUTPUT
          fi

      - name: Create Pull Request
        if: steps.check.outputs.needed == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: |
            chore(plugin-dev): sync skillcreator ${{ steps.local.outputs.version }} → ${{ steps.upstream.outputs.version }}
          branch: auto-sync/skillcreator
          delete-branch: true
          title: "chore(plugin-dev): sync skillcreator to ${{ steps.upstream.outputs.tag }}"
          labels: |
            automated
            dependencies
            plugin-dev
          body: |
            ## SkillCreator Sync

            **Upstream:** [tripleyak/skill-creator-and-improver](https://github.com/${{ env.UPSTREAM_REPO }})
            **Version:** `${{ steps.local.outputs.version }}` → `${{ steps.upstream.outputs.version }}`

            ### Validation

            **Status:** ${{ steps.validate.outputs.status }}

            <details>
            <summary>Validation output</summary>

            ```
            ${{ steps.validate.outputs.output }}
            ```

            </details>

            ### Release Notes

            ${{ steps.upstream.outputs.notes }}

            ---

            <sub>🤖 Created by [sync-skillcreator.yml](.github/workflows/sync-skillcreator.yml)</sub>
```

**Step 2: Validate YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/sync-skillcreator.yml'))"`
Expected: No output (valid YAML)

If Python yaml module not available, use:
Run: `cat .github/workflows/sync-skillcreator.yml | head -20`
Expected: Valid YAML structure visible

**Step 3: Commit**

```bash
git add .github/workflows/sync-skillcreator.yml
git commit -m "feat(ci): add skillcreator sync workflow

Automatically syncs plugins/plugin-dev/skills/skillcreator/ from
upstream tripleyak/skill-creator-and-improver on new releases.

- Polls every 48 hours for new GitHub Releases
- Creates PR with validation results and release notes
- Excludes repo-level files (README, LICENSE, images)"
```

---

## Task 3: Test Workflow Locally (Dry Run)

**Files:**
- Read: `.github/workflows/sync-skillcreator.yml`

**Step 1: Simulate release check**

Test the API call that the workflow will make:

```bash
curl -s "https://api.github.com/repos/tripleyak/skill-creator-and-improver/releases/latest" | jq '{tag: .tag_name, name: .name}'
```

Expected: JSON with tag and release name (e.g., `{"tag": "v3.2", "name": "SkillCreator v3.2"}`)

**Step 2: Simulate version extraction**

```bash
TAG="v3.2"
VERSION=$(echo "$TAG" | sed 's/^v//' | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' || echo "$TAG")
echo "Extracted version: $VERSION"
```

Expected: `Extracted version: 3.2`

**Step 3: Simulate local version check**

```bash
SKILL_FILE="plugins/plugin-dev/skills/skillcreator/SKILL.md"
if [[ -f "$SKILL_FILE" ]]; then
  VERSION=$(grep -oP 'version:\s*\K[\d.]+' "$SKILL_FILE" | head -1)
  echo "Local version: $VERSION"
else
  echo "Local version: 0.0.0 (no file)"
fi
```

Expected: Either version number or `0.0.0 (no file)`

**Step 4: No commit needed**

This task is verification only.

---

## Task 4: Push Branch and Create PR

**Files:**
- None (git operations only)

**Step 1: View commit history**

```bash
git log --oneline -5
```

Expected: 2 commits (workflows directory + workflow file)

**Step 2: Push branch to origin**

```bash
git push -u origin feat/skillcreator-sync
```

Expected: Branch pushed, tracking set up

**Step 3: Create PR**

```bash
gh pr create \
  --title "feat(ci): add skillcreator sync workflow" \
  --body "## Summary

Adds automated GitHub Actions workflow to sync \`plugins/plugin-dev/skills/skillcreator/\` from upstream [tripleyak/skill-creator-and-improver](https://github.com/tripleyak/skill-creator-and-improver).

## Features

- Polls every 48 hours for new GitHub Releases
- Compares upstream version with local SKILL.md version
- Syncs files (excluding README, LICENSE, images)
- Runs validation and includes results in PR
- Creates PR with release notes for human review

## Testing

After merge, trigger manually:
1. Go to Actions → Sync SkillCreator
2. Click 'Run workflow'
3. Check 'Sync even if versions match'
4. Verify PR is created

## Design

See \`docs/plans/2025-12-30-skillcreator-sync-design.md\`

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)" \
  --base main
```

Expected: PR created, URL returned

---

## Task 5: Test Workflow (Post-Merge)

> **Note:** This task runs AFTER the PR is merged to main.

**Step 1: Trigger workflow manually**

Go to: `https://github.com/<owner>/<repo>/actions/workflows/sync-skillcreator.yml`

Click: "Run workflow" → Check "Sync even if versions match" → "Run workflow"

**Step 2: Monitor workflow execution**

Watch the workflow run. Expected steps:
1. ✅ Checkout
2. ✅ Check upstream release exists
3. ✅ Get latest upstream release
4. ✅ Get local version
5. ✅ Check if sync needed (should show "needed=true" with force)
6. ✅ Sync from upstream
7. ✅ Validate synced skill
8. ✅ Create Pull Request

**Step 3: Verify PR created**

Check: A new PR titled "chore(plugin-dev): sync skillcreator to v3.2" (or similar) should appear.

Verify PR contains:
- [ ] Version transition in title
- [ ] Validation status
- [ ] Validation output (collapsed)
- [ ] Release notes from upstream
- [ ] Correct labels (automated, dependencies, plugin-dev)

**Step 4: Review and merge sync PR**

If everything looks correct, merge the sync PR to complete the first automated sync.

---

## Post-Implementation

After all tasks complete:

1. **Clean up worktree:**
   ```bash
   cd /Users/jp/Projects/active/claude-code-plugin-development
   git worktree remove .worktrees/skillcreator-sync
   ```

2. **Delete local branch (if PR merged):**
   ```bash
   git branch -d feat/skillcreator-sync
   ```

3. **Verify scheduled runs:** Check Actions tab in ~48 hours to confirm scheduled trigger works.

---

## Rollback

If workflow causes issues:

```bash
# Disable workflow (don't delete)
git mv .github/workflows/sync-skillcreator.yml .github/workflows/sync-skillcreator.yml.disabled
git commit -m "chore(ci): disable skillcreator sync workflow"
git push
```
