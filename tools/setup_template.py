#!/usr/bin/env python3
"""
Setup script for tokenized Python project template.

This script personalizes a template repository by replacing placeholders with your
chosen names and optionally initializing git.

Placeholders expected in the template:
- {{project_name}} : Project/repository name (e.g., used in pyproject name)
- {{package_name}} : Python package import name (e.g., src/{{package_name}})

Usage examples:
  # Prompt for names interactively
  python tools/setup_template.py

  # Provide names via flags and initialize git with remote
  python tools/setup_template.py \
      --project-name my-cool-thing \
      --package-name my_cool_thing \
      --init-git \
      --remote-url https://github.com/you/my-cool-thing

Notes:
- The script modifies files in-place under the current directory.
- It skips common build and VCS directories (e.g., .git, .venv).
- It will also rename directories that are named exactly '{{package_name}}'.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PH_PROJECT = "{{project_name}}"
PH_PACKAGE = "{{package_name}}"

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
EXCLUDE_FILES: set[str] = set()

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


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    return path.name in EXCLUDE_FILES


def validate_project_name(name: str) -> bool:
    # Allow PEP 503 normalized names (letters, numbers, '-', '_', '.')
    return bool(re.fullmatch(r"[A-Za-z0-9._-]+", name))


def validate_package_name(name: str) -> bool:
    # Python package name: letters, numbers, underscore, not starting with a digit
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))


def replace_tokens_in_text(content: str, project_name: str, package_name: str) -> str:
    # Targeted replacements; keep simple for robustness across many files
    content = content.replace(PH_PROJECT, project_name)
    content = content.replace(PH_PACKAGE, package_name)
    return content


def rename_token_dirs(root: Path, package_name: str) -> None:
    """Rename any directory path segments that are exactly the package token.

    We do a bottom-up traversal to avoid breaking parent paths prematurely.
    """
    # Collect directories first
    dirs = [p for p in root.rglob("*") if p.is_dir() and not should_skip(p)]
    # Sort by depth descending so we rename deepest first
    dirs.sort(key=lambda p: len(p.relative_to(root).parts), reverse=True)
    for d in dirs:
        if d.name == PH_PACKAGE:
            new_d = d.with_name(package_name)
            if not new_d.exists():
                d.rename(new_d)


def rewrite_files(root: Path, project_name: str, package_name: str) -> None:
    for p in root.rglob("*"):
        if should_skip(p) or p.is_dir():
            continue
        if is_text_file(p):
            try:
                content = p.read_text(encoding="utf-8")
            except Exception:
                continue
            new_content = replace_tokens_in_text(content, project_name, package_name)
            if new_content != content:
                p.write_text(new_content, encoding="utf-8")


def git_init(remote_url: str | None, default_branch: str = "main") -> None:
    subprocess.check_call(["git", "init"])  # current directory
    subprocess.check_call(["git", "checkout", "-B", default_branch])
    subprocess.check_call(["git", "add", "-A"])
    subprocess.check_call(["git", "commit", "-m", "chore: initialize project from template"])
    if remote_url:
        subprocess.check_call(["git", "remote", "add", "origin", remote_url])
        subprocess.check_call(["git", "push", "-u", "origin", default_branch])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Personalize a template by replacing placeholders")
    ap.add_argument("--project-name", help="New project/repo name (e.g., my-cool-thing)")
    ap.add_argument("--package-name", help="New Python package name (e.g., my_cool_thing)")
    ap.add_argument("--init-git", action="store_true", help="Initialize a git repo and commit")
    ap.add_argument("--remote-url", help="Optional remote URL to add as origin and push")
    ap.add_argument("--default-branch", default="main", help="Default branch name (main)")
    args = ap.parse_args(argv)

    project_name = args.project_name or input("Project name (e.g., my-cool-thing): ").strip()
    package_name = args.package_name or input("Package name (e.g., my_cool_thing): ").strip()

    if not validate_project_name(project_name):
        sys.stderr.write("error: invalid project name. Use letters, digits, '.', '_' or '-'.\n")
        return 2
    if not validate_package_name(package_name):
        sys.stderr.write(
            "error: invalid package name. Must be a valid Python identifier "
            "(letters, digits, '_', not starting with a digit).\n"
        )
        return 2

    root = Path.cwd()
    # 1) Rename any {{package_name}} directories first (e.g., src/{{package_name}})
    rename_token_dirs(root, package_name)
    # 2) Replace placeholders in text files
    rewrite_files(root, project_name, package_name)

    print("Applied template tokens:")
    print(f"  {PH_PROJECT} -> {project_name}")
    print(f"  {PH_PACKAGE} -> {package_name}")

    if args.init_git:
        try:
            git_init(args.remote_url, args.default_branch)
            print("Initialized git repository and pushed to origin.")
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"warning: git initialization failed: {e}\n")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
