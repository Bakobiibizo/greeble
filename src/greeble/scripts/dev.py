"""
Developer helper CLI: `uv run dev <subcommand>`

Subcommands:
  - lint       -> ruff check .  (adds --fix locally; check-only in CI)
  - format     -> ruff format .
  - typecheck  -> mypy .
  - fix        -> ruff check --fix .
  - precommit  -> pre-commit run --all-files
  - ci         -> ruff check . + ruff format --check . + mypy . + uv build
  - test       -> pytest -q
  - build      -> uv build
  - check      -> ruff check (--fix locally) + ruff format . + mypy . + pytest -q
  - version    -> dev version [current|bump <major|minor|patch>]
  - release    -> dev release rc  (create and push the release-candidate branch)
  - protect-main -> attempt to enable branch protection via gh CLI

Pass-through args after the subcommand are forwarded to the underlying tool.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path
from typing import Literal, cast


def is_ci() -> bool:
    """Return True if running in a CI environment."""
    return bool(os.getenv("CI"))


def run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        sys.stderr.write(f"error: command not found: {cmd[0]}\n")
        sys.stderr.flush()
        return 127


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    parser = argparse.ArgumentParser(prog="dev", add_help=True)
    parser.add_argument(
        "subcommand",
        choices=[
            "lint",
            "format",
            "typecheck",
            "fix",
            "precommit",
            "ci",
            "test",
            "build",
            "check",
            "version",
            "release",
            "protect-main",
        ],
        help="task to run",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER, help="args to pass through")

    if not argv:
        parser.print_help()
        return 2

    ns = parser.parse_args(argv[:1])
    passthrough = argv[1:]
    # Allow callers to pass a conventional '--' separator (e.g., 'uv run dev format -- --check')
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    match ns.subcommand:
        case "lint":
            check_cmd = [
                "ruff",
                "check",
                *([] if is_ci() else ["--fix"]),
                ".",
                *passthrough,
            ]
            return run(check_cmd)
        case "format":
            return run(["ruff", "format", ".", *passthrough])
        case "typecheck":
            return run(["mypy", ".", *passthrough])
        case "fix":
            return run(["ruff", "check", "--fix", ".", *passthrough])
        case "precommit":
            return run(["pre-commit", "run", "--all-files", *passthrough])
        case "ci":
            if (rc := run(["ruff", "check", "."])) != 0:
                return rc
            if (rc := run(["ruff", "format", "--check", "."])) != 0:
                return rc
            return run_mypy_then(["uv", "build"])
        case "test":
            return run(["pytest", "-q", *passthrough])
        case "build":
            return run(["uv", "build", *passthrough])
        case "check":
            # Match pre-commit order: ruff check --fix, then ruff format
            check_cmd = ["ruff", "check", *([] if is_ci() else ["--fix"]), "."]
            if (rc := run(check_cmd)) != 0:
                return rc
            if (rc := run(["ruff", "format", "."])) != 0:
                return rc
            return run_mypy_then_pytest_quiet()
        case "version":
            return handle_version(passthrough)
        case "release":
            return handle_release(passthrough)
        case "protect-main":
            return handle_protect_main()
    parser.error("unknown subcommand")
    return 2


def run_mypy_then(final_cmd: list[str]) -> int:
    """Run mypy first, then the provided final command if type-checking passes."""
    if (rc := run(["mypy", "."])) != 0:
        return rc
    return run(final_cmd)


def run_mypy_then_pytest_quiet() -> int:
    """Run mypy then pytest -q, treating pytest's exit code 5 (no tests) as success."""
    if (rc := run(["mypy", "."])) != 0:
        return rc
    rc = run(["pytest", "-q"]) or 0
    return 0 if rc in (0, 5) else rc


# --- Versioning & Release helpers -------------------------------------------------

VersionPart = Literal["major", "minor", "patch"]


