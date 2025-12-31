# SkillCreator Sync Workflow Design

> **⚠️ SUPERSEDED (2025-12-31):** The upstream repository was renamed from `tripleyak/skill-creator-and-improver` to `tripleyak/SkillForge` and the skill was renamed from `skillcreator` to `skillforge`.
>
> - Migration documentation: [`plugins/plugin-dev/docs/migrations/skillcreator-to-skillforge.md`](../../plugins/plugin-dev/docs/migrations/skillcreator-to-skillforge.md)
> - Current workflow: [`.github/workflows/sync-skillforge.yml`](../../.github/workflows/sync-skillforge.yml)
>
> *Original plan preserved below for historical reference.*

---

**Goal:** Keep `plugins/plugin-dev/skills/skillcreator/` synchronized with the upstream repository [tripleyak/skill-creator-and-improver](https://github.com/tripleyak/skill-creator-and-improver).

**Constraints:**
- Plugin-dev must remain self-contained (all skills bundled)
- Users must always get the latest SkillCreator version
- Sync only on upstream releases (not every commit)
- No push access to upstream repo

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Check upstream  │────▶│ Compare versions │────▶│ New release?    │
│ latest release  │     │ (upstream vs     │     │                 │
│ via GitHub API  │     │  local SKILL.md) │     │ No ──▶ Exit     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                         │ Yes
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Create PR with  │◀────│ Run validation   │◀────│ Sync files      │
│ diff + results  │     │ (quick_validate) │     │ (rsync w/       │
│                 │     │                  │     │  exclusions)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sync trigger | GitHub Releases | Releases represent intentional publishes, not WIP |
| Poll frequency | Every 48 hours | Balances responsiveness with CI efficiency |
| Version tracking | Parse SKILL.md frontmatter | No separate tracking file needed |
| On new release | Auto-create PR | Human reviews before merge |
| Validation failure | Create PR anyway | Failure indicates upstream issue; surface it, don't hide it |

---

## Sync Scope

| Include | Exclude |
|---------|---------|
| `SKILL.md` | `README.md` (repo-level, not skill docs) |
| `references/*` | `LICENSE` (plugin-dev has its own) |
| `assets/templates/*` | `.gitignore` (repo-level) |
| `scripts/*` | `assets/images/*` (only used by README) |
| `.sync-metadata` (generated) | `.git`, `.github` |

---

## Workflow File

**Location:** `.github/workflows/sync-skillcreator.yml`

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

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No upstream releases | Workflow exits with warning |
| No local skillcreator | Version defaults to `0.0.0`; first sync creates directory |
| Validation script missing | Skips validation; notes in PR |
| PR branch exists | Updates existing PR |
| Network failure | Workflow fails; retries on next schedule |

---

## Testing the Workflow

1. **Manual trigger:** Run workflow with `force_sync: true` to test end-to-end
2. **Verify PR contents:** Check version diff, validation output, release notes appear
3. **Merge and verify:** Confirm files synced correctly to plugin-dev

---

## Related

- [Existing integration plan](./2025-12-30-skillcreator-integration.md) — Predates this design; superseded for sync approach
- [Plugin-dev README](../../plugins/plugin-dev/README.md) — Documents skillcreator skill
