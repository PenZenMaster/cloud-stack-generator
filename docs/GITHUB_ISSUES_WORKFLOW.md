# GitHub Issues Workflow Integration

**Version**: 1.0
**Created**: December 21, 2025
**Purpose**: Integrate GitHub Issues into daily development workflow for defect tracking and feature planning

---

## Overview

This document describes how GitHub Issues are integrated into the Cloud Stack Generator development workflow for tracking bugs, feature requests, test coverage gaps, and documentation improvements.

---

## Issue Templates

Four issue templates are available when creating a new issue:

### 1. Bug Report (`bug_report.yml`)
**Use for**: Reporting defects, errors, or unexpected behavior

**Key Fields**:
- Version affected
- Expected vs actual behavior
- Steps to reproduce
- Severity level (Critical/High/Medium/Low)
- Component affected
- Error logs/screenshots

**Labels**: `bug`, `triage`

### 2. Feature Request (`feature_request.yml`)
**Use for**: Proposing new features or enhancements

**Key Fields**:
- Problem statement
- Proposed solution
- Priority level
- Feature category
- Estimated complexity
- Dependencies/blockers
- Implementation considerations

**Labels**: `enhancement`, `triage`

### 3. Test Coverage Gap (`test_coverage.yml`)
**Use for**: Identifying missing or inadequate test coverage

**Key Fields**:
- Coverage gap type
- Module/component affected
- Test scenarios needed
- Test phase (Phase 1-4)
- Testing complexity

**Labels**: `testing`, `quality`

### 4. Documentation Improvement (`documentation.yml`)
**Use for**: Reporting documentation gaps, errors, or improvements

**Key Fields**:
- Documentation type
- Issue type (missing, incorrect, outdated)
- Document location
- Proposed improvement
- User impact

**Labels**: `documentation`

---

## Daily Workflow Integration

### When to Create Issues

#### During Development
- **Bug Discovered**: Create bug report immediately with reproduction steps
- **Test Failure**: Create test coverage issue if test reveals gap
- **Feature Idea**: Create feature request with problem statement
- **Documentation Gap**: Create documentation issue when unclear

#### During Code Review
- **Review Findings**: Create issues for bugs or improvements found
- **Technical Debt**: Create issues for refactoring needs
- **Missing Tests**: Create test coverage issues

#### During Testing/QA
- **Failed Test Case**: Create bug report with test details
- **Edge Case Found**: Create test coverage issue to document scenario
- **User Confusion**: Create documentation issue to improve guides

---

## Issue Management

### Labels

**Priority Labels**:
- `critical` - Immediate attention required
- `high` - Important, schedule soon
- `medium` - Normal priority
- `low` - Nice to have

**Type Labels**:
- `bug` - Defect or error
- `enhancement` - New feature or improvement
- `testing` - Test-related issue
- `documentation` - Documentation issue
- `technical-debt` - Refactoring or cleanup needed

**Status Labels**:
- `triage` - Needs review and prioritization
- `in-progress` - Currently being worked on
- `blocked` - Waiting on dependency
- `ready` - Ready to be implemented

**Component Labels**:
- `ui` - User interface components
- `core` - Core business logic
- `deployment` - Cloud deployment features
- `api` - API integrations
- `testing` - Test infrastructure

### Milestones

Link issues to version milestones:
- `v3.7.0` - Next minor release
- `v3.6.x` - Current release patches
- `v4.0.0` - Major version planning

---

## Issue Workflow States

```
┌─────────┐
│  Open   │ (Created, labeled as 'triage')
└────┬────┘
     │
     v
┌─────────┐
│ Triaged │ (Priority assigned, milestone set)
└────┬────┘
     │
     v
┌─────────┐
│  Ready  │ (Approved for implementation)
└────┬────┘
     │
     v
┌──────────────┐
│ In Progress  │ (Assigned, being worked on)
└──────┬───────┘
       │
       v
┌─────────────┐
│   Testing   │ (Implementation complete, needs QA)
└──────┬──────┘
       │
       v
┌─────────┐
│ Closed  │ (Resolved, verified, merged)
└─────────┘
```

---

## Creating Issues from Defects

### Example: Bug Found During Testing

```bash
# When you find a bug:
1. Note the exact steps to reproduce
2. Capture error logs or screenshots
3. Check if similar issue already exists
4. Create new bug report with template
5. Add appropriate labels and milestone
6. Reference in commit when fixed
```

### Linking Commits to Issues

When fixing an issue, reference it in the commit message:

