# SDLC checklist (one page)

Use it for every project. Scale it to the work: a **spike** needs only phase 5; a **small change** needs phases 2, 5, 6, 7 and 9; a **feature** uses all of them.

| # | Phase | You (human) | Claude | Skill / tool | Done when this exists |
|---|---|---|---|---|---|
| 0 | **Start** | Name the app and its purpose | Scaffolds from the official starter + studio overlay | `/studio:new-project` | Repo, CI, vault project note |
| 1 | **Discovery** | Explain the problem; decide go / no-go | Interviews you, researches, spikes | `/studio:grill-with-docs`, plan mode | Vault Research note, `GLOSSARY.md` |
| 2 | **Spec** | Approve scope and non-goals | Synthesises the spec and test seams | `/studio:to-spec` | Spec issue with acceptance criteria |
| 3 | **Design** | Make the hard-to-reverse calls | Proposes options, drafts ADRs | `/studio:domain-modeling`, plan mode | `docs/adr/NNNN-*.md` |
| 4 | **Planning** | Check slice size and blocking order | Splits into tracer-bullet vertical slices | `/studio:to-tickets`, `gh issue` | One GitHub issue per slice |
| 5 | **Build** | Agree test seams; stop drift (`Esc`, `/clear`) | One failing test → pass → refactor; small commits | superpowers `writing-plans`, `executing-plans`, `test-driven-development` | Branch with tests, Conventional Commits |
| 6 | **Review** | Read every test diff and the auth/data paths | Fresh-context correctness review against the spec | `/code-review`, superpowers `requesting-code-review` | PR with findings resolved |
| 7 | **CI** | Keep CI fast; required checks on | Fixes red builds | GitHub Actions (studio CI template) | Green run |
| 8 | **Security** | Own secrets and risk calls | Runs a security review | `/security-review`, Dependabot, gitleaks (private repos) | No open high findings |
| 9 | **Release** | Approve merge and deploy; push `main` yourself | Writes release notes, verifies before claiming done | superpowers `verification-before-completion`, `finishing-a-development-branch` | Merged PR, tagged release |
| 10 | **Monitor** | Triage alerts | Investigates; fixes with a regression test | Sentry (free), UptimeRobot (free) | Alert → issue → fix PR |
| 11 | **Retro** (weekly, 15 min) | Decide one process change | Summarises merged PRs, incidents, repeated mistakes | Vault Lesson note | A CLAUDE.md line, a hook, or an ADR |

## Rules that never bend

- A test that looks wrong is reported, never edited to pass.
- Nothing is "done" until tests, type-check and lint have run and their output was read.
- A mistake Claude makes twice becomes a line in the project `CLAUDE.md`; a line it keeps ignoring becomes a hook.
- Measure, don't trust the feeling: note lead time and CI failures in the retro (developers misjudge AI speed-ups; METR 2025).
- Portfolio: when a project ships, write its case study from the vault Portfolio template.