def handle_version(args: Sequence[str]) -> int:
    """`dev version [current|bump <major|minor|patch>]`

    - `current`: prints the current version to stdout
    - `bump <part>`: increments version in pyproject.toml, updates CHANGELOG.md from
      conventional commits since last tag, creates a release commit and an annotated tag.
    """
    cmd = args[0] if args else "current"
    if cmd not in {"current", "bump"}:
        sys.stderr.write("usage: dev version [current|bump <major|minor|patch>]\n")
        return 2

    root = find_project_root()
    pyproject = root / "pyproject.toml"
    if cmd == "current":
        print(read_project_version(pyproject))
        return 0

    # bump flow
    part: VersionPart = "patch"
    if len(args) >= 2:
        part_arg = args[1].lower()
        if part_arg not in {"major", "minor", "patch"}:
            sys.stderr.write("error: part must be one of: major, minor, patch\n")
            return 2
        part = cast(VersionPart, part_arg)

    current_version = read_project_version(pyproject)
    new_version = bump_version(current_version, part)

    # Update pyproject.toml
    write_project_version(pyproject, new_version)

    # Update CHANGELOG.md
    changelog = root / "CHANGELOG.md"
    prev_tag = f"v{current_version}"
    entries = collect_conventional_commits(prev_tag)
    prepend_changelog(changelog, new_version, entries)

    # Commit and tag
    git(["add", str(pyproject), str(changelog)])
    git(["commit", "-m", f"chore(release): v{new_version}"])
    git(["tag", "-a", f"v{new_version}", "-m", f"Release v{new_version}"])
    print(f"Bumped version: {current_version} -> {new_version}")
    print(f"Created tag v{new_version}. Push with: git push && git push --tags")
    return 0


def handle_protect_main() -> int:
    """Attempt to protect the `main` branch using GitHub CLI, or print instructions."""
    # Try to detect owner/repo from git and use gh if available.
    try:
        origin = git(["config", "--get", "remote.origin.url"], capture_output=True)
        owner_repo = parse_owner_repo(origin.strip())
        if not owner_repo:
            raise RuntimeError("Could not parse owner/repo from remote.origin.url")
        if shutil_which("gh") is None:
            raise RuntimeError("gh CLI not found")
        owner, repo = owner_repo
        payload = (
            "{\n"
            '  "enforce_admins": true,\n'
            '  "required_status_checks": null,\n'
            '  "required_pull_request_reviews": {\n'
            '    "required_approving_review_count": 1\n'
            "  },\n"
            '  "restrictions": null\n'
            "}"
        )
        gh_cmd = [
            "gh",
            "api",
            "-X",
            "PUT",
            f"repos/{owner}/{repo}/branches/main/protection",
            "-H",
            "Accept: application/vnd.github+json",
            "--input",
            "-",
        ]
        # Feed JSON via stdin
        proc = subprocess.run(gh_cmd, input=payload.encode(), check=False)
        if proc.returncode == 0:
            print("Branch protection for main configured via gh CLI.")
            return 0
        else:
            raise RuntimeError("gh api command failed")
    except Exception as e:  # noqa: BLE001 - we want a friendly message
        print(
            (
                "Could not configure branch protection automatically.\n"
                "To enable manually, run:\n"
                "  gh api -X PUT repos/<owner>/<repo>/branches/main/protection \\\n"
                "    -H 'Accept: application/vnd.github+json' \\\n"
                "    --input - <<'JSON'\n"
                "{\n"
                '  "enforce_admins": true,\n'
                '  "required_status_checks": null,\n'
                '  "required_pull_request_reviews": {\n'
                '    "required_approving_review_count": 1\n'
                "  },\n"
                '  "restrictions": null\n'
                "}\n"
                "JSON\n"
            )
            + (f"Reason: {e}\n")
        )
        return 1


def shutil_which(
    name: str,
) -> str | None:
    from shutil import which

    return which(name)


def handle_release(args: Sequence[str]) -> int:
    """`dev release rc` creates and pushes the `release-candidate` branch.

    Intended workflow:
    - Create `release-candidate`
    - Merge feature branches into `release-candidate`
    - When ready, merge `release-candidate` into `main` and bump version
    """
    if not args or args[0] != "rc":
        sys.stderr.write("usage: dev release rc\n")
        return 2
    # Ensure working tree clean, or proceed? We'll proceed but git may block.
    branch = "release-candidate"
    git(["checkout", "-B", branch])
    # Push and set upstream
    try:
        git(["push", "-u", "origin", branch])
    except subprocess.CalledProcessError:
        # Origin may not be set; print next steps
        print("Created local branch 'release-candidate'. Set up a remote and push when ready.")
        return 0
    print("Release candidate branch created and pushed: release-candidate")
    return 0


def find_project_root() -> Path:
    """Find the project root containing a pyproject.toml."""
    cur = Path.cwd()
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").exists():
            return p
    raise FileNotFoundError("pyproject.toml not found in current directory or parents")


