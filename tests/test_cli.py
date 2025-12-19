from __future__ import annotations

from importlib import metadata
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


def test_manifest_default_path_uses_packaged_distribution(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeFile:
        def __init__(self, name: str, located: Path) -> None:
            self._name = name
            self._located = located

        def __str__(self) -> str:
            return self._name

        def locate(self) -> Path:
            return self._located

    packaged_manifest = Path("/tmp/greeble.manifest.yaml")

    def _files(_: str):
        return [
            _FakeFile("foo.txt", Path("/tmp/foo.txt")),
            _FakeFile("greeble.manifest.yaml", packaged_manifest),
        ]

    monkeypatch.setattr(metadata, "files", _files)
    assert default_manifest_path() == packaged_manifest


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
    assert (project_root / "docs" / "components" / f"{component}.md").exists()


def test_cli_add_component_custom_docs(tmp_path: Path) -> None:
    project_root = tmp_path / "app_modal_docs"
    exit_code = main(
        [
            "add",
            "modal",
            "--project",
            str(project_root),
            "--include-docs",
            "--docs",
            "documentation",
        ]
    )
    assert exit_code == 0
    assert (project_root / "templates" / "greeble" / "modal.html").exists()
    assert (project_root / "documentation" / "components" / "modal.md").exists()
    # Hyperscript snippet should be included for modal
    assert (project_root / "templates" / "greeble" / "modal.hyperscript.html").exists()


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

    starter_main = project_root / "src" / "greeble_starter" / "app.py"
    assert starter_main.exists()
    content = starter_main.read_text(encoding="utf-8")
    assert "FastAPI" in content

    modal_template = project_root / "templates" / "greeble" / "modal.html"
    assert modal_template.exists()
    modal_partial = project_root / "templates" / "greeble" / "modal.partial.html"
    assert modal_partial.exists()
    # Hyperscript snippet should be present in starter assets as well
    modal_hyperscript = project_root / "templates" / "greeble" / "modal.hyperscript.html"
    assert modal_hyperscript.exists()

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


def test_cli_init_baseline_assets(tmp_path: Path) -> None:
    project_root = tmp_path / "existing"
    exit_code = main(["init", "--project", str(project_root)])
    assert exit_code == 0
    assert (project_root / "static" / "greeble" / "greeble-core.css").exists()
    assert (project_root / "static" / "greeble" / "greeble-landing.css").exists()
    assert (project_root / "static" / "greeble" / "hyperscript" / "greeble.hyperscript").exists()


def test_cli_init_baseline_assets_dry_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = tmp_path / "existing"
    exit_code = main(["init", "--project", str(project_root), "--dry-run"])
    assert exit_code == 0
    assert not (project_root / "static").exists()

    captured = capsys.readouterr()
    assert "Baseline assets that would be created" in captured.out
    assert "static/greeble/greeble-core.css" in captured.out
    assert "static/greeble/greeble-landing.css" in captured.out
    assert "static/greeble/hyperscript/greeble.hyperscript" in captured.out


def test_cli_init_baseline_assets_existing_files_without_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = tmp_path / "existing"

    existing_paths = [
        Path("static/greeble/greeble-core.css"),
        Path("static/greeble/greeble-landing.css"),
        Path("static/greeble/hyperscript/greeble.hyperscript"),
    ]
    for rel_path in existing_paths:
        file_path = project_root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("", encoding="utf-8")

    exit_code = main(["init", "--project", str(project_root)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "already exists" in captured.err
    assert "greeble-core.css" in captured.err


def test_cli_add_with_init_scaffolds_baseline(tmp_path: Path) -> None:
    project_root = tmp_path / "app_init"
    exit_code = main(["add", "modal", "--project", str(project_root), "--init"])
    assert exit_code == 0
    assert (project_root / "templates" / "greeble" / "modal.html").exists()
    assert (project_root / "static" / "greeble" / "greeble-core.css").exists()


def test_cli_sync_with_init_scaffolds_baseline_and_respects_dry_run(tmp_path: Path) -> None:
    project_root = tmp_path / "sync_init"

    exit_code = main(["sync", "modal", "--project", str(project_root), "--init", "--dry-run"])
    assert exit_code == 0
    assert not (project_root / "static" / "greeble" / "greeble-core.css").exists()
    assert not (project_root / "static" / "greeble" / "greeble-landing.css").exists()
    assert not (
        project_root / "static" / "greeble" / "hyperscript" / "greeble.hyperscript"
    ).exists()

    exit_code = main(["sync", "modal", "--project", str(project_root), "--init"])
    assert exit_code == 0
    assert (project_root / "static" / "greeble" / "greeble-core.css").exists()
    assert (project_root / "static" / "greeble" / "greeble-landing.css").exists()
    assert (project_root / "static" / "greeble" / "hyperscript" / "greeble.hyperscript").exists()


def test_cli_add_with_init_requires_force_when_baseline_assets_exist(tmp_path: Path) -> None:
    project_root = tmp_path / "idempotent_add"
    assert main(["add", "modal", "--project", str(project_root), "--init"]) == 0
    assert (project_root / "static" / "greeble" / "greeble-core.css").exists()

    # Second run should fail without --force since baseline assets already exist
    assert main(["add", "modal", "--project", str(project_root), "--init"]) == 2

    # With --force it should succeed
    assert main(["add", "modal", "--project", str(project_root), "--init", "--force"]) == 0


def test_cli_theme_init_scaffolds_tailwind_config(tmp_path: Path) -> None:
    project_root = tmp_path / "tw_project"
    exit_code = main(
        [
            "theme",
            "init",
            "--project",
            str(project_root),
            "--config",
            "tailwind.config.cjs",
            "--preset-dest",
            "tools/greeble/tailwind/preset.cjs",
            "--content",
            "./templates/**/*.html",
            "--content",
            "./docs/**/*.md",
        ]
    )
    assert exit_code == 0
    preset_path = project_root / "tools" / "greeble" / "tailwind" / "preset.cjs"
    theme_path = project_root / "tools" / "greeble" / "tailwind" / "theme.cjs"
    index_path = project_root / "tools" / "greeble" / "tailwind" / "index.js"
    config_path = project_root / "tailwind.config.cjs"
    assert preset_path.exists(), "Expected Tailwind preset to be copied into project"
    assert theme_path.exists(), "Expected Tailwind theme helper to be copied"
    assert index_path.exists(), "Expected Tailwind preset ESM entry to be copied"
    assert config_path.exists(), "Expected Tailwind config to be created"
    cfg = config_path.read_text(encoding="utf-8")
    assert "presets: [require('./tools/greeble/tailwind/preset.cjs')]" in cfg
    assert "./templates/**/*.html" in cfg and "./docs/**/*.md" in cfg
    assert cfg.startswith("/** Generated by greeble theme init */")


def test_cli_theme_init_requires_force_when_files_exist(tmp_path: Path) -> None:
    project_root = tmp_path / "tw_project"
    args = [
        "theme",
        "init",
        "--project",
        str(project_root),
    ]
    first_exit = main(args)
    assert first_exit == 0

    second_exit = main(args)
    assert second_exit == 2, "Second run without --force should fail when files exist"


def test_cli_theme_init_force_overwrites(tmp_path: Path) -> None:
    project_root = tmp_path / "tw_project"
    args = [
        "theme",
        "init",
        "--project",
        str(project_root),
    ]
    assert main(args) == 0

    preset_asset = project_root / "tools" / "greeble" / "tailwind" / "preset.cjs"
    preset_asset.write_text("// modified", encoding="utf-8")

    force_args = [*args, "--force"]
    assert main(force_args) == 0
    content = preset_asset.read_text(encoding="utf-8")
    assert "--greeble-color-background" in content, (
        "Force run should overwrite with canonical preset contents"
    )
