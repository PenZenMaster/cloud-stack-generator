# Deprecated Context Files

**Deprecated On**: 2025-11-27
**Reason**: Performance optimization - replaced with streamlined STARTUP_CONTEXT.md

---

## Why These Files Were Deprecated

### Problem

The old session handoff system used multiple redundant files:

- `SESSION_CONTEXT.md` (188 lines, 5.1KB)
- `HANDOFF_SUMMARY.md` (246 lines, 7.0KB)

**Issues:**
1. **Massive redundancy**: 70%+ overlap between files
2. **Stale data**: Files not always updated each session
3. **Slow startup**: Reading 3-4 files took ~40 minutes of session time
4. **Manual maintenance**: Required manual updates

### Solution

Replaced with single lightweight file:

- `docs/STARTUP_CONTEXT.md` (~40 lines, <3KB)

**Benefits:**
- ✅ 90% size reduction (434 lines → ~40 lines)
- ✅ Single source of truth
- ✅ Auto-updated on AWG shutdown
- ✅ 35-37 minute time savings per session (87-92% reduction)

---

## Migration

**Old Command**: `AWG start` (read SESSION_CONTEXT.md + HANDOFF_SUMMARY.md + checkpoint + projectStatus.md)

**New Command**: `AWG start` (read only STARTUP_CONTEXT.md)

**Backward Compatibility**:
- Old checkpoints remain in `docs/archive/checkpoints/` for historical reference
- `docs/projectStatus.md` still maintained for full project history
- These deprecated files preserved here for reference

---

## Restoration

If you need to restore the old system:

1. Copy these files back to `docs/`
2. Remove `.deprecated` extension
3. Update `.claude/CLAUDE.md` to use old AWG start/shutdown commands

**Not recommended** - the new system is significantly faster and more maintainable.

---

**Files in this directory:**
- `SESSION_CONTEXT.md.deprecated` - Last session context (Nov 21, 2025)
- `HANDOFF_SUMMARY.md.deprecated` - Last handoff summary (Nov 21, 2025)