def read_project_version(pyproject_path: Path) -> str:
    import tomllib

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not isinstance(version, str):
        raise ValueError("project.version not found or invalid in pyproject.toml")
    return version


def write_project_version(pyproject_path: Path, new_version: str) -> None:
    content = pyproject_path.read_text(encoding="utf-8")
    # Replace the first occurrence of version = "..." under [project]
    # Simple, assumes a single project.version key.
    new_content, n = re.subn(r"(?m)^(version\s*=\s*)\"[^\"]+\"", rf"\1\"{new_version}\"", content)
    if n == 0:
        raise ValueError("Could not update version in pyproject.toml")
    pyproject_path.write_text(new_content, encoding="utf-8")


def bump_version(version: str, part: VersionPart) -> str:
    try:
        major_s, minor_s, patch_s = version.split(".")
        major, minor, patch = int(major_s), int(minor_s), int(patch_s)
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"invalid version: {version}") from e
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def git(args: Sequence[str], *, capture_output: bool = False) -> str:
    cmd = ["git", *args]
    if capture_output:
        return subprocess.check_output(cmd).decode().strip()
    subprocess.check_call(cmd)
    return ""


def collect_conventional_commits(since_tag: str | None) -> list[tuple[str, str, str]]:
    """Return list of (type, subject, short_sha) since a tag (or from start)."""
    fmt = "%h\t%s"
    range_spec = f"{since_tag}..HEAD" if since_tag and tag_exists(since_tag) else None
    log_cmd = ["log", "--pretty=format:" + fmt, "--no-merges"]
    if range_spec:
        log_cmd.append(range_spec)
    out = git(log_cmd, capture_output=True)
    entries: list[tuple[str, str, str]] = []
    cc_re = re.compile(
        r"^(?P<type>feat|fix|perf|refactor|docs|build|ci|test|chore|revert)"
        r"(?:\([^)]*\))?(?:!)?:\s*(?P<subject>.+)"
    )
    for line in out.splitlines():
        try:
            sha, subject = line.split("\t", 1)
        except ValueError:
            continue
        m = cc_re.match(subject)
        ctype = m.group("type") if m else "other"
        csubject = m.group("subject") if m else subject
        entries.append((ctype, csubject, sha))
    return entries


def tag_exists(tag: str) -> bool:
    try:
        git(["rev-parse", tag], capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def prepend_changelog(
    changelog_path: Path,
    new_version: str,
    entries: Iterable[tuple[str, str, str]],
) -> None:
    today = date.today().isoformat()
    header = f"## [{new_version}] - {today}\n\n"
    if not entries:
        body = "- No user-facing changes\n\n"
    else:
        # Group by type but keep chronological order
        type_order = [
            "feat",
            "fix",
            "perf",
            "refactor",
            "docs",
            "build",
            "ci",
            "test",
            "chore",
            "revert",
            "other",
        ]
        lines: list[str] = []
        for ctype in type_order:
            group = [(t, s, h) for (t, s, h) in entries if t == ctype]
            if not group:
                continue
            lines.append(f"### {ctype}")
            lines.extend([f"- {s} ({h})" for (_, s, h) in group])
            lines.append("")
        body = "\n".join(lines) + "\n"
    if changelog_path.exists():
        prev = changelog_path.read_text(encoding="utf-8")
    else:
        prev = "# Changelog\n\n"
    # Prepend new release notes so the latest version appears at the top
    new_content = header + body + prev
    changelog_path.write_text(new_content, encoding="utf-8")


def parse_owner_repo(remote_url: str) -> tuple[str, str] | None:
    # Support SSH and HTTPS
    # git@github.com:owner/repo.git or https://github.com/owner/repo.git
    m = re.search(r"github.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", remote_url)
    if not m:
        return None
    return m.group("owner"), m.group("repo")


def lint_main() -> int:
    return main(["lint"])  # applies fixes locally; check-only in CI


def format_main() -> int:
    return main(["format"])  # applies changes by default


def typecheck_main() -> int:
    return main(["typecheck"])  # mypy src


def test_main() -> int:
    return main(["test"])  # pytest -q


def check_main() -> int:
    return main(["check"])  # ruff check --fix ., ruff format ., mypy, pytest


def precommit_main() -> int:
    return main(["precommit"])  # pre-commit run --all-files


if __name__ == "__main__":
    raise SystemExit(main())
