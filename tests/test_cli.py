from __future__ import annotations

from pathlib import Path

import pytest

from greeble_cli import main
from greeble_cli.manifest import Manifest, default_manifest_path, load_manifest


def _component_template(component: str, manifest: Manifest) -> Path:
    return (
        manifest.root
        / "packages"
        / "greeble_components"
        / "components"
        / component
        / "templates"
        / (component if component != "palette" else "palette")
    )


def test_manifest_load() -> None:
    manifest = load_manifest(default_manifest_path())
    assert manifest.version >= 1
    assert "button" in manifest.components


def test_cli_list(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["list"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Available components" in captured.out
    assert "button" in captured.out


@pytest.mark.parametrize("component", ["button", "drawer", "palette"])
def test_cli_add_component(tmp_path: Path, component: str) -> None:
    project_root = tmp_path / f"app_{component}"
    exit_code = main(
        [
            "add",
            component,
            "--project",
            str(project_root),
            "--include-docs",
        ]
    )
    assert exit_code == 0
    assert (project_root / "templates" / "greeble" / f"{component}.html").exists()


def test_cli_add_nonexistent_component(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project_root = tmp_path / "app_nonexistent"
    missing = "not_a_real_component"
    exit_code = main(
        [
            "add",
            missing,
            "--project",
            str(project_root),
            "--include-docs",
        ]
    )
    assert exit_code != 0
    captured = capsys.readouterr()
    assert missing in captured.err


@pytest.mark.parametrize("component", ["button", "drawer"])
def test_cli_remove_component(tmp_path: Path, component: str) -> None:
    project_root = tmp_path / f"app_rm_{component}"
    main(
        [
            "add",
            component,
            "--project",
            str(project_root),
            "--include-docs",
        ]
    )
    target = project_root / "templates" / "greeble" / f"{component}.html"
    assert target.exists()
    exit_code = main(
        [
            "remove",
            component,
            "--project",
            str(project_root),
            "--include-docs",
        ]
    )
    assert exit_code == 0
    assert not target.exists()


def test_cli_sync_component(tmp_path: Path) -> None:
    component = "button"
    project_root = tmp_path / "app_sync"
    main(["add", component, "--project", str(project_root)])
    target = project_root / "templates" / "greeble" / "button.html"
    assert target.exists()
    target.write_text("MODIFIED", encoding="utf-8")
    exit_code = main(["sync", component, "--project", str(project_root)])
    assert exit_code == 0
    source = (
        default_manifest_path().parent
        / "packages"
        / "greeble_components"
        / "components"
        / component
        / "templates"
        / "button.html"
    )
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")


def test_cli_doctor(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["doctor"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Manifest path" in captured.out


def test_cli_new_starter(tmp_path: Path) -> None:
    project_root = tmp_path / "starter"
    exit_code = main(["new", str(project_root), "--include-docs"])
    assert exit_code == 0

    starter_main = project_root / "app" / "main.py"
    assert starter_main.exists()
    content = starter_main.read_text(encoding="utf-8")
    assert "FastAPI" in content
    assert "/modal/submit" in content

    modal_template = project_root / "templates" / "greeble" / "modal.html"
    assert modal_template.exists()
    modal_partial = project_root / "templates" / "greeble" / "modal.partial.html"
    assert modal_partial.exists()

    docs_path = project_root / "docs" / "components" / "modal.md"
    assert docs_path.exists()


def test_cli_new_requires_force_for_non_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "starter"
    project_root.mkdir()
    (project_root / "README.md").write_text("existing", encoding="utf-8")

    exit_code = main(["new", str(project_root)])
    assert exit_code == 2

    exit_code = main(["new", str(project_root), "--force"])
    assert exit_code == 0


def test_cli_new_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project_root = tmp_path / "preview"
    exit_code = main(["new", str(project_root), "--dry-run"])
    assert exit_code == 0
    assert not project_root.exists()

    captured = capsys.readouterr()
    assert "Starter files that would be created" in captured.out
    assert "templates/greeble/modal.html" in captured.out
