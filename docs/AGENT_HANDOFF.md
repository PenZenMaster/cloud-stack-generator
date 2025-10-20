# Agent Coordination Log

> **Purpose**: Cross-tool communication between GitHub Copilot and Claude Code for seamless AI-assisted development workflow.

---

## How to Use This File

### For Claude Code
- **Before checkpoint**: Document completed work, decisions, and handoff tasks
- **At session start**: Read this file to understand Copilot's recent contributions
- **Format**: Use structured sections below with clear context and next actions

### For GitHub Copilot (via Developer)
- **After coding sessions**: Log what was implemented via Copilot autocomplete
- **Document patterns**: Note repeated patterns Copilot suggested that worked well
- **Flag issues**: Mark code that needs Claude's architectural review

---

## Active Handoffs

### [YYYY-MM-DD] - Agent → Agent
**Task**: [Brief task description]
**Status**: [In Progress / Needs Review / Blocked / Complete]
**Files**: [List of affected files]
**Context**: [Key decisions, patterns, or background]
**Next Steps**: [Specific actionable items for next agent]
**Blockers**: [Any blocking issues or decisions needed]

---

## Handoff History

### 2025-10-17 - Claude → Copilot (Template Example)
**Task**: Implement city page generator template variations
**Status**: Planning Complete
**Files**:
- `src/generators/city_page.py`
- `templates/city/*.html`
**Context**:
- Using Jinja2 template system
- Each city needs 800-1200 word content
- Schema markup required for SEO
- Follow pattern established in `templates/base.html`
**Next Steps**:
1. Use Copilot to autocomplete city template variants (beach, mountain, urban)
2. Follow established Jinja2 block structure
3. Maintain consistent CSS classes from `static/css/main.css`
**Blockers**: None

---

## Collaboration Patterns That Work

### Pattern: Architecture → Implementation
1. **Claude**: Design system architecture, write interfaces/base classes
2. **Copilot**: Autocomplete concrete implementations following the pattern
3. **Claude**: Review for type safety, test coverage, edge cases

### Pattern: Refactor → Optimize
1. **Copilot**: Generate initial working code
2. **Claude**: Refactor for maintainability, add error handling
3. **Copilot**: Apply refactored pattern across similar functions

### Pattern: Test → Code → Review
1. **Claude**: Write test cases (TDD approach)
2. **Copilot**: Implement code to pass tests
3. **Claude**: Verify quality gates, add edge case tests

---

## Code Comment Conventions

Use these structured comments for cross-agent communication:

```python
# AGENT(copilot): Implement retry logic here following exponential backoff pattern
# AGENT(claude): Review error handling - verify all exceptions caught
# DECISION: Using factory pattern for multi-provider support - see docs/architecture.md
# PATTERN: This function structure should be replicated for other content types
# REVIEW_NEEDED: Type hints incomplete, needs mypy verification
```

---

## Quick Reference

**Agent Strengths**:
- **Copilot**: Autocomplete, boilerplate, pattern repetition, inline suggestions
- **Claude Code**: Architecture, refactoring, debugging, testing, session planning, git workflow

**Coordination Triggers**:
- Use `AWG checkpoint` to document Claude's work for Copilot context
- Add entries here after significant Copilot-assisted coding sessions
- Reference this file during `AWG start` for session continuity

---

## Notes & Tips

- Keep handoff entries concise but contextual
- Link to relevant docs rather than duplicating information
- Archive completed handoffs monthly to `docs/archive/agent-handoffs/`
- Use git commit messages to cross-reference handoff entries
