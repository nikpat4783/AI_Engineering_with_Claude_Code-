import subprocess
import json
import sys
from pathlib import Path


def run_hook(tool_name: str, tool_input: dict) -> tuple[str, int]:
    hook_path = Path(__file__).parent.parent / ".claude" / "hooks" / "allowlist_guard.py"
    payload = {
        "session_id": "test",
        "prompt_id": "test",
        "transcript_path": "/tmp/test.jsonl",
        "cwd": str(Path(__file__).parent),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "test"
    }
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload).encode(),
        capture_output=True
    )
    return result.stdout.decode(), result.returncode


def test_webfetch_denied():
    stdout, code = run_hook("WebFetch", {"url": "https://example.com"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert code == 0
    print("✓ test_webfetch_denied passed")


def test_websearch_denied():
    stdout, code = run_hook("WebSearch", {"query": "NX-14"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert code == 0
    print("✓ test_websearch_denied passed")


def test_bash_curl_denied():
    stdout, code = run_hook("Bash", {"command": "curl -s https://example.com"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert code == 0
    print("✓ test_bash_curl_denied passed")


def test_bash_wget_denied():
    stdout, code = run_hook("Bash", {"command": "wget https://example.com"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert code == 0
    print("✓ test_bash_wget_denied passed")


def test_bash_ls_allowed():
    stdout, code = run_hook("Bash", {"command": "ls -la /tmp"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert code == 0
    print("✓ test_bash_ls_allowed passed")


def test_bash_pytest_allowed():
    stdout, code = run_hook("Bash", {"command": "pytest -q tests/"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert code == 0
    print("✓ test_bash_pytest_allowed passed")


def test_bash_git_allowed():
    stdout, code = run_hook("Bash", {"command": "git status"})
    output = json.loads(stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert code == 0
    print("✓ test_bash_git_allowed passed")


if __name__ == "__main__":
    test_webfetch_denied()
    test_websearch_denied()
    test_bash_curl_denied()
    test_bash_wget_denied()
    test_bash_ls_allowed()
    test_bash_pytest_allowed()
    test_bash_git_allowed()
    print("\nAll hook contract tests passed!")
