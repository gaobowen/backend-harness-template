# Git Workflow

## Before Git Writes

Run:

```bash
git branch --show-current
git status --short --branch
```

Preserve unrelated work. Stop and align when working-tree ownership or overlapping changes are unclear.

## Branches And Worktrees

- Use one focused branch per task.
- Prefer an isolated worktree for parallel Agent tasks.
- Use a consistent branch prefix selected by the adopting team.
- Do not create, remove, switch, fetch, pull, merge, rebase, commit, push, or open a pull request or merge request unless the task authorizes it.

## Verification Before Handoff

Run `make preflight`. Also run database migrations and affected integration tests for API, database, Redis, or worker changes. Run `make security-audit` for dependency changes.

## Commit And Review

- Stage explicit files; avoid broad staging in a mixed working tree.
- Keep a commit focused on one behavior or infrastructure goal.
- Include success criteria, risk, migration impact, verification evidence, and skipped checks in the PR or MR.
- Do not auto-merge by default.
- Never force-push or rewrite shared history without explicit approval.

## Builder And Checker

For assisted Loop changes, the Builder creates a patch in an isolated worktree. A separate Checker context reviews the diff, API and data impact, and reruns the relevant gates before a draft PR or MR is proposed.
