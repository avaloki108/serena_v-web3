# Upstream Synchronization Guide

This guide explains how to sync your `serena_v-web3` fork with the upstream `oraios/serena` repository while preserving your custom Web3 features.

## Overview

The `serena_v-web3` repository is a fork of `oraios/serena` with additional Web3 vulnerability hunting capabilities. To stay up-to-date with the latest improvements from the upstream project while keeping your Web3 enhancements, you need to regularly sync with upstream.

## Quick Start

To sync with upstream, simply run:

```bash
./scripts/sync_with_upstream.sh
```

This script will:
1. ✅ Stash any uncommitted changes
2. ✅ Add/update the upstream remote
3. ✅ Fetch the latest changes from upstream
4. ✅ Merge upstream changes into your current branch
5. ✅ Restore your stashed changes
6. ✅ Verify that your Web3 files are intact

## Script Options

### Dry Run Mode

To preview what the script will do without making any changes:

```bash
./scripts/sync_with_upstream.sh --dry-run
```

### Sync from a Different Branch

By default, the script syncs from the `main` branch. To sync from a different branch:

```bash
./scripts/sync_with_upstream.sh --branch develop
```

### Help

To see all available options:

```bash
./scripts/sync_with_upstream.sh --help
```

## What Gets Synced?

When you run the sync script, you'll receive:

- 🔄 **Core Updates**: Bug fixes, performance improvements, and new features from the upstream Serena project
- 🔄 **Language Support**: New programming language support and LSP improvements
- 🔄 **Tool Enhancements**: Improvements to existing tools and new tool additions
- 🔄 **Documentation**: Updated documentation and examples
- 🔄 **Security Fixes**: Important security patches and vulnerability fixes

## What Stays Preserved?

Your custom Web3 features will be preserved:

- ✅ `src/serena/tools/web3_tools.py` - Web3 vulnerability hunting tools
- ✅ `src/serena/config/web3_config.py` - Web3 configuration
- ✅ `test/serena/test_web3_tools.py` - Web3 tool tests
- ✅ `docs/web3_*.md` - Web3 documentation
- ✅ `examples/web3_security_demo.py` - Web3 examples
- ✅ `WEB3_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- ✅ `WEB3_LANGUAGE_IMPLEMENTATION.md` - Language implementation details

## Manual Sync Process

If you prefer to sync manually or need more control, follow these steps:

### 1. Ensure Clean Working Directory

```bash
# Check for uncommitted changes
git status

# If you have changes, stash them
git stash push -m "My work in progress"
```

### 2. Add Upstream Remote (First Time Only)

```bash
git remote add upstream https://github.com/oraios/serena.git
```

To verify the remote was added:

```bash
git remote -v
```

You should see both `origin` (your fork) and `upstream` (oraios/serena).

### 3. Fetch Upstream Changes

```bash
git fetch upstream main
```

### 4. Merge Upstream Changes

```bash
# Make sure you're on your main branch or the branch you want to update
git checkout main

# Merge upstream changes
git merge upstream/main
```

### 5. Restore Your Changes

If you stashed changes in step 1:

```bash
git stash pop
```

### 6. Push to Your Fork

```bash
git push origin main
```

## Handling Merge Conflicts

If you encounter merge conflicts during the sync:

1. **Don't Panic**: Conflicts are normal when syncing, especially if both repositories modified the same files.

2. **Identify Conflicting Files**:
   ```bash
   git status
   ```
   Files with conflicts will be marked as "both modified".

3. **Resolve Each Conflict**:
   - Open the conflicting file in your editor
   - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
   - Choose which changes to keep or merge them manually
   - Remove the conflict markers

4. **Mark as Resolved**:
   ```bash
   git add <resolved-file>
   ```

5. **Complete the Merge**:
   ```bash
   git commit
   ```

6. **Restore Stashed Changes** (if any):
   ```bash
   git stash pop
   ```

### Common Conflict Scenarios

#### Scenario 1: Both Repos Modified README.md

If both upstream and your fork modified `README.md`, you'll need to merge the changes. Typically:
- Keep your Web3 feature descriptions
- Incorporate upstream's new features or fixes
- Preserve both sets of changes

#### Scenario 2: Core Tool Files Changed

If upstream modified core tool files that your Web3 tools depend on:
- Keep your Web3-specific changes
- Incorporate upstream improvements
- Test thoroughly after merging

#### Scenario 3: Configuration File Conflicts

For files like `pyproject.toml` or configuration files:
- Merge dependencies (keep both yours and upstream's)
- Preserve your Web3-specific configurations
- Ensure no duplicate entries

## Testing After Sync

After syncing, always test your installation:

### 1. Format and Type Check

```bash
uv run poe format
uv run poe type-check
```

### 2. Run Tests

```bash
# Run all tests
uv run poe test

