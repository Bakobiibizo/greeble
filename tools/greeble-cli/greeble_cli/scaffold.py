# Re-export from main package (src/greeble_cli/scaffold.py)
from greeble_cli.scaffold import (  # noqa: F401
    CopyPlan,
    ScaffoldError,
    backup_existing_files,
    build_copy_plan,
    component_sources,
    ensure_within_project,
    execute_plan,
    remove_files,
)

__all__ = [
    "CopyPlan",
    "ScaffoldError",
    "backup_existing_files",
    "build_copy_plan",
    "component_sources",
    "ensure_within_project",
    "execute_plan",
    "remove_files",
]
