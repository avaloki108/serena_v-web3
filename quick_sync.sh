#!/bin/bash

###############################################################################
# Quick Sync Script for serena_v-web3
###############################################################################
# This script performs a complete sync workflow:
#   1. Commits or stashes local changes
#   2. Fetches from upstream (oraios/serena:main)
#   3. Pulls and merges upstream changes
#   4. Pushes to origin (avaloki108/serena_v-web3:main)
#
# Usage:
#   ./quick_sync.sh
###############################################################################

set -e  # Exit on error

# Configuration
UPSTREAM_REMOTE="upstream"
UPSTREAM_BRANCH="main"
ORIGIN_REMOTE="origin"
ORIGIN_BRANCH="main"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_header "Quick Sync: serena_v-web3"

# Step 1: Check for uncommitted changes and commit/stash
print_info "Step 1: Checking for uncommitted changes..."

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    print_warning "Uncommitted changes detected"
    git status --short
    
    # Try to commit changes
    print_info "Attempting to commit changes..."
    if git add -A && git commit -m "WIP: Auto-commit before sync ($(date '+%Y-%m-%d %H:%M:%S'))"; then
        print_success "Changes committed"
    else
        # If commit fails, stash instead
        print_info "Commit failed, stashing changes..."
        STASH_MESSAGE="quick_sync_$(date +%Y%m%d_%H%M%S)"
        git stash push -m "$STASH_MESSAGE"
        print_success "Changes stashed as: $STASH_MESSAGE"
        STASHED=true
    fi
else
    print_success "Working directory is clean"
    STASHED=false
fi

# Step 2: Fetch from upstream
print_info "Step 2: Fetching from upstream ($UPSTREAM_REMOTE/$UPSTREAM_BRANCH)..."

if git fetch "$UPSTREAM_REMOTE" "$UPSTREAM_BRANCH"; then
    print_success "Fetched from upstream"
else
    print_error "Failed to fetch from upstream"
    exit 1
fi

# Step 3: Pull and merge from upstream
print_info "Step 3: Pulling and merging from upstream..."

if git pull "$UPSTREAM_REMOTE" "$UPSTREAM_BRANCH" --rebase; then
    print_success "Merged upstream changes"
else
    print_warning "Merge/rebase encountered issues - attempting to continue..."
    # The rebase might be in progress, let user handle it
fi

# Step 4: Pull from origin to sync any remote changes
print_info "Step 4: Syncing with origin ($ORIGIN_REMOTE/$ORIGIN_BRANCH)..."

if git pull "$ORIGIN_REMOTE" "$ORIGIN_BRANCH" --rebase; then
    print_success "Synced with origin"
else
    print_warning "Pull from origin encountered issues"
fi

# Step 5: Push to origin
print_info "Step 5: Pushing to origin ($ORIGIN_REMOTE/$ORIGIN_BRANCH)..."

if git push "$ORIGIN_REMOTE" "$ORIGIN_BRANCH"; then
    print_success "Pushed to origin successfully!"
else
    print_error "Failed to push to origin"
    print_info "You may need to resolve conflicts or force push"
    exit 1
fi

# Step 6: Restore stashed changes if any
if [ "$STASHED" = true ]; then
    print_info "Step 6: Restoring stashed changes..."
    
    if git stash pop; then
        print_success "Stashed changes restored"
    else
        print_warning "Failed to apply stashed changes automatically"
        print_info "Your changes are in the stash. Use 'git stash pop' to apply them manually."
    fi
fi

# Summary
print_header "Sync Complete!"

print_success "Successfully synced with upstream and pushed to origin"

echo ""
print_info "Current status:"
git --no-pager log --oneline -5

echo ""
print_success "Quick sync completed successfully!"

exit 0
