from __future__ import annotations

from typing import Any

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from greeble.scripts import dev


def _capture_git_calls(
    monkeypatch: MonkeyPatch, responses: dict[tuple[Any, ...], Any]
) -> list[tuple[tuple[Any, ...], bool]]:
    calls: list[tuple[tuple[Any, ...], bool]] = []

    def fake_git(args: list[str] | tuple[str, ...], *, capture_output: bool = False) -> Any:
        calls.append((tuple(args), capture_output))
        key = tuple(args)
        if capture_output:
            return responses.get(key, "")
        result = responses.get(key)
        if isinstance(result, Exception):
            raise result
        return ""

    monkeypatch.setattr(dev, "git", fake_git)
    return calls


def test_branch_create_success(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    responses = {
        ("rev-parse", "--abbrev-ref", "HEAD"): "release-candidate",
        ("checkout", "-B", "release-candidate", "origin/release-candidate"): "",
        ("checkout", "-B", "feat/test-branch", "release-candidate"): "",
    }

    calls = _capture_git_calls(monkeypatch, responses)
    monkeypatch.setattr(dev, "checkout_release_candidate_with_base", lambda: True)

    rc = dev.handle_branch_create(["feat/test-branch"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Created" in out
    # ensure push attempted
    assert any(cmd[0][0] == "push" for cmd in calls)


def test_branch_create_invalid_tag(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr(dev, "checkout_release_candidate_with_base", lambda: True)
    rc = dev.handle_branch_create(["unknown/foo"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "tag must be one of" in err


def test_branch_rebase_happy_path(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    responses = {
        ("rev-parse", "--abbrev-ref", "HEAD"): "feature/test",
        ("checkout", "feature/test"): "",
        ("rebase", "release-candidate"): "",
        ("push",): "",
    }
    calls = _capture_git_calls(monkeypatch, responses)
    monkeypatch.setattr(dev, "checkout_release_candidate_with_base", lambda: True)

    rc = dev.handle_branch_rebase()
    assert rc == 0
    assert "Rebased" in capsys.readouterr().out
    assert any(cmd[0][0] == "rebase" for cmd in calls)


def test_branch_rebase_disallows_main(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    responses = {
        ("rev-parse", "--abbrev-ref", "HEAD"): "main",
    }
    _capture_git_calls(monkeypatch, responses)
    rc = dev.handle_branch_rebase()
    assert rc == 2
    assert "feature branch" in capsys.readouterr().err
