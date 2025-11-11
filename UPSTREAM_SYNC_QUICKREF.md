# Upstream Sync Quick Reference

This repository is a fork of [oraios/serena](https://github.com/oraios/serena) with additional Web3 vulnerability hunting capabilities.

## Quick Sync

To sync with the latest upstream changes while preserving your Web3 features:

```bash
./scripts/sync_with_upstream.sh
```

## Test Before Syncing

To preview what will be synced without making changes:

```bash
./scripts/sync_with_upstream.sh --dry-run
```

## Full Documentation

For detailed instructions, troubleshooting, and manual sync processes, see:

📖 **[docs/UPSTREAM_SYNC.md](docs/UPSTREAM_SYNC.md)**

## What Gets Preserved

All Web3-specific features are automatically preserved during sync:

- ✅ Web3 vulnerability hunting tools
- ✅ Smart contract analysis capabilities
- ✅ Blockchain language support (Solidity, Vyper, Move, Sui Move, Cairo)
- ✅ Web3 documentation and examples
- ✅ Web3 test suites

## Sync Schedule

- **Recommended:** Sync weekly or bi-weekly
- **Before major changes:** Always sync before starting new features
- **After upstream releases:** Sync when upstream announces updates

## Need Help?

If you encounter issues:

1. Check [docs/UPSTREAM_SYNC.md](docs/UPSTREAM_SYNC.md) for common solutions
2. Run with `--dry-run` to preview changes
3. Review the script output for specific error messages
4. Check that all Web3 files are intact after sync

---

**Upstream Repository:** https://github.com/oraios/serena  
**Upstream Documentation:** https://oraios.github.io/serena/
