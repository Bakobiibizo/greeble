#!/usr/bin/env python3
"""
Export this repo as a tokenized template.

- Replaces occurrences of the current project and package names with placeholders
  in file contents and path names.
- Excludes typical build/venv/metadata directories.
- Optionally initializes a new git repo in the output directory and pushes to
  a remote (by default the URL of the local 'template' remote).

Placeholders used:
- {{project_name}} : The project/repo name (e.g., on PyPI/GitHub)
- {{package_name}} : The Python import package (src/{{package_name}})

Usage:
  uv run python tools/template_export.py --out-dir ../python-template-src --push
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

# Defaults for the current repo
CURRENT_PROJECT_NAME = "greeble"
CURRENT_PACKAGE_NAME = "greeble"

# Placeholders in the exported template
PH_PROJECT = "{{project_name}}"
PH_PACKAGE = "{{package_name}}"

# Exclusions for copying
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    ".idea",
    ".vscode",
}
EXCLUDE_FILES = {
    ".gitignore.lock",  # example placeholder; none currently
}

TEXT_EXTENSIONS = {
    ".py",
    ".toml",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".ini",
    ".cfg",
    ".sh",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
}


def is_text_file(path: Path) -> bool:
    if path.suffix in TEXT_EXTENSIONS:
        return True
    try:
        _ = path.read_text(encoding="utf-8")
        return True
    except Exception:
        return False


def renamed_rel_path(root: Path, path: Path) -> Path:
    """Return the new relative path with package name segments tokenized.

    Any path segment exactly equal to CURRENT_PACKAGE_NAME is replaced with PH_PACKAGE.
    """
    rel = path.relative_to(root)
    parts = [PH_PACKAGE if p == CURRENT_PACKAGE_NAME else p for p in rel.parts]
    return Path(*parts)


def replace_tokens_in_text(content: str) -> str:
    # Simple targeted replacements; avoid overreaching tokens inside URLs
    # Replace project name occurrences in pyproject name field patterns
    content = re.sub(r'(?m)^(\s*name\s*=\s*)"[^"]+"', rf'\1"{PH_PROJECT}"', content)

    # Replace import/package references and bare names
    content = content.replace(CURRENT_PACKAGE_NAME, PH_PACKAGE)
    # Capitalized occurrences (for titles)
    content = content.replace(CURRENT_PROJECT_NAME.capitalize(), PH_PROJECT)

    return content


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    return path.name in EXCLUDE_FILES


def copy_tree_with_tokens(src_root: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in src_root.rglob("*"):
        if should_skip(p):
            continue
        rel_new = renamed_rel_path(src_root, p)
        target = out_dir / rel_new
        if p.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_text_file(p):
            content = p.read_text(encoding="utf-8")
            new_content = replace_tokens_in_text(content)
            target.write_text(new_content, encoding="utf-8")
        else:
            shutil.copy2(p, target)


def git_remote_url(name: str) -> str | None:
    try:
        return subprocess.check_output(["git", "remote", "get-url", name]).decode().strip()
    except subprocess.CalledProcessError:
        return None


def git_init_and_push(out_dir: Path, remote_url: str | None, default_branch: str = "main") -> None:
    subprocess.check_call(["git", "init"], cwd=out_dir)
    subprocess.check_call(["git", "checkout", "-B", default_branch], cwd=out_dir)
    subprocess.check_call(["git", "add", "-A"], cwd=out_dir)
    subprocess.check_call(
        ["git", "commit", "-m", "chore: initialize from template export"], cwd=out_dir
    )
    if remote_url:
        subprocess.check_call(["git", "remote", "add", "origin", remote_url], cwd=out_dir)
        subprocess.check_call(["git", "push", "-u", "origin", default_branch], cwd=out_dir)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Export tokenized template copy of this repo")
    ap.add_argument("--out-dir", required=True, help="Directory to write the exported template")
    ap.add_argument(
        "--push",
        action="store_true",
        help="Initialize a git repo in out-dir and push to the 'template' remote URL",
    )
    ap.add_argument(
        "--remote-url",
        help="Explicit remote URL to push to (overrides the local 'template' remote)",
    )
    args = ap.parse_args(argv)

    src_root = Path.cwd()
    out_dir = Path(args.out_dir).resolve()

    copy_tree_with_tokens(src_root, out_dir)

    if args.push:
        remote_url = args.remote_url or git_remote_url("template")
        if not remote_url:
            print("No remote URL provided and no 'template' remote configured. Skipping push.")
        else:
            git_init_and_push(out_dir, remote_url)
            print(f"Exported and pushed template to: {remote_url}")
    else:
        print(f"Exported template to: {out_dir}")

    print("Placeholders used: {{project_name}}, {{package_name}}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
