#!/usr/bin/env python3
"""
Upload CSVs from files_to_data_bricks/<processor>/<farm>/ to a Unity Catalog Volume,
mirroring the same folder layout. Directories and files on the volume are created
only when missing; existing remote files are skipped.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from dotenv import load_dotenv

if TYPE_CHECKING:
    from databricks.sdk import WorkspaceClient

REPO_ROOT = Path(__file__).resolve().parent
load_dotenv(REPO_ROOT / ".env")
FILES_TO_DATABRICKS = REPO_ROOT / "files_to_data_bricks"
DEFAULT_VOLUME_BASE = "/Volumes/data_eng_dev/processor_raw/files"


def _volume_join(*parts: str) -> str:
    """Build an absolute /Volumes/... path with single slashes."""
    base = DEFAULT_VOLUME_BASE
    for p in parts:
        p = p.strip()
        if not p:
            continue
        p = p.strip("/")
        if not p:
            continue
        base = f"{base.rstrip('/')}/{p}"
    return base


def _iter_staged_csvs(
    staging_root: Path,
) -> Iterator[tuple[Path, str, str]]:
    """
    Yield (local_file, processor_name, farm_dir_name) for each CSV under
    staging_root/processor/farm/
    """
    if not staging_root.is_dir():
        return
    for proc_path in sorted(staging_root.iterdir()):
        if not proc_path.is_dir() or proc_path.name.startswith("."):
            continue
        processor = proc_path.name
        for farm_path in sorted(proc_path.iterdir()):
            if not farm_path.is_dir() or farm_path.name.startswith("."):
                continue
            farm = farm_path.name
            for f in sorted(farm_path.iterdir()):
                if not f.is_file() or f.name.startswith("."):
                    continue
                if not f.name.lower().endswith(".csv"):
                    print(f"Skipping non-CSV under {farm_path}: {f.name}")
                    continue
                yield (f, processor, farm)


def _check_auth_or_exit() -> None:
    if not os.environ.get("DATABRICKS_HOST", "").strip():
        print("DATABRICKS_HOST is not set; cannot connect to the workspace.", file=sys.stderr)
        raise SystemExit(1)
    if not os.environ.get("DATABRICKS_TOKEN", "").strip():
        print("DATABRICKS_TOKEN is not set; cannot authenticate.", file=sys.stderr)
        raise SystemExit(1)


def _ensure_directory(client: WorkspaceClient, directory_path: str) -> str | None:
    """
    Ensure a directory exists on the volume. Returns a log message if created,
    None if it already existed.
    """
    from databricks.sdk.errors import NotFound

    try:
        client.files.get_directory_metadata(directory_path)
    except NotFound:
        client.files.create_directory(directory_path)
        return f"Created directory: {directory_path}"
    return None


def _remote_file_exists(client: WorkspaceClient, file_path: str) -> bool:
    from databricks.sdk.errors import NotFound

    try:
        client.files.get_metadata(file_path)
    except NotFound:
        return False
    return True


def _upload_file(
    client: WorkspaceClient,
    local_path: Path,
    remote_path: str,
    dry_run: bool,
) -> str:
    """Return status: 'uploaded' | 'skipped' | 'dry_run' | 'error'."""
    if dry_run:
        print(f"Would upload: {local_path} -> {remote_path}")
        return "dry_run"

    if _remote_file_exists(client, remote_path):
        print(f"Skip (exists on volume): {remote_path}")
        return "skipped"

    # overwrite=False: only create when missing; race-safe intent with metadata check
    client.files.upload_from(
        file_path=remote_path,
        source_path=str(local_path),
        overwrite=False,
    )
    print(f"Uploaded: {local_path} -> {remote_path}")
    return "uploaded"


def run(
    dry_run: bool = False,
    staging_root: Path | None = None,
) -> tuple[dict[str, int], int]:
    """
    Walk staged files, ensure remote dirs, upload new files.
    Returns (counter dict, failure_count).
    """
    root = staging_root or FILES_TO_DATABRICKS
    stats = {
        "uploaded": 0,
        "skipped": 0,
        "dry_run": 0,
        "dir_created": 0,
    }
    failures: list[str] = []

    if not root.is_dir():
        print(f"Staging directory not found or not a directory: {root}", file=sys.stderr)
        return (stats, 0)

    if not any(root.iterdir()):
        print(f"Warning: staging directory is empty: {root}", file=sys.stderr)

    client: WorkspaceClient | None = None
    if not dry_run:
        _check_auth_or_exit()
        from databricks.sdk import WorkspaceClient

        client = WorkspaceClient()

    for local_file, processor, farm in _iter_staged_csvs(root):
        proc_remote = _volume_join(processor)
        farm_remote = _volume_join(processor, farm)
        file_remote = _volume_join(processor, farm, local_file.name)

        if dry_run:
            print(
                f"Would ensure remote dirs: {proc_remote} , {farm_remote} ; file: {file_remote}"
            )
            stats["dry_run"] += 1
            continue

        assert client is not None
        try:
            m = _ensure_directory(client, proc_remote)
            if m:
                print(m)
                stats["dir_created"] += 1
            m = _ensure_directory(client, farm_remote)
            if m:
                print(m)
                stats["dir_created"] += 1
            st = _upload_file(client, local_file, file_remote, dry_run=False)
            if st == "uploaded":
                stats["uploaded"] += 1
            elif st == "skipped":
                stats["skipped"] += 1
        except Exception as e:  # noqa: BLE001
            # Log and continue: network, auth, and volume errors
            err = f"{local_file} -> {e}"
            print(f"Error: {err}", file=sys.stderr)
            failures.append(err)

    n_fail = len(failures)
    return (stats, n_fail)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Upload files_to_data_bricks/<processor>/<farm>/*.csv to a "
            "Unity Catalog volume, creating remote folders and files as needed."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned ensure-dir and upload steps without calling Databricks (no auth needed).",
    )
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=None,
        help=f"Override local staging root (default: {FILES_TO_DATABRICKS})",
    )
    args = parser.parse_args()

    stats, n_fail = run(
        dry_run=args.dry_run,
        staging_root=args.staging_dir,
    )
    if args.dry_run:
        print(
            f"Done (dry run). would_process_files={stats['dry_run']}, "
            f"dir_created=0 (not connected)"
        )
    else:
        print(
            f"Done. uploaded={stats['uploaded']}, skipped_remote_exists={stats['skipped']}, "
            f"remote_dirs_created={stats['dir_created']}, failures={n_fail}"
        )
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
