# studio (Claude Code plugin)

The shared workflow of the AI dev studio, installable in any Claude Code setup.

## What it adds

| Piece | What it does |
|---|---|
| `/studio:new-project` | Scaffolds an app from the official Laravel, Next.js or Expo starter, then applies the studio overlay (agent rules in `CLAUDE.md`, `.env` deny rules, PR template, Dependabot, CI), creates a vault note and hands off to discovery. Never overwrites starter files. |
| `/studio:grill-with-docs` | Interviews you about an idea until the design is clear, writing `GLOSSARY.md` terms and ADRs as decisions land. |
| `/studio:to-spec`, `/studio:to-tickets` | Turn the discussion into a spec issue, then into tracer-bullet vertical-slice tickets with blocking links on GitHub Issues. |
| `/studio:setup-matt-pocock-skills` | One-time per-repo setup: issue tracker and domain-doc layout for the planning skills. |
| Git guard hook | Blocks force-pushes, pushes to `main`/`master`, `reset --hard`, `clean -f`, `branch -D`, path checkouts/restores, `stash clear` and history rewrites, including wrapped forms like `git -C dir push --force`. Tests: `bash hooks/test_git_guard.sh`. |

The planning skills are vendored from [mattpocock/skills](https://github.com/mattpocock/skills) under MIT; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The build loop (plans, TDD, verification) comes from the separate [superpowers](https://github.com/obra/superpowers) plugin.

## Install

```bash
claude plugin marketplace add <owner>/ai-dev-studio
claude plugin install studio@ai-dev-studio
```

Requirements: `python3` (hook), `jq` (overlay script), `gh` (GitHub Issues), plus the starter's own tools (`laravel`/`composer` or `node`/`npm`).
