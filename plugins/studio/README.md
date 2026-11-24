# studio (Claude Code plugin)

The shared workflow of the AI dev studio, installable in any Claude Code setup.

## What it adds

| Piece | What it does |
|---|---|
| `/studio:new-project` | Scaffolds an app from the official Laravel, Next.js or Expo starter, then applies the studio overlay (agent rules in `CLAUDE.md`, `.env` deny rules, PR template, Dependabot, CI), creates a vault note and hands off to discovery. Never overwrites starter files. |
| `/studio:grill-with-docs` | Interviews you about an idea until the design is clear, writing `GLOSSARY.md` terms and ADRs as decisions land. |
| `/studio:to-spec`, `/studio:to-tickets` | Turn the discussion into a spec issue, then into tracer-bullet vertical-slice tickets with blocking links on GitHub Issues. |
| `/studio:setup-matt-pocock-skills` | One-time per-repo setup: issue tracker and domain-doc layout for the planning skills. |
| `studio-researcher` agent | Researches how the studio's own workflow could improve and writes a cited Research note to the vault. The note gives, per SDLC phase, the manager's approval gate and the agents' work, then ranked proposals. It proposes only: decisions become ADRs in your own session. Claude is told to delegate to it only when you ask ("use the studio-researcher agent to research …"). Sonnet, read and web tools plus `Write` (and `Bash` only to list files when Glob/Grep are missing), 60-turn cap. |
| Git guard hook | Blocks force-pushes, pushes to `main`/`master`, `reset --hard`, `clean -f`, `branch -D`, path checkouts/restores, `stash clear` and history rewrites, including wrapped forms like `git -C dir push --force`, `bash -c '…'`, `eval` and heredocs fed to a shell. Quoted text and heredoc data are ignored. Tests: `python3 hooks/test_git_guard.py` (cases in `hooks/test_cases.json`). |

The planning skills are vendored from [mattpocock/skills](https://github.com/mattpocock/skills) under MIT; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The build loop (plans, TDD, verification) comes from the separate [superpowers](https://github.com/obra/superpowers) plugin.

## Install

```bash
claude plugin marketplace add micahchrls/ai-dev-studio
claude plugin install studio@ai-dev-studio
```

Requirements: `python3` (hook), `jq` (overlay script), `gh` (GitHub Issues), plus the starter's own tools (`laravel`/`composer` or `node`/`npm`).
