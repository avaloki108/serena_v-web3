#!/bin/bash

###############################################################################
# Upstream Sync Script for serena_v-web3
###############################################################################
# This script synchronizes the local fork with the upstream oraios/serena
# repository while preserving all custom Web3 features and modifications.
#
# Usage:
#   ./scripts/sync_with_upstream.sh [--dry-run] [--branch BRANCH]
#
# Options:
#   --dry-run           Show what would be done without making changes
#   --branch BRANCH     Specify upstream branch to sync from (default: main)
#   --help              Show this help message
#
# The script performs the following steps:
#   1. Validates the current git state
#   2. Stashes any uncommitted local changes
#   3. Adds upstream remote if not already configured
#   4. Fetches latest changes from upstream
#   5. Merges upstream changes into current branch
#   6. Re-applies stashed changes if any
#   7. Reports sync status and any conflicts
###############################################################################

set -e  # Exit on error

# Default values
UPSTREAM_REPO="https://github.com/oraios/serena.git"
UPSTREAM_REMOTE="upstream"
UPSTREAM_BRANCH="main"
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --branch)
            UPSTREAM_BRANCH="$2"
            shift 2
            ;;
        --help)
            sed -n '2,/^$/p' "$0" | sed 's/^# //;s/^#//'
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Navigate to repository root
cd "$REPO_ROOT"

print_header "Upstream Sync Script for serena_v-web3"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN MODE - No changes will be made"
fi

# Step 1: Validate git repository
print_info "Step 1: Validating git repository..."

if [ ! -d .git ]; then
    print_error "Not a git repository!"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    HAS_UNCOMMITTED=true
    print_warning "You have uncommitted changes that will be stashed"
    git status --short
else
    HAS_UNCOMMITTED=false
    print_success "Working directory is clean"
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_info "Current branch: $CURRENT_BRANCH"

# Step 2: Stash uncommitted changes if any
if [ "$HAS_UNCOMMITTED" = true ]; then
    print_info "Step 2: Stashing uncommitted changes..."
    
    if [ "$DRY_RUN" = false ]; then
        STASH_MESSAGE="sync_with_upstream_$(date +%Y%m%d_%H%M%S)"
        git stash push -m "$STASH_MESSAGE"
        print_success "Changes stashed as: $STASH_MESSAGE"
        STASHED=true
    else
        print_info "[DRY RUN] Would stash uncommitted changes"
        STASHED=false
    fi
else
    print_info "Step 2: No uncommitted changes to stash"
    STASHED=false
fi

# Step 3: Configure upstream remote
print_info "Step 3: Configuring upstream remote..."

if git remote | grep -q "^${UPSTREAM_REMOTE}$"; then
    CURRENT_UPSTREAM=$(git remote get-url "$UPSTREAM_REMOTE")
    if [ "$CURRENT_UPSTREAM" != "$UPSTREAM_REPO" ]; then
        print_warning "Upstream remote exists with different URL: $CURRENT_UPSTREAM"
        print_info "Updating to: $UPSTREAM_REPO"
        
        if [ "$DRY_RUN" = false ]; then
            git remote set-url "$UPSTREAM_REMOTE" "$UPSTREAM_REPO"
            print_success "Upstream remote updated"
        else
            print_info "[DRY RUN] Would update upstream remote URL"
        fi
    else
        print_success "Upstream remote already configured correctly"
    fi
else
    print_info "Adding upstream remote: $UPSTREAM_REPO"
    
    if [ "$DRY_RUN" = false ]; then
        git remote add "$UPSTREAM_REMOTE" "$UPSTREAM_REPO"
        print_success "Upstream remote added"
    else
        print_info "[DRY RUN] Would add upstream remote"
    fi
fi

# Step 4: Fetch from upstream
print_info "Step 4: Fetching from upstream..."

if [ "$DRY_RUN" = false ]; then
    if git fetch "$UPSTREAM_REMOTE" "$UPSTREAM_BRANCH" --tags; then
        print_success "Fetched latest changes from upstream/$UPSTREAM_BRANCH"
    else
        print_error "Failed to fetch from upstream"
        
        # Restore stashed changes before exiting
        if [ "$STASHED" = true ]; then
            print_info "Restoring stashed changes..."
            git stash pop
        fi
        exit 1
    fi
