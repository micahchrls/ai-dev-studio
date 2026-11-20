#!/usr/bin/env bash
# Apply the studio overlay to a freshly scaffolded project. Never overwrites existing files:
# CLAUDE.md gets a section appended, .claude/settings.json deny rules are merged, everything
# else is copied only if missing. Safe to re-run.
#
# Usage: apply-overlay.sh <laravel|nextjs|expo> <project-dir> <project-name> "<one-line purpose>"
set -euo pipefail

STACK=${1:?stack required: laravel|nextjs|expo}
DIR=${2:?project directory required}
NAME=${3:?project name required}
PURPOSE=${4:-"TODO: one-line purpose."}

TEMPLATES="$(cd "$(dirname "$0")/../../.." && pwd)/templates"
case "$STACK" in laravel|nextjs|expo) ;; *) echo "Unknown stack: $STACK" >&2; exit 1 ;; esac
[ -d "$DIR" ] || { echo "Project directory not found: $DIR" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

esc() { printf '%s' "$1" | sed -e 's/[|&\\]/\\&/g'; }
render() {
  sed -e "s|{{NAME}}|$(esc "$NAME")|g" -e "s|{{STACK}}|$(esc "$STACK")|g" \
      -e "s|{{PURPOSE}}|$(esc "$PURPOSE")|g" "$1"
}
note() { printf '  %-34s %s\n' "$1" "$2"; }

echo "Applying studio overlay ($STACK) to $DIR"

# 1. CLAUDE.md: create, or append the studio sections once.
CLAUDE_MD="$DIR/CLAUDE.md"
if [ ! -f "$CLAUDE_MD" ]; then
  { render "$TEMPLATES/common/claude-header.md"; cat "$TEMPLATES/$STACK/commands.md"; render "$TEMPLATES/common/studio-section.md"; } > "$CLAUDE_MD"
  note "CLAUDE.md" "created"
elif ! grep -q "^## Studio workflow" "$CLAUDE_MD"; then
  { printf '\n'; cat "$TEMPLATES/$STACK/commands.md"; render "$TEMPLATES/common/studio-section.md"; } >> "$CLAUDE_MD"
  note "CLAUDE.md" "existing file: studio sections appended"
else
  note "CLAUDE.md" "already has studio sections, skipped"
fi

# 2. .claude/settings.json: merge deny rules into whatever the starter shipped.
SETTINGS="$DIR/.claude/settings.json"
mkdir -p "$DIR/.claude"
if [ -f "$SETTINGS" ]; then
  tmp=$(mktemp)
  jq -s '(.[0].permissions.deny // []) as $a | (.[1].permissions.deny // []) as $b
         | (.[0] * .[1]) | .permissions.deny = ($a + $b | unique)' \
     "$SETTINGS" "$TEMPLATES/common/.claude/settings.json" > "$tmp" && mv "$tmp" "$SETTINGS"
  note ".claude/settings.json" "merged deny rules"
else
  cp "$TEMPLATES/common/.claude/settings.json" "$SETTINGS"
  note ".claude/settings.json" "created"
fi

# 3. GitHub files: PR template, Dependabot, CI (CI only if the starter shipped no workflows).
copy_if_missing() {
  local src=$1 dest=$2
  if [ -e "$dest" ]; then note "${dest#"$DIR"/}" "exists, kept"; else
    mkdir -p "$(dirname "$dest")"; cp "$src" "$dest"; note "${dest#"$DIR"/}" "created"; fi
}
copy_if_missing "$TEMPLATES/common/.github/pull_request_template.md" "$DIR/.github/pull_request_template.md"
copy_if_missing "$TEMPLATES/$STACK/.github/dependabot.yml" "$DIR/.github/dependabot.yml"
if ls "$DIR"/.github/workflows/*.yml >/dev/null 2>&1; then
  note ".github/workflows/ci.yml" "starter already ships workflows, kept theirs"
else
  copy_if_missing "$TEMPLATES/$STACK/.github/workflows/ci.yml" "$DIR/.github/workflows/ci.yml"
fi

# 4. .gitignore: keep personal Claude files out of the repo.
touch "$DIR/.gitignore"
for line in ".claude/settings.local.json" "CLAUDE.local.md"; do
  grep -qxF "$line" "$DIR/.gitignore" || { printf '%s\n' "$line" >> "$DIR/.gitignore"; note ".gitignore" "added $line"; }
done

echo "Overlay applied."
