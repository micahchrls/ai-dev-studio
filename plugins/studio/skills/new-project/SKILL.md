---
name: new-project
description: Scaffold a new studio project from an official starter (Laravel, Next.js or Expo), apply the studio overlay, create its vault note and hand off to discovery. Use when the user wants to start a new app.
disable-model-invocation: true
---

# New studio project

Scaffold one app under the studio's `projects/` folder using the official starter for its stack, then layer the studio workflow on top. Do not invent a custom generator: the starters own the app code, this skill only orchestrates.

Studio root: `$STUDIO_HOME` if set, otherwise `~/ai-dev-studio`. Projects go in `<studio root>/projects/<name>/`; the vault is `<studio root>/vault/`.

## 1. Ask (one question at a time, recommended answer first)

1. **Name**: kebab-case, becomes the folder and repo name.
2. **Stack**: `laravel` (default: Laravel + Inertia + React/TS + Pest + PostgreSQL + Boost), `nextjs` (the TypeScript flagship) or `expo` (mobile client, usually of a Laravel API).
3. **Purpose**: one sentence, from the user's point of view.

If the user passed these as arguments ($ARGUMENTS), skip the questions you already have answers to.

## 2. Check prerequisites

Run these and stop with a clear message if one fails:

- `<studio root>/projects/<name>` must not exist.
- `gh auth status` (needed for GitHub Issues later; if not signed in, tell the user to run `gh auth login` themselves and continue).
- Stack tools: `laravel --version` and `composer --version` (laravel); `node --version` and `npm --version` (nextjs, expo).
- **laravel only: PostgreSQL.** Check that a server is reachable (`pg_isready`, or a running Docker container). If none is, ask the user: start one (for example `docker run -d --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17`, or Laravel Herd/DBngin), or scaffold with `--database=sqlite` now and switch later. Tests use SQLite in memory either way, so CI doesn't need Postgres.

## 3. Run the official starter

Starter flags drift between versions. Before running, check the current flags with `--help` and adjust if any flag below no longer exists.

- **laravel**: `laravel new <name> --react --pest --database=pgsql --boost --npm --git --no-interaction` (run inside `projects/`).
- **nextjs**: `npx create-next-app@latest <name> --ts --eslint --tailwind --app --src-dir --use-npm --yes`.
- **expo**: `npx create-expo-app@latest <name>`.

## 4. Apply the studio overlay

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/apply-overlay.sh" <stack> "<studio root>/projects/<name>" "<name>" "<purpose>"
```

It never overwrites: it appends the studio sections to an existing `CLAUDE.md`, merges `.env` deny rules into `.claude/settings.json`, and adds the PR template, Dependabot config and CI workflow only where missing. Show the user its output.

Then trim `CLAUDE.md`: if the starter generated long guidelines (Laravel Boost does), keep them but make sure the file stays readable and under about 200 lines of project-specific content.

## 5. Git

- If the starter did not initialise git, run `git init -b main`.
- Make one local commit: `chore: scaffold <name> from <starter> with studio overlay`.
- **Ask before publishing.** Creating the GitHub repo is the user's call: offer `gh repo create <name> --public --source . --remote origin` and only run it on an explicit yes. Right after it is created, add the label the planning skills apply: `gh label create ready-for-agent --description "Spec or ticket ready for an agent" --color 0E8A16`. Pushing `main` is the user's action (the studio git guard blocks pushes to `main`), so give them the exact command instead: `git push -u origin main`.

## 6. Vault note

Create `<studio root>/vault/<Name>.md` from `vault/Templates/Project.md`: fill `status: active`, `start` (today, YYYY-MM-DD), `stack`, `repo` (the GitHub URL, if created) and the Goal from the purpose. Append a line to today's daily log (`vault/Daily/YYYY-MM-DD.md`, created from `Templates/Daily log.md` if missing): `Started [[<Name>]] (<stack>).`

## 7. Hand off to discovery

Tell the user what was created (folder, overlay output, vault note, repo URL or the command to create it) and the next two steps, in order:

1. Open a new Claude Code session in the project folder and run `/studio:setup-matt-pocock-skills` (choose GitHub Issues).
2. Run `/studio:grill-with-docs` to interview the idea into a shared design, then `/studio:to-spec` and `/studio:to-tickets`.

A new session matters: it loads the project's own `CLAUDE.md`, `.claude/settings.json` and Boost/Expo tooling, which this session cannot see.
