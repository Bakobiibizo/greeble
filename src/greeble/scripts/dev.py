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
  - branch-finalize -> merge the current branch into release-candidate and push
  - branch-rebase -> rebase current branch onto latest release-candidate
  - branch-create -> create a new branch from release-candidate (prompts if omitted)
  - release-pr -> open a PR from release-candidate to main (uses latest CHANGELOG)
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
from contextlib import suppress
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
            "docs-serve",
            "docs-build",
            "release",
            "branch-finalize",
            "branch-rebase",
            "branch-create",
            "release-pr",
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
        case "docs-serve":
            # Serve docs with MkDocs Material if installed
            # Default bind: localhost:8000; allow passthrough to override
            return run(["mkdocs", "serve", *passthrough])
        case "docs-build":
            # Build static docs site into ./site (default)
            return run(["mkdocs", "build", *passthrough])
        case "release":
            return handle_release(passthrough)
        case "branch-finalize":
            return handle_branch_finalize()
        case "branch-rebase":
            return handle_branch_rebase()
        case "branch-create":
            return handle_branch_create(passthrough)
        case "release-pr":
            return handle_release_pr()
        case "protect-main":
            return handle_protect_main()
    parser.error("unknown subcommand")
    return 2


def run_mypy_then(final_cmd: list[str]) -> int:
    """Run mypy first, then the provided final command if type-checking passes."""
    return rc if (rc := run(["mypy", "."])) != 0 else run(final_cmd)


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
    # Use --no-verify to avoid pre-commit failing the release commit if it reformats files
    git(["commit", "--no-verify", "-m", f"chore(release): v{new_version}"])
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
        if proc.returncode != 0:
            raise RuntimeError("gh api command failed")
        print("Branch protection for main configured via gh CLI.")
        return 0
    except Exception as e:
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


