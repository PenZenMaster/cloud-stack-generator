# Git Hooks

This directory contains git hook templates for the Cloud Stack Generator project.

## Available Hooks

### pre-commit

Runs automated checks before allowing commits:

**Cloud Infrastructure Tests (Fast)**
- AWS Credentials tests
- S3 Manager tests
- OAC Methods tests
- GCS Provider tests (NEW in v3.4.0)

**Coverage Requirements**
- Measures coverage for `src.core.aws` and `src.core.deployment.providers`
- Requires minimum 69% coverage
- Current coverage: ~69.30%

**Code Quality Checks**
- Ruff linting (if available)
- TODO comment detection
- Debug statement detection (print, pdb, breakpoint)
- Hardcoded secrets detection

## Installation

### Windows (Git Bash/Cygwin)

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Linux/macOS

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Verification

Test the hook manually:

```bash
bash .git/hooks/pre-commit
```

## Bypassing the Hook

If you need to commit without running the hook (not recommended):

```bash
git commit --no-verify -m "your message"
```

## Updating the Hook

1. Edit `hooks/pre-commit` (this trackable template)
2. Copy to `.git/hooks/`: `cp hooks/pre-commit .git/hooks/pre-commit`
3. Commit the updated template

## Hook Details

### Coverage Breakdown (v3.4.0)

| Component | Coverage | Statements | Missed |
|-----------|----------|------------|--------|
| Abstract Provider | 82% | 128 | 23 |
| GCS Provider | 76% | 199 | 47 |
| Provider Factory | 72% | 82 | 23 |
| AWS Credentials | 69% | 248 | 77 |
| S3 Manager | 62% | 448 | 170 |
| **Total** | **69.30%** | **1,114** | **342** |

### Test Suite

- **111 tests** total
- **98 passing** (88% pass rate)
- Runs in ~10-15 seconds

## Troubleshooting

**Hook fails on every commit**
- Check Python and pytest are installed
- Run `pip install -r requirements.txt`
- Verify tests pass manually: `pytest tests/unit/test_aws_credentials.py -v`

**Coverage fails**
- Check which files are causing coverage drop
- Add tests to improve coverage
- Or adjust threshold in hook (not recommended)

**Permission denied**
- Ensure hook is executable: `chmod +x .git/hooks/pre-commit`

## Contributing

When adding new cloud providers:
1. Add provider tests to the hook (line 42)
2. Add coverage path to coverage check (line 49)
3. Update this README with new coverage stats
