#!/usr/bin/env python3
"""Studio git guard: a Claude Code PreToolUse hook for the Bash tool.

Blocks git commands that destroy work or rewrite shared history, plus any push to
main/master. Exit code 2 blocks the tool call and shows stderr to Claude; exit 0 lets
the normal permission flow continue (this hook never auto-approves anything).

This is the second safety layer. The first is the deny/ask rules in
~/.claude/settings.json, which only match literal command prefixes; this hook also
catches variants such as `git -C dir push --force`, `cd x && git reset --hard`,
`bash -c '...'`, `eval ...`, `$(...)` and heredocs fed to a shell.

Parsing rules:
- Commands are split on unquoted ; & | ( ) newlines, $( and backticks. Text inside
  quotes is data, so `git commit -m "wip; git clean -fd"` is one git commit.
- `$(...)` and backticks inside double quotes still run, so their contents are checked.
- Heredoc bodies are data (`cat > f <<EOF`) unless the heredoc feeds a shell
  (`bash <<EOF`), in which case the body is checked as commands.
- `bash|sh|zsh -c '<script>'` and `eval <args>` are checked recursively.

Compatible with the macOS system Python (3.9). Standard library only.
Tests: python3 test_git_guard.py (cases in test_cases.json, shared with the studio map page).
"""
import json
import re
import subprocess
import sys

PROTECTED_BRANCHES = {"main", "master"}
# Global git options that consume the following token as their value.
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
WRAPPERS = {"command", "sudo", "env", "time", "nohup", "exec", "xargs"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
SEPARATORS = set(";&|()\n`")
HEREDOC = re.compile(r"(?<!<)<<(?!<)(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
MAX_DEPTH = 4


def segments(cmd):
    """Split a shell command into simple commands, each a list of tokens (quote-aware)."""
    segs, cur = [], []
    tok, has, q = "", False, None
    i, n = 0, len(cmd)

    def end_token():
        nonlocal tok, has
        if tok or has:
            cur.append(tok)
        tok, has = "", False

    def end_segment():
        nonlocal cur
        end_token()
        if cur:
            segs.append(cur)
        cur = []

    while i < n:
        c = cmd[i]
        if q == "'":
            if c == "'":
                q = None
            else:
                tok += c
        elif q == '"':
            if c == '"':
                q = None
            elif c == "\\" and i + 1 < n:
                i += 1
                tok += cmd[i]
            elif c == "$" and cmd[i + 1:i + 2] == "(":
                j, depth = i + 2, 1
                while j < n and depth:
                    if cmd[j] == "(":
                        depth += 1
                    elif cmd[j] == ")":
                        depth -= 1
                    j += 1
                segs.extend(segments(cmd[i + 2:j - 1]))
                i = j
                continue
            elif c == "`":
                j = cmd.find("`", i + 1)
                j = n if j < 0 else j
                segs.extend(segments(cmd[i + 1:j]))
                i = j + 1
                continue
            else:
                tok += c
        elif c in "'\"":
            q, has = c, True
        elif c == "\\" and i + 1 < n:
            i += 1
            if cmd[i] != "\n":
                tok += cmd[i]
        elif c == "$" and cmd[i + 1:i + 2] == "(":
            end_segment()
            i += 2
            continue
        elif c in SEPARATORS:
            end_segment()
        elif c.isspace():
            end_token()
        else:
            tok += c
        i += 1
    end_segment()
    return segs


def command_index(tokens):
    """Index of the token that is actually executed (skips VAR=x and wrappers)."""
    for i, tok in enumerate(tokens):
        if "=" in tok and not tok.startswith("-"):
            continue
        if tok in WRAPPERS:
            continue
        return i
    return None


def strip_heredocs(command):
    """Drop heredoc bodies that are plain data; keep bodies that feed a shell."""
    lines = command.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        m = HEREDOC.search(line)
        if not m:
            continue
        consumer = ""
        before = segments(line[:m.start()])
        if before:
            k = command_index(before[-1])
            if k is not None:
                consumer = before[-1][k].rsplit("/", 1)[-1]
        delim, dash = m.group(3), m.group(1) == "-"
        body = []
        while i < len(lines):
            end = lines[i].lstrip("\t") if dash else lines[i]
            i += 1
            if end == delim:
                break
            body.append(lines[i - 1])
        if consumer in SHELLS:
            out.extend(body)
    return "\n".join(out)


def git_invocations(command, depth=0):
    """Yield (git_dir, subcommand, args) for every git call in a shell command."""
    if depth > MAX_DEPTH:
        return
    for tokens in segments(strip_heredocs(command)):
        i = command_index(tokens)
        if i is None:
            continue
        word, rest = tokens[i].rsplit("/", 1)[-1], tokens[i + 1:]
        if word in SHELLS and "-c" in rest:
            k = rest.index("-c")
            if k + 1 < len(rest):
                for inv in git_invocations(rest[k + 1], depth + 1):
                    yield inv
            continue
        if word == "eval":
            for inv in git_invocations(" ".join(rest), depth + 1):
                yield inv
            continue
        if word != "git":
            continue
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


def check_push(args, branch_of):
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
        branch = branch_of()
        if branch in PROTECTED_BRANCHES:
            return "push while on protected branch '%s'" % branch
    return None


def check(sub, args, branch_of):
    flags = short_flags(args)
    if sub == "push":
        return check_push(args, branch_of)
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
        reason = check(sub, args, lambda: current_branch(cwd, git_dir))
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