```bash
git commit -m "fix: Correct Path mocking in test_deploy_client_website_not_found

Fixes #123

- Use MagicMock for __truediv__ support
- Explicitly configure exists() to return False
- Add S3WebsiteDeployer mock to prevent boto3 init

Test Coverage: 46/46 passing (100%)
"
```

**Keywords that close issues automatically**:
- `Fixes #123`
- `Closes #123`
- `Resolves #123`

---

## Search and Filter

### Common Queries

**All open bugs**: `is:issue is:open label:bug`

**Critical issues**: `is:issue is:open label:critical`

**Test coverage gaps**: `is:issue is:open label:testing`

**My assigned issues**: `is:issue is:open assignee:@me`

**Ready to implement**: `is:issue is:open label:ready`

**Blocked issues**: `is:issue is:open label:blocked`

---

## Integration with AWG Workflow

### AWG Checkpoint Command

When running `AWG checkpoint`, include open issues summary:

```markdown
## Open Issues
- Bug #45: Path mocking failure (In Progress)
- Feature #67: WYSIWYG Template Editor (Ready)
- Test #89: Products Tab Coverage (Triaged)
- Docs #90: Admin Guide Missing (Open)
```

### AWG Startup Command

At session start, review:
1. Issues assigned to you
2. Critical/high priority issues
3. Issues blocked on dependencies
4. Recently closed issues

---

## Best Practices

### DO:
- Create issues early when problems are found
- Provide detailed reproduction steps
- Add relevant labels and milestones
- Link related issues and PRs
- Close issues when verified fixed
- Update issue status as work progresses

### DON'T:
- Create duplicate issues (search first)
- Use vague titles or descriptions
- Leave issues open indefinitely
- Skip reproduction steps
- Forget to link commits
- Close issues without verification

---

## Example Workflow

### Scenario: Bug Discovered During Testing

1. **Discovery**:
   ```
   Test fails: test_deploy_client_website_not_found
   Error: Path mocking not preventing boto3 init
   ```

2. **Create Issue**:
   - Use Bug Report template
   - Title: "[BUG]: Path mocking failure in S3 deployer test"
   - Severity: High
   - Component: Core - S3 Deployer
   - Reproduction steps documented
   - Label: `bug`, `testing`, `triage`

3. **Triage**:
   - Review and add `high` priority
   - Assign to developer
   - Set milestone: `v3.6.1`
   - Move to `ready` status

4. **Implementation**:
   - Change status to `in-progress`
   - Create feature branch
   - Fix the issue
   - Write tests
   - Commit with "Fixes #X"

5. **Verification**:
   - Run full test suite
   - QA confirms fix
   - Merge to main
   - Issue auto-closes

6. **Documentation**:
   - Update CHANGELOG
   - Update test documentation
   - Add to checkpoint notes

---

## Automation

### GitHub Actions Integration

Future automation possibilities:
- Auto-label based on file paths
- Auto-assign based on component
- Stale issue detection
- Test coverage reporting on issues
- Automatic milestone progression

---

## Metrics & Reporting

### Track:
- Open issues by priority
- Average time to resolution
- Issues opened vs closed (velocity)
- Test coverage gaps identified
- Documentation improvements made

### Generate Reports:
```bash
# Open bugs by severity
gh issue list --label bug,critical

# Issues in current milestone
gh issue list --milestone v3.7.0

# Recently closed issues
gh issue list --state closed --limit 10
```

---

## Quick Reference

### Create Issue
```bash
# Via web: github.com/PenZenMaster/cloud-stack-generator/issues/new/choose
# Via CLI:
gh issue create --title "[BUG]: Issue title" --body "Description" --label bug
```

### List Issues
```bash
# All open issues
gh issue list

# Filter by label
gh issue list --label bug

# Search
gh issue list --search "Path mocking"
```

### Close Issue
```bash
gh issue close <issue-number> --comment "Fixed in commit abc123"
```

---

## Integration Checklist

- [x] Issue templates created
- [x] Labels defined
- [x] Workflow documented
- [ ] Team training on issue usage
- [ ] Automation setup (future)
- [ ] Metrics dashboard (future)

---

## See Also

- [GitHub Issues Documentation](https://docs.github.com/en/issues)
- [Linking Pull Requests to Issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [AWG Project Plan](./AWG-Project-Plan.md)
- [STARTUP_CONTEXT.md](./STARTUP_CONTEXT.md)

---

**Last Updated**: December 21, 2025
**Version**: 1.0
**Maintainer**: Development Team
