# AI dev studio

A one-person software studio run with [Claude Code](https://code.claude.com). This repo is the studio's operating system: one shared workflow that every project inherits, a one-command way to start a new app, and the guardrails that keep AI-assisted work safe and reviewable.

It is built on a simple belief backed by current research: **AI speeds up delivery only when the checks are strong.** DORA's 2025 report found AI raises throughput but hurts stability unless testing and version control are solid, so this setup invests in tests, CI, review and safety rails rather than in prompt tricks.

## What a reviewer should look at

| Look at | What it shows |
|---|---|
| [`docs/sdlc-checklist.md`](docs/sdlc-checklist.md) | The lifecycle every project follows, from idea to retrospective, with the human's and the AI's role in each phase |
| [`plugins/studio/`](plugins/studio) | A Claude Code plugin: skills, a git safety hook and project templates, installable by anyone |
| [`plugins/studio/hooks/git_guard.py`](plugins/studio/hooks/git_guard.py) | A PreToolUse hook that blocks force-pushes, pushes to `main`, `reset --hard` and other destructive git commands, with [regression tests](plugins/studio/hooks/test_git_guard.sh) |
| [`plugins/studio/skills/new-project/`](plugins/studio/skills/new-project) | `/studio:new-project`: scaffolds from the official Laravel, Next.js or Expo starter, then layers on CI, Dependabot, a PR template and agent rules |
| [`CLAUDE.md`](CLAUDE.md) | Studio-wide instructions every project session inherits, kept short on purpose |
| The project repos | Each app shows the workflow in practice: spec and tickets as GitHub Issues, ADRs in `docs/adr/`, small PRs with review notes, green CI |

## How it works

```
~/ai-dev-studio/            (this repo, public)
├── CLAUDE.md               inherited by every session under projects/
├── plugins/studio/         shared workflow, installed once for the user
├── docs/                   SDLC checklist
├── settings/               sanitized copy of the user-level Claude Code settings
├── projects/<app>/         each app is its own repo (not tracked here)
└── vault/                  private Obsidian second brain (not tracked here)
```

Claude Code only passes a parent folder's `CLAUDE.md` down into a project that is its own git repo; settings, skills and hooks stop at the repo boundary. So the shared workflow ships as a **plugin** (skills, hooks, templates) plus **user-level settings** (permission rules and model choice, which plugins can't carry).

### The workflow, by size of work

| Size | Process |
|---|---|
| Spike | Throwaway branch |
| Small change | Issue with acceptance criteria → plan mode → failing test → code → review → PR |
| Feature | Interview (`/studio:grill-with-docs`) → spec (`/studio:to-spec`) → vertical-slice tickets (`/studio:to-tickets`) → per ticket: plan, TDD, review, PR |

The build loop uses the [superpowers](https://github.com/obra/superpowers) plugin (planning, TDD, verification before claiming done). Planning uses five skills vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, see [notices](plugins/studio/THIRD_PARTY_NOTICES.md)).

### Safety rails

- **Deny rules** in user settings block force-pushes, `reset --hard`, `clean -f` and `branch -D`, and every other push needs approval.
- **The git guard hook** catches the variants that prefix rules miss (`git -C dir push --force`, `cd x && git reset --hard`) and blocks any push to `main`.
- **Per-project deny rules** stop the agent reading or editing `.env` files.
- **A pre-commit hook** in this repo refuses to commit the private vault or project repos.
- **Tests are the contract:** the agent is told to report a wrong-looking test, never edit it to pass.

### Default stacks

- **Web:** Laravel 13 + Inertia + React/TypeScript (strict) + PostgreSQL + Pest, with Laravel Boost for agent tooling.
- **TypeScript flagship:** Next.js 16.
- **Mobile:** Expo, as a client of a Laravel API.

Each choice is recorded with its research and trade-offs as an architecture decision record.

## Use it yourself

```bash
claude plugin marketplace add <owner>/ai-dev-studio
claude plugin install studio@ai-dev-studio
```

Then, in Claude Code: `/studio:new-project`. Copy the permission rules you want from [`settings/settings.example.json`](settings/settings.example.json) into your own `~/.claude/settings.json`.

## Status

Set up November 2026. Projects built with this workflow will be linked here as they ship.