# Run only Web3 tests
uv run poe test test/serena/test_web3_tools.py
```

### 3. Test Web3 Features

```bash
# Run the Web3 demo
python examples/web3_security_demo.py
```

### 4. Verify MCP Server

```bash
uv run serena-mcp-server --help
```

## Sync Schedule Recommendations

- 🗓️ **Weekly**: Check for upstream updates if you're actively developing
- 🗓️ **Bi-weekly**: Sync if you're in maintenance mode
- 🗓️ **Before Major Changes**: Always sync before starting significant new features
- 🗓️ **After Upstream Releases**: Sync when upstream announces new releases

## Keeping Your Fork Up to Date

### Strategy 1: Main Branch Tracks Upstream

Keep your `main` branch in sync with upstream and do all development in feature branches:

```bash
# On main branch
./scripts/sync_with_upstream.sh
git push origin main

# Create feature branch for your work
git checkout -b feature/my-new-web3-feature
```

### Strategy 2: Separate Upstream Branch

Maintain a separate branch that tracks upstream:

```bash
# Create upstream tracking branch
git checkout -b upstream-main
./scripts/sync_with_upstream.sh

# Merge into your main when ready
git checkout main
git merge upstream-main
```

## Troubleshooting

### Problem: "Failed to fetch from upstream"

**Solution**: Check your internet connection and verify the upstream URL:
```bash
git remote get-url upstream
```

### Problem: "Merge conflicts in many files"

**Solution**: If you have extensive conflicts, consider:
1. Creating a backup branch first: `git branch backup-before-sync`
2. Using a merge tool: `git mergetool`
3. Syncing more frequently to avoid large divergences

### Problem: "Stash pop failed"

**Solution**: Your stashed changes conflict with merged changes:
```bash
# View your stash
git stash show -p

# Apply stash without removing it
git stash apply

# Resolve conflicts, then drop the stash
git stash drop
```

### Problem: "Lost my Web3 files after sync"

**Solution**: If files are missing after sync:
```bash
# Check if they were deleted in the merge
git log --all --full-history -- path/to/missing/file

# Restore from previous commit if needed
git checkout HEAD@{1} -- path/to/missing/file
```

## Advanced: Rebasing Instead of Merging

For a cleaner history, you can rebase instead of merge:

```bash
# Fetch upstream
git fetch upstream main

# Rebase your branch onto upstream
git rebase upstream/main

# If conflicts occur, resolve them and continue
git add <resolved-files>
git rebase --continue

# Force push to your fork (only do this on branches you own)
git push origin main --force-with-lease
```

⚠️ **Warning**: Only use `--force-with-lease` on branches where you're the sole contributor!

## Getting Help

If you encounter issues during sync:

1. Check this guide for common solutions
2. Review the script output for specific error messages
3. Create an issue in your repository with:
   - The exact command you ran
   - The error message
   - Your git status output

## Additional Resources

- [Git Documentation on Syncing a Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
- [Upstream Serena Repository](https://github.com/oraios/serena)
- [Upstream Serena Documentation](https://oraios.github.io/serena/)

---

**Remember**: Regular syncing keeps your fork healthy and makes merging easier! 🚀