else
    print_info "[DRY RUN] Would fetch from $UPSTREAM_REMOTE/$UPSTREAM_BRANCH"
fi

# Show what commits would be merged
print_info "Commits that will be merged from upstream:"
if [ "$DRY_RUN" = false ]; then
    MERGE_BASE=$(git merge-base HEAD "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" 2>/dev/null || echo "")
    if [ -n "$MERGE_BASE" ]; then
        COMMIT_COUNT=$(git rev-list --count HEAD.."$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" 2>/dev/null || echo "0")
        echo "  New commits from upstream: $COMMIT_COUNT"
        
        if [ "$COMMIT_COUNT" -gt 0 ]; then
            git log --oneline --graph --decorate HEAD.."$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" | head -20
        else
            print_success "Already up to date with upstream"
        fi
    fi
else
    print_info "[DRY RUN] Would show commit preview"
fi

# Step 5: Merge upstream changes
print_info "Step 5: Merging upstream changes..."

if [ "$DRY_RUN" = false ]; then
    # Attempt to merge (allow unrelated histories for forked repos)
    if git merge "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" --no-edit --allow-unrelated-histories -m "Merge upstream $UPSTREAM_BRANCH into $CURRENT_BRANCH"; then
        print_success "Successfully merged upstream changes"
        MERGE_SUCCESS=true
    else
        print_warning "Merge conflicts detected!"
        print_info "Conflicting files:"
        git diff --name-only --diff-filter=U
        
        echo ""
        print_warning "Please resolve conflicts manually, then run:"
        echo "  git add <resolved-files>"
        echo "  git commit"
        
        if [ "$STASHED" = true ]; then
            echo ""
            print_warning "After resolving conflicts, restore your stashed changes with:"
            echo "  git stash pop"
        fi
        
        MERGE_SUCCESS=false
        exit 1
    fi
else
    print_info "[DRY RUN] Would merge $UPSTREAM_REMOTE/$UPSTREAM_BRANCH"
    MERGE_SUCCESS=true
fi

# Step 6: Restore stashed changes
if [ "$STASHED" = true ] && [ "$MERGE_SUCCESS" = true ]; then
    print_info "Step 6: Restoring stashed changes..."
    
    if [ "$DRY_RUN" = false ]; then
        if git stash pop; then
            print_success "Stashed changes restored successfully"
        else
            print_error "Failed to apply stashed changes"
            print_info "Your changes are still in the stash. Use 'git stash list' to see them."
            print_info "You can manually apply them with 'git stash pop' after resolving any issues."
            exit 1
        fi
    else
        print_info "[DRY RUN] Would restore stashed changes"
    fi
else
    print_info "Step 6: No stashed changes to restore"
fi

# Step 7: Summary and recommendations
print_header "Sync Complete!"

print_success "Successfully synchronized with upstream/$UPSTREAM_BRANCH"

echo ""
print_info "Recommended next steps:"
echo "  1. Review the changes: git log --oneline -10"
echo "  2. Test your application to ensure Web3 features still work"
echo "  3. Run tests: uv run poe test"
echo "  4. Push changes to your fork: git push origin $CURRENT_BRANCH"

# Display custom Web3 files for reference
echo ""
print_info "Your custom Web3 files (verify these are intact):"
WEB3_FILES=(
    "src/serena/tools/web3_tools.py"
    "src/serena/config/web3_config.py"
    "test/serena/test_web3_tools.py"
    "docs/web3_security.md"
    "docs/web3_architecture.md"
    "docs/web3_languages.md"
    "examples/web3_security_demo.py"
    "WEB3_IMPLEMENTATION_SUMMARY.md"
    "WEB3_LANGUAGE_IMPLEMENTATION.md"
)

for file in "${WEB3_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING - may have been affected by merge)"
    fi
done

echo ""
print_success "Upstream sync completed successfully!"

exit 0
