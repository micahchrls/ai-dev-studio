#!/usr/bin/env bash
# Regression tests for git_guard.py. Run: bash plugins/studio/hooks/test_git_guard.sh
set -u
H="$(cd "$(dirname "$0")" && pwd)/git_guard.py"
T=$(mktemp -d)
git -C "$T" init -q -b main
git -C "$T" -c user.name=t -c user.email=t@example.com commit -q --allow-empty -m init
git -C "$T" switch -q -c feature

run() {
  local json
  json=$(python3 -c 'import json,sys;print(json.dumps({"tool_name":"Bash","cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$1" "$T")
  printf '%s' "$json" | python3 -I "$H" 2>/dev/null
  echo $?
}
pass=0; fail=0
expect() {
  local got; got=$(run "$2")
  if [ "$got" = "$1" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: want exit $1, got $got: $2"; fi
}

# Allowed
for c in "git status" "git push origin feature" "git push -u origin feature" "git checkout -b new-thing" \
  "git restore --staged a.txt" "git restore -S a.txt" "git branch -d merged" "git log --oneline" \
  "git reset --soft HEAD~1" "git clean -n" "npm test && git commit -m wip" "echo git push --force" \
  "grep -r 'reset --hard' docs"; do expect 0 "$c"; done

# Blocked
for c in "git push --force" "git push -f origin feature" "git -C $T push --force-with-lease" \
  "git push origin +feature" "git push origin main" "git push origin HEAD:main" "cd x && git reset --hard" \
  "git clean -fd" "git branch -D old" "git checkout -- ." "git checkout ." "git restore src/a.ts" \
  "git stash clear" "git filter-branch --all" "GIT_TRACE=1 git push --force" "sudo git reset --hard" \
  "true; /usr/bin/git clean -xfd"; do expect 2 "$c"; done

# Bare push depends on the current branch
expect 0 "git push"
git -C "$T" switch -q main
expect 2 "git push"

rm -rf "$T"
echo "pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
