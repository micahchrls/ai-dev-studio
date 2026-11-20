
## Studio workflow

- Work happens on a branch per ticket (`<issue-number>-<slug>`), never directly on `main`. Open a PR; CI must be green before merge.
- Tickets live in GitHub Issues. Specs: `/studio:to-spec`; tickets: `/studio:to-tickets`.
- One failing test first, then the smallest change that passes it. If a test looks wrong, stop and tell the user instead of editing it to pass.
- Run the test, type-check and lint commands above before saying a task is done.
- Code-level decisions go in `docs/adr/` (format from `/studio:domain-modeling`); domain terms go in `GLOSSARY.md`.
- Gotchas Claude hits twice get a line here. Keep this file under 200 lines; never describe architecture Claude can read from the code.

## Gotchas

- (none yet)
