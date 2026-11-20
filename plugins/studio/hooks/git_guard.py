#!/usr/bin/env python3
"""Studio git guard: a Claude Code PreToolUse hook for the Bash tool.

Blocks git commands that destroy work or rewrite shared history, plus any push to
main/master. Exit code 2 blocks the tool call and shows stderr to Claude; exit 0 lets
the normal permission flow continue (this hook never auto-approves anything).

This is the second safety layer. The first is the deny/ask rules in
~/.claude/settings.json, which only match literal command prefixes; this hook also
catches variants such as `git -C dir push --force` or `cd x && git reset --hard`.

Compatible with the macOS system Python (3.9). Standard library only.
"""
import json
import re
import shlex
import subprocess
import sys

PROTECTED_BRANCHES = {"main", "master"}
# Global git options that consume the following token as their value.
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n|\$\(|`|\(|\)")


def tokenize(segment):
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


WRAPPERS = {"command", "sudo", "env", "time", "nohup", "exec", "xargs"}


def command_index(tokens):
    """Index of the token that is actually executed (skips VAR=x and wrappers)."""
    for i, tok in enumerate(tokens):
        if "=" in tok and not tok.startswith("-"):
            continue
        if tok in WRAPPERS:
            continue
        return i
    return None


def git_invocations(command):
    """Yield (git_dir, subcommand, args) for every git call in a shell command."""
    for segment in SEGMENT_SPLIT.split(command):
        tokens = tokenize(segment)
        i = command_index(tokens)
        if i is not None and tokens[i].rsplit("/", 1)[-1] == "git":
            j, git_dir = i + 1, None
            while j < len(tokens) and tokens[j].startswith("-"):
                opt = tokens[j]
                if opt in GIT_OPTS_WITH_VALUE and j + 1 < len(tokens):
                    if opt == "-C":
                        git_dir = tokens[j + 1]
                    j += 2
                else:
                    j += 1
            if j < len(tokens):
                yield git_dir, tokens[j], tokens[j + 1:]


def short_flags(args):
    """Letters from combined short flags, e.g. ['-uf'] -> {'u', 'f'}."""
    letters = set()
    for a in args:
        if a.startswith("-") and not a.startswith("--"):
            letters.update(a[1:])
    return letters


def current_branch(cwd, git_dir):
    target = git_dir or cwd or "."
    try:
        out = subprocess.run(
            ["git", "-C", target, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def check_push(args, cwd, git_dir):
    flags = short_flags(args)
    for a in args:
        if a.startswith("--force") or a in ("--mirror", "--delete", "--prune"):
            return "force/destructive push (%s)" % a
    if "f" in flags or "d" in flags:
        return "force/delete push (short flag)"
    positional = [a for a in args if not a.startswith("-")]
    refspecs = positional[1:]  # first positional is the remote
    for ref in refspecs:
        if ref.startswith("+") or ref.startswith(":"):
            return "force or delete refspec (%s)" % ref
        dest = ref.split(":")[-1].replace("refs/heads/", "")
        if dest in PROTECTED_BRANCHES:
            return "push to protected branch '%s'" % dest
    if not refspecs:
        branch = current_branch(cwd, git_dir)
        if branch in PROTECTED_BRANCHES:
            return "push while on protected branch '%s'" % branch
    return None


def check(sub, args, cwd, git_dir):
    flags = short_flags(args)
    if sub == "push":
        return check_push(args, cwd, git_dir)
    if sub == "reset" and "--hard" in args:
        return "git reset --hard discards uncommitted work"
    if sub == "clean" and ("f" in flags or "--force" in args):
        return "git clean -f deletes untracked files"
    if sub == "branch" and ("D" in flags or ("--delete" in args and "--force" in args)):
        return "git branch -D force-deletes an unmerged branch"
    if sub == "checkout" and ("." in args or "--" in args or "f" in flags or "--force" in args):
        return "git checkout of paths discards local changes"
    staged_only = ("--staged" in args or "S" in flags) and "--worktree" not in args and "W" not in flags
    if sub == "restore" and not staged_only:
        return "git restore discards working-tree changes"
    if sub == "stash" and args[:1] and args[0] in ("drop", "clear"):
        return "git stash %s deletes stashed work" % args[0]
    if sub in ("filter-branch", "filter-repo"):
        return "history rewrite (%s)" % sub
    if sub == "reflog" and args[:1] == ["expire"]:
        return "git reflog expire removes recovery points"
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    if "git" not in command:
        return 0
    cwd = data.get("cwd")
    for git_dir, sub, args in git_invocations(command):
        reason = check(sub, args, cwd, git_dir)
        if reason:
            sys.stderr.write(
                "Blocked by studio git guard: %s.\n"
                "If this is really intended, stop and ask the user to run it themselves "
                "in their own terminal. Do not retry it in another form.\n" % reason
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
