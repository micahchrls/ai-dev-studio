# Third-party notices

## mattpocock/skills (MIT)

These skills are vendored (copied and pinned) from
[github.com/mattpocock/skills](https://github.com/mattpocock/skills) at commit `abeeaf9` (2026-11-19):

| Skill | Upstream path |
|---|---|
| `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills` |
| `grill-with-docs` | `skills/engineering/grill-with-docs` |
| `grilling` | `skills/productivity/grilling` |
| `domain-modeling` | `skills/engineering/domain-modeling` |
| `to-spec` | `skills/engineering/to-spec` |
| `to-tickets` | `skills/engineering/to-tickets` |

Changes from upstream:

- Removed the `agents/openai.yaml` files (Codex-specific).
- `grill-with-docs/SKILL.md`: skill references renamed to the plugin namespace
  (`studio:grilling`, `studio:domain-modeling`).

Why vendored rather than installed from the upstream plugin: upstream renamed or deleted
more than a dozen skills during 2026, and the full plugin duplicates skills already covered by
the superpowers plugin. Pinning a copy keeps the workflow stable. To update, diff against a
newer upstream commit and copy deliberately.

The upstream license is reproduced in [`LICENSE-mattpocock-skills`](LICENSE-mattpocock-skills).
