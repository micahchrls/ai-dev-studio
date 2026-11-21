#!/usr/bin/env python3
"""Regression tests for git_guard.py. Run: python3 plugins/studio/hooks/test_git_guard.py

Runs the real hook as Claude Code would (JSON on stdin, exit code 2 = blocked) against
every case in test_cases.json, inside a throwaway git repo on the case's branch.
The same cases drive the JavaScript port on the studio map page.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "git_guard.py")


def git(repo, *args):
    subprocess.run(["git", "-C", repo] + list(args), check=True, capture_output=True)


def main():
    cases = json.load(open(os.path.join(HERE, "test_cases.json")))["cases"]
    failures = 0
    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "init")
        git(repo, "branch", "feature")
        for case in cases:
            git(repo, "switch", "-q", case.get("branch", "feature"))
            payload = json.dumps({"tool_name": "Bash", "cwd": repo, "tool_input": {"command": case["cmd"]}})
            proc = subprocess.run([sys.executable, "-I", HOOK], input=payload, capture_output=True, text=True)
            got = "block" if proc.returncode == 2 else "allow"
            if got != case["expect"]:
                failures += 1
                print("FAIL: want %s, got %s: %r" % (case["expect"], got, case["cmd"]))
    print("pass=%d fail=%d" % (len(cases) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