def handle_branch_finalize() -> int:
    """Merge the current branch into 'release-candidate' and push.

    - Detect the current branch (must not be 'release-candidate').
    - Checkout 'release-candidate' based on (in order): origin/release-candidate, origin/main, main.
    - Merge the current branch with a no-fast-forward merge.
    - Push 'release-candidate' (creates upstream if needed).
    - Switch back to the original branch on success.
    """
    try:
        current = git(["rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    except subprocess.CalledProcessError:
        sys.stderr.write("error: not a git repository or cannot determine current branch\n")
        return 2
    current = current.strip()
    if current == "release-candidate":
        sys.stderr.write(
            "error: you're already on 'release-candidate'. Run this from a feature branch.\n"
        )
        return 2

    # Try to fetch remotes to get latest refs
    with suppress(subprocess.CalledProcessError):
        git(["fetch", "--all"])

    # Checkout release-candidate with sensible base
    if not checkout_release_candidate_with_base():
        sys.stderr.write(
            "error: could not checkout 'release-candidate'. "
            "Ensure 'main' exists locally or on origin.\n"
        )
        return 2

    # Merge current branch (auto-approve commit message with --no-edit)
    try:
        git(["merge", "--no-ff", "--no-edit", current])
    except subprocess.CalledProcessError:
        print(
            "Merge conflicts detected while merging into 'release-candidate'.\n"
            "Resolve conflicts, commit the merge, then push with:\n"
            "  git push -u origin release-candidate\n"
        )
        return 1

    # Push RC
    try:
        git(["push", "-u", "origin", "release-candidate"])
        pushed = True
    except subprocess.CalledProcessError:
        pushed = False
        print(
            "Could not push 'release-candidate' automatically. Push manually with:\n"
            "  git push -u origin release-candidate\n"
        )

    # Switch back to original branch
    with suppress(subprocess.CalledProcessError):
        # stay on RC if we cannot switch back
        git(["checkout", current])

    if pushed:
        print("Merged current branch into 'release-candidate' and pushed upstream.")
        return 0
    print("Merged current branch into 'release-candidate'. Not pushed.")
    return 0


def checkout_release_candidate_with_base() -> bool:
    """Checkout 'release-candidate' creating/updating it from the best available base."""
    bases = [
        "origin/release-candidate",
        "origin/main",
        "main",
    ]
    for base in bases:
        try:
            git(["checkout", "-B", "release-candidate", base])
            return True
        except subprocess.CalledProcessError:
            continue
    # Last resort: try to just create the branch if no base is available
    try:
        git(["checkout", "-B", "release-candidate"])  # detached from any base
        return True
    except subprocess.CalledProcessError:
        return False


def handle_branch_create(args: Sequence[str]) -> int:
    """Create a new branch from 'release-candidate'.

    Usage:
      dev branch-create [<tag>/<branch-name>]

    If the name is omitted, the user will be prompted. Allowed tags are:
    feat, fix, docs, chore, refactor, perf, test, build, ci.
    """
    allowed = {"feat", "fix", "docs", "chore", "refactor", "perf", "test", "build", "ci"}

    name = args[0].strip() if args else ""
    if not name:
        try:
            name = input("Enter new branch (e.g., feat/my-change): ").strip()
        except EOFError:
            sys.stderr.write("error: branch name required\n")
            return 2

    if "/" not in name:
        sys.stderr.write("error: name must be in the form <tag>/<branch-name>\n")
        return 2
    tag, _, rest = name.partition("/")
    if tag not in allowed:
        sys.stderr.write("error: tag must be one of: " + ", ".join(sorted(allowed)) + "\n")
        return 2
    if not re.fullmatch(r"[A-Za-z0-9._\-][A-Za-z0-9._\-/]*", rest):
        sys.stderr.write("error: branch name contains invalid characters\n")
        return 2

    # Prepare base branch 'release-candidate'
    with suppress(subprocess.CalledProcessError):
        git(["fetch", "--all"])
    # Ensure we can checkout/update RC
    if not checkout_release_candidate_with_base():
        sys.stderr.write(
            "error: could not prepare 'release-candidate'. "
            "Ensure 'main' exists locally or on origin.\n"
        )
        return 2

    # Create the branch from RC
    try:
        git(["checkout", "-B", name, "release-candidate"])
    except subprocess.CalledProcessError:
        sys.stderr.write("error: failed to create branch from release-candidate\n")
        return 1

    # Try to push and set upstream
    try:
        git(["push", "-u", "origin", name])
        print(f"Created and pushed branch '{name}' from release-candidate.")
        return 0
    except subprocess.CalledProcessError:
        print(
            f"Created branch '{name}' from release-candidate.\n"
            f"Push manually with: git push -u origin {name}\n"
        )
        return 0


def handle_branch_rebase() -> int:
    """Rebase the current branch on top of the latest 'release-candidate'.

    - Ensures we're on a feature branch (not 'main' or 'release-candidate').
    - Fetches remotes and prepares RC via checkout_release_candidate_with_base().
    - Rebases the current branch onto 'release-candidate'.
    - Attempts a normal push; if it fails (non-fast-forward), suggests
      `git push --force-with-lease`.
    """
    try:
        current = git(["rev-parse", "--abbrev-ref", "HEAD"], capture_output=True).strip()
    except subprocess.CalledProcessError:
        sys.stderr.write("error: not a git repository or cannot determine current branch\n")
        return 2
    if current in {"main", "release-candidate"}:
        sys.stderr.write(
            "error: rebase should be run from a feature branch "
            "(not 'main' or 'release-candidate')\n"
        )
        return 2

    with suppress(subprocess.CalledProcessError):
        git(["fetch", "--all"])
    if not checkout_release_candidate_with_base():
        sys.stderr.write(
            "error: could not prepare 'release-candidate'. "
            "Ensure 'main' exists locally or on origin.\n"
        )
        return 2

    # Switch back to the feature branch and rebase
    try:
        git(["checkout", current])
    except subprocess.CalledProcessError:
        sys.stderr.write("error: failed to return to current branch after preparing RC\n")
        return 1
    try:
        git(["rebase", "release-candidate"])
    except subprocess.CalledProcessError:
        print(
            "Rebase encountered conflicts. Resolve them and continue with:\n"
            "  git add -A\n  git rebase --continue\n"
            "Or abort rebase with:\n  git rebase --abort\n"
        )
        return 1

    # Try a normal push; if rejected, advise force-with-lease
    try:
        git(["push"])  # upstream assumed already set
        print("Rebased on 'release-candidate' and pushed successfully.")
        return 0
    except subprocess.CalledProcessError:
        print(
            "Rebased on 'release-candidate'. Upstream rejected push.\n"
            "Push with: git push --force-with-lease\n"
        )
        return 0


def handle_release_pr() -> int:
    """Open a GitHub PR from release-candidate to main using the latest changelog.

    Requires the GitHub CLI (gh). The PR title will default to "Release vX.Y.Z" if the
    latest CHANGELOG section header is of the form `## [X.Y.Z] - YYYY-MM-DD`, otherwise
    it will be "Release candidate to main". The PR body will be the content of the
    latest section.
    """
    if shutil_which("gh") is None:
        print(
            "GitHub CLI (gh) not found. Install from https://cli.github.com/ and run:\n"
            "  gh auth login\n"
            "Then re-run: uv run dev release-pr\n"
        )
        return 2

    # Ensure release-candidate exists locally
    with suppress(subprocess.CalledProcessError):
        git(["fetch", "--all"])
    try:
        git(["rev-parse", "--verify", "release-candidate"], capture_output=True)
    except subprocess.CalledProcessError:
        sys.stderr.write(
            "error: 'release-candidate' branch not found. Create it first with "
            "'uv run dev release rc' or 'uv run dev branch-finalize'.\n"
        )
        return 2

    root = find_project_root()
    changelog_path = root / "CHANGELOG.md"
    version, section_body = parse_changelog_latest_section(changelog_path)
    title = f"Release v{version}" if version else "Release candidate to main"
    body = section_body or "(No changelog entries found)"

    # Create PR with gh
    cmd = [
        "gh",
        "pr",
        "create",
        "--base",
        "main",
        "--head",
        "release-candidate",
        "--title",
        title,
        "--body",
        body,
    ]
    proc = subprocess.run(cmd, check=False)
    if proc.returncode == 0:
        print("Opened pull request from release-candidate to main.")
        return 0
    print("Failed to open pull request via gh CLI. Ensure you are authenticated.")
    return 1


def parse_changelog_latest_section(
    changelog_path: Path,
) -> tuple[str | None, str]:
    """Return (version, section_body) for the latest changelog section.

    The expected header format is: `## [X.Y.Z] - YYYY-MM-DD`.
    If the file or header is missing, returns (None, "").
    """
    if not changelog_path.exists():
        return None, ""
    lines = changelog_path.read_text(encoding="utf-8").splitlines()
    header_re = re.compile(r"^## \[(?P<ver>\d+\.\d+\.\d+)\] - ")
    version: str | None = None
    start_idx: int | None = None
    end_idx: int | None = None
    for i, line in enumerate(lines):
        if m := header_re.match(line.strip()):
            if start_idx is None:
                start_idx = i
                version = m["ver"]
            elif end_idx is None:
                end_idx = i
                break
    if start_idx is None:
        return None, ""
    if end_idx is None:
        end_idx = len(lines)
    # Section body excludes the header and ends before next section header
    body_lines = lines[start_idx + 1 : end_idx]
    # Trim leading blank lines
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    # Keep body as markdown
    return version, "\n".join(body_lines).strip()


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
    def _repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}"{new_version}"'

    new_content, n = re.subn(r"(?m)^(version\s*=\s*)\"[^\"]+\"", _repl, content)
    if n == 0:
        raise ValueError("Could not update version in pyproject.toml")
    pyproject_path.write_text(new_content, encoding="utf-8")


def bump_version(version: str, part: VersionPart) -> str:
    try:
        major_s, minor_s, patch_s = version.split(".")
        major, minor, patch = int(major_s), int(minor_s), int(patch_s)
    except Exception as e:
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
    log_cmd = ["log", f"--pretty=format:{fmt}", "--no-merges"]
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
        ctype = m["type"] if m else "other"
        csubject = m["subject"] if m else subject
        entries.append((ctype, csubject, sha))
    return entries


def tag_exists(tag: str) -> bool:
    try:
        out = git(["tag", "-l", tag], capture_output=True)
        return any(line.strip() == tag for line in out.splitlines())
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
    return (m["owner"], m["repo"]) if m else None


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
