#!/usr/bin/env bash
#
# release.sh - Atomically release a plugin version
#
# Updates all version references across the monorepo and creates a tagged commit.
#
# Usage:
#   ./scripts/release.sh <plugin-name> <version> [options]
#
# Examples:
#   ./scripts/release.sh plugin-dev 1.3.0
#   ./scripts/release.sh plugin-dev 1.3.0 --dry-run
#   ./scripts/release.sh deep-analysis 0.2.0 --yes
#
# Options:
#   --dry-run   Preview changes without applying
#   --yes       Skip confirmation prompt
#   --force     Allow dirty tree, same version, etc.
#   --verbose   Show detailed output
#   --help      Show this help message
#

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"

# Auto-discover valid plugins (directories with .claude-plugin/plugin.json)
discover_plugins() {
    local plugins=()
    for dir in "$PLUGINS_DIR"/*/; do
        if [[ -f "${dir}.claude-plugin/plugin.json" ]]; then
            plugins+=("$(basename "$dir")")
        fi
    done
    echo "${plugins[@]}"
}

VALID_PLUGINS=($(discover_plugins))

# Colors (disabled if not a terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

# -----------------------------------------------------------------------------
# Options (set by parse_args)
# -----------------------------------------------------------------------------

PLUGIN=""
VERSION=""
DRY_RUN=false
FORCE=false
YES=false
VERBOSE=false

# State
CURRENT_VERSION=""
FILES_TO_UPDATE=()

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

log() { echo -e "$*"; }
log_verbose() { [[ "$VERBOSE" == "true" ]] && echo -e "${BLUE}[verbose]${NC} $*" || true; }
log_success() { echo -e "${GREEN}✓${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $*"; }
log_error() { echo -e "${RED}✗${NC} $*" >&2; }

die() {
    log_error "$1"
    exit 1
}

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

show_help() {
    cat << EOF
release.sh - Atomically release a plugin version

USAGE:
    ./scripts/release.sh <plugin-name> <version> [options]

ARGUMENTS:
    plugin-name    One of: ${VALID_PLUGINS[*]}
    version        Semantic version (e.g., 1.2.3)

OPTIONS:
    --dry-run      Preview changes without applying them
    --yes          Skip confirmation prompt
    --force        Allow dirty working tree and same-version releases
    --verbose      Show detailed output
    --help         Show this help message

EXAMPLES:
    # Standard release
    ./scripts/release.sh plugin-dev 1.3.0

    # Preview what would change
    ./scripts/release.sh plugin-dev 1.3.0 --dry-run

    # Non-interactive release
    ./scripts/release.sh plugin-dev 1.3.0 --yes

FILES UPDATED:
    - plugins/<name>/.claude-plugin/plugin.json
    - plugins/<name>/README.md (if has ## Version section)
    - README.md (root - version table)
    - CHANGELOG.md (new section + version table)
    - plugins/<name>/mcp/pyproject.toml (deep-analysis only)

GIT OPERATIONS:
    - Creates commit: "release(<plugin>): v<version>"
    - Creates tag: "<plugin>-v<version>"

NEXT STEPS AFTER RELEASE:
    1. Edit CHANGELOG.md to fill in release notes
    2. Amend the commit: git commit --amend
    3. Push with tags: git push origin main --tags
EOF
}

# -----------------------------------------------------------------------------
# Argument Parsing
# -----------------------------------------------------------------------------

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --yes|-y)
                YES=true
                shift
                ;;
            --force|-f)
                FORCE=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            -*)
                die "Unknown option: $1\nRun with --help for usage."
                ;;
            *)
                if [[ -z "$PLUGIN" ]]; then
                    PLUGIN="$1"
                elif [[ -z "$VERSION" ]]; then
                    VERSION="$1"
                else
                    die "Unexpected argument: $1\nRun with --help for usage."
                fi
                shift
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$PLUGIN" ]] || [[ -z "$VERSION" ]]; then
        die "Missing required arguments.\n\nUsage: ./scripts/release.sh <plugin-name> <version>\nRun with --help for more information."
    fi
}

# -----------------------------------------------------------------------------
# Validation Functions
# -----------------------------------------------------------------------------

validate_plugin() {
    local valid=false
    for p in "${VALID_PLUGINS[@]}"; do
        if [[ "$p" == "$PLUGIN" ]]; then
            valid=true
            break
        fi
    done

    if [[ "$valid" != "true" ]]; then
        die "Unknown plugin: $PLUGIN\n\nValid plugins: ${VALID_PLUGINS[*]}"
    fi

    # Verify plugin directory exists
    if [[ ! -d "$PLUGINS_DIR/$PLUGIN" ]]; then
        die "Plugin directory not found: $PLUGINS_DIR/$PLUGIN"
    fi

    # Verify plugin.json exists
    if [[ ! -f "$PLUGINS_DIR/$PLUGIN/.claude-plugin/plugin.json" ]]; then
        die "Plugin manifest not found: $PLUGINS_DIR/$PLUGIN/.claude-plugin/plugin.json"
    fi

    log_verbose "Plugin validated: $PLUGIN"
}

validate_version() {
    # Check semver format (X.Y.Z)
    if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        die "Invalid version format: $VERSION\n\nExpected semantic version (e.g., 1.2.3)"
    fi

    log_verbose "Version format validated: $VERSION"
}

get_current_version() {
    local plugin_json="$PLUGINS_DIR/$PLUGIN/.claude-plugin/plugin.json"

    # Extract version using grep (portable, no jq dependency)
    CURRENT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$plugin_json" | \
                      grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)

    if [[ -z "$CURRENT_VERSION" ]]; then
        die "Could not extract current version from $plugin_json"
    fi

    log_verbose "Current version: $CURRENT_VERSION"
}

# Compare two semver versions. Returns 0 if $1 > $2, 1 otherwise
version_gt() {
    local v1="$1" v2="$2"

    # Split versions into arrays
    IFS='.' read -ra V1_PARTS <<< "$v1"
    IFS='.' read -ra V2_PARTS <<< "$v2"

    for i in 0 1 2; do
        local n1="${V1_PARTS[$i]:-0}"
        local n2="${V2_PARTS[$i]:-0}"
        if (( n1 > n2 )); then
            return 0
        elif (( n1 < n2 )); then
            return 1
        fi
    done

    return 1  # Equal versions
}

check_version_increment() {
    if [[ "$VERSION" == "$CURRENT_VERSION" ]]; then
        if [[ "$FORCE" == "true" ]]; then
            log_warning "Version unchanged ($VERSION) - proceeding with --force"
        else
            die "Version unchanged: $VERSION\n\nTo re-release the same version, use --force"
        fi
    elif ! version_gt "$VERSION" "$CURRENT_VERSION"; then
        if [[ "$FORCE" == "true" ]]; then
            log_warning "New version ($VERSION) is not greater than current ($CURRENT_VERSION) - proceeding with --force"
        else
            die "New version ($VERSION) must be greater than current ($CURRENT_VERSION)\n\nTo downgrade, use --force"
        fi
    fi
}

check_git_clean() {
    if [[ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
        if [[ "$FORCE" == "true" ]]; then
            log_warning "Working tree has uncommitted changes - proceeding with --force"
        else
            die "Working tree has uncommitted changes.\n\nCommit or stash changes first, or use --force to proceed anyway."
        fi
    fi
    log_verbose "Working tree is clean"
}

check_tag_exists() {
    local tag="${PLUGIN}-v${VERSION}"
    if git -C "$REPO_ROOT" tag -l "$tag" | grep -q "^$tag$"; then
        die "Tag already exists: $tag\n\nChoose a different version or delete the existing tag."
    fi
    log_verbose "Tag $tag does not exist"
}

check_preconditions() {
    get_current_version
    check_version_increment
    check_git_clean
    check_tag_exists
}

# -----------------------------------------------------------------------------
# File Detection
# -----------------------------------------------------------------------------

detect_files_to_update() {
    FILES_TO_UPDATE=()

    # 1. plugin.json (always)
    FILES_TO_UPDATE+=("$PLUGINS_DIR/$PLUGIN/.claude-plugin/plugin.json")

    # 2. Plugin README.md (if has ## Version section)
    local plugin_readme="$PLUGINS_DIR/$PLUGIN/README.md"
    if [[ -f "$plugin_readme" ]] && grep -q "^## Version" "$plugin_readme"; then
        FILES_TO_UPDATE+=("$plugin_readme")
    else
        log_verbose "Skipping plugin README (no ## Version section): $plugin_readme"
    fi

    # 3. Root README.md (always)
    FILES_TO_UPDATE+=("$REPO_ROOT/README.md")

    # 4. CHANGELOG.md (always)
    FILES_TO_UPDATE+=("$REPO_ROOT/CHANGELOG.md")

    # 5. pyproject.toml (deep-analysis only)
    if [[ "$PLUGIN" == "deep-analysis" ]]; then
        local pyproject="$PLUGINS_DIR/$PLUGIN/mcp/pyproject.toml"
        if [[ -f "$pyproject" ]]; then
            FILES_TO_UPDATE+=("$pyproject")
        else
            log_warning "pyproject.toml not found: $pyproject"
        fi
    fi
}

# -----------------------------------------------------------------------------
# Preview
# -----------------------------------------------------------------------------

show_preview() {
    log ""
    log "${BOLD}Release: $PLUGIN ${CURRENT_VERSION} → ${VERSION}${NC}"
    log ""

    log "${BOLD}Files to update:${NC}"
    for file in "${FILES_TO_UPDATE[@]}"; do
        # Show relative path
        local rel_path="${file#$REPO_ROOT/}"
        log "  ${GREEN}✓${NC} $rel_path"
    done
    log ""

    log "${BOLD}Git operations:${NC}"
    log "  ${GREEN}✓${NC} Commit: release($PLUGIN): v$VERSION"
    log "  ${GREEN}✓${NC} Tag: ${PLUGIN}-v${VERSION}"
    log ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "${YELLOW}[dry-run]${NC} No changes will be made."
    fi
}

# -----------------------------------------------------------------------------
# Confirmation
# -----------------------------------------------------------------------------

confirm_or_exit() {
    if [[ "$YES" == "true" ]]; then
        log_verbose "Skipping confirmation (--yes)"
        return
    fi

    echo -n "Proceed? [y/N] "
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            return
            ;;
        *)
            log "Aborted."
            exit 0
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Update Functions
# -----------------------------------------------------------------------------

update_plugin_json() {
    local file="$PLUGINS_DIR/$PLUGIN/.claude-plugin/plugin.json"
    log_verbose "Updating plugin.json..."

    # Use sed to replace version
    # Pattern: "version": "X.Y.Z" -> "version": "NEW_VERSION"
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/\"version\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"version\": \"$VERSION\"/" "$file"
    else
        sed -i "s/\"version\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"version\": \"$VERSION\"/" "$file"
    fi

    log_success "Updated plugin.json"
}

update_plugin_readme() {
    local file="$PLUGINS_DIR/$PLUGIN/README.md"

    # Check if file should be updated
    if [[ ! " ${FILES_TO_UPDATE[*]} " =~ " ${file} " ]]; then
        log_verbose "Skipping plugin README (not in update list)"
        return
    fi

    log_verbose "Updating plugin README..."

    # Pattern: After "## Version", replace the version line
    # The version line format is: X.Y.Z - description
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "/^## Version/,/^## /{s/^[0-9]\+\.[0-9]\+\.[0-9]\+/$VERSION/;}" "$file"
    else
        sed -i "/^## Version/,/^## /{s/^[0-9]\+\.[0-9]\+\.[0-9]\+/$VERSION/;}" "$file"
    fi

    log_success "Updated plugin README"
}

update_root_readme() {
    local file="$REPO_ROOT/README.md"
    log_verbose "Updating root README..."

    # Pattern: | **[plugin-name](...) | X.Y.Z | description |
    # We need to match the plugin name in the link and update the version
    local pattern="\(| \*\*\[${PLUGIN}\]([^)]*)\*\* | \)[0-9]\+\.[0-9]\+\.[0-9]\+\( |.*\)"
    local replacement="\1${VERSION}\2"

    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/${pattern}/${replacement}/" "$file"
    else
        sed -i "s/${pattern}/${replacement}/" "$file"
    fi

    log_success "Updated root README"
}

update_changelog() {
    local file="$REPO_ROOT/CHANGELOG.md"
    local today
    today=$(date +%Y-%m-%d)

    log_verbose "Updating CHANGELOG..."

    # 1. Add new release section after the plugin's ## Plugin: heading
    local section_header="## Plugin: $PLUGIN"

    # Create the new section content
    local new_section="### [$VERSION] - $today

<!-- TODO: Fill in release notes -->

#### Added
-

#### Changed
-

#### Fixed
-

"

    # Insert after the section header using awk (more reliable than sed for multi-line)
    awk -v header="$section_header" -v content="$new_section" '
        $0 == header {
            print
            getline  # Skip the blank line after header
            print ""
            printf "%s", content
            next
        }
        { print }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"

    # 2. Update version in the versioning table at the bottom
    # Pattern: | plugin-name | X.Y.Z | Status |
    local table_pattern="\(| ${PLUGIN} | \)[0-9]\+\.[0-9]\+\.[0-9]\+\( |.*\)"
    local table_replacement="\1${VERSION}\2"

    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/${table_pattern}/${table_replacement}/" "$file"
    else
        sed -i "s/${table_pattern}/${table_replacement}/" "$file"
    fi

    # 3. Add version link at the bottom if not exists
    local version_link="[${VERSION}]: https://github.com/jp/claude-code-plugin-development/releases/tag/${PLUGIN}-v${VERSION}"
    if ! grep -q "\[${VERSION}\]:" "$file"; then
        echo "$version_link" >> "$file"
    fi

    log_success "Updated CHANGELOG"
}

update_pyproject() {
    local file="$PLUGINS_DIR/$PLUGIN/mcp/pyproject.toml"

    # Only for deep-analysis
    if [[ "$PLUGIN" != "deep-analysis" ]]; then
        return
    fi

    # Check if file exists
    if [[ ! -f "$file" ]]; then
        log_warning "pyproject.toml not found, skipping"
        return
    fi

    log_verbose "Updating pyproject.toml..."

    # Pattern: version = "X.Y.Z"
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" "$file"
    else
        sed -i "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" "$file"
    fi

    log_success "Updated pyproject.toml"
}

apply_changes() {
    log ""
    update_plugin_json
    update_plugin_readme
    update_root_readme
    update_changelog
    update_pyproject
}

# -----------------------------------------------------------------------------
# Git Operations
# -----------------------------------------------------------------------------

git_operations() {
    log ""
    log_verbose "Staging changes..."

    for file in "${FILES_TO_UPDATE[@]}"; do
        git -C "$REPO_ROOT" add "$file"
    done

    log_verbose "Creating commit..."
    git -C "$REPO_ROOT" commit -m "release($PLUGIN): v$VERSION

Updates version to $VERSION across all references.

Files updated:
$(for f in "${FILES_TO_UPDATE[@]}"; do echo "- ${f#$REPO_ROOT/}"; done)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    log_success "Created commit"

    log_verbose "Creating tag..."
    git -C "$REPO_ROOT" tag "${PLUGIN}-v${VERSION}"
    log_success "Created tag: ${PLUGIN}-v${VERSION}"
}

# -----------------------------------------------------------------------------
# Next Steps
# -----------------------------------------------------------------------------

show_next_steps() {
    log ""
    log "${GREEN}${BOLD}✓ Released $PLUGIN v$VERSION${NC}"
    log ""
    log "${BOLD}Next steps:${NC}"
    log "  1. Edit CHANGELOG.md to fill in release notes"
    log "  2. Amend the commit: ${BLUE}git commit --amend${NC}"
    log "  3. Push with tags: ${BLUE}git push origin main --tags${NC}"
    log ""
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main() {
    parse_args "$@"
    validate_plugin
    validate_version
    check_preconditions
    detect_files_to_update
    show_preview

    if [[ "$DRY_RUN" == "true" ]]; then
        exit 0
    fi

    confirm_or_exit
    apply_changes
    git_operations
    show_next_steps
}

main "$@"
