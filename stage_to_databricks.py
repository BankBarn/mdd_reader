#!/usr/bin/env python3
"""
Move CSVs from mdd_downloads into files_to_data_bricks/<processor>/<farm>/
with filenames prefixed as yyyymmdd_<original_name>.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import sqlAPI

REPO_ROOT = Path(__file__).resolve().parent
FILES_TO_DATABRICKS = REPO_ROOT / "files_to_data_bricks"
DOWNLOADS = REPO_ROOT / "mdd_downloads"
MILK_REPORT_SUFFIX = "_Milk_Sample_Report"
_DATED_CSV = re.compile(r"^\d{8}_.+\.csv$", re.IGNORECASE)


def _name_for_farm_match(filename: str) -> str:
    """If the download was already yyyymmdd_ prefixed, strip that for MDD stem matching."""
    if _DATED_CSV.match(filename) and len(filename) > 9 and filename[8] == "_":
        return filename[9:]
    return filename


def _farm_name_to_file_prefix(farm_name: str) -> str:
    return farm_name.replace(" ", "_")


def _safe_farm_dir_name(farm_name: str) -> str:
    """Build a single path segment for the farm folder (avoids / and \\)."""
    s = farm_name.replace("/", "-").replace("\\", "-")
    s = s.strip() or "unknown_farm"
    if s in (".", ".."):
        return f"_{s}"
    return s


def _match_farm_and_processor(
    filename: str, farms_with_processors: list[tuple[str, str]]
) -> tuple[str, str] | None:
    """
    Match filename to (farm_name, processor_name) using longest farm name first
    and requiring the name to start with the normalized farm prefix + _Milk_Sample_Report.
    """
    # Longest first so e.g. "Minglewood, Inc. - 01010000427" wins over "Minglewood, Inc."
    sorted_rows = sorted(
        farms_with_processors, key=lambda t: len(t[0]), reverse=True
    )
    for farm_name, processor_name in sorted_rows:
        name = _name_for_farm_match(filename)
        prefix = _farm_name_to_file_prefix(farm_name)
        stem = f"{prefix}{MILK_REPORT_SUFFIX}"
        if name.startswith(stem) and name.lower().endswith(".csv"):
            return (farm_name, processor_name)
    return None


def _dated_filename(original: str, today: datetime | None = None) -> str:
    day = today or datetime.now()
    ymd = day.strftime("%Y%m%d")
    return f"{ymd}_{original}"


def _staged_basename(path: Path, today: datetime | None = None) -> str:
    """Single yyyymmdd_ prefix: strip an existing one from the filename if present."""
    name = path.name
    if _DATED_CSV.match(name) and len(name) > 9 and name[8] == "_":
        name = name[9:]
    return _dated_filename(name, today=today)


def ensure_staging_folders() -> None:
    for name in sqlAPI.list_of_processor_names():
        (FILES_TO_DATABRICKS / name).mkdir(parents=True, exist_ok=True)
    for farm_name, processor_name in sqlAPI.get_all_farms_with_processors():
        sub = FILES_TO_DATABRICKS / processor_name / _safe_farm_dir_name(farm_name)
        sub.mkdir(parents=True, exist_ok=True)


def organize_downloads(
    dry_run: bool = False, today: datetime | None = None
) -> tuple[int, int, int]:
    """
    Returns (moved_count, skipped_count, unmatched_count).
    """
    if not DOWNLOADS.is_dir():
        print(f"Download directory not found: {DOWNLOADS}", file=sys.stderr)
        return (0, 0, 0)

    farms_with_processors = sqlAPI.get_all_farms_with_processors()
    if not farms_with_processors:
        print("No farms in database; nothing to match.", file=sys.stderr)
        return (0, 0, 0)

    if not dry_run:
        ensure_staging_folders()

    moved = 0
    skipped = 0
    unmatched = 0
    day = today or datetime.now()

    for path in sorted(DOWNLOADS.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if not path.name.lower().endswith(".csv"):
            print(f"Skipping non-CSV: {path.name}")
            continue

        match = _match_farm_and_processor(path.name, farms_with_processors)
        if not match:
            print(f"Unmatched (no farm in DB): {path.name}")
            unmatched += 1
            continue

        farm_name, processor_name = match
        dest_dir = (
            FILES_TO_DATABRICKS / processor_name / _safe_farm_dir_name(farm_name)
        )
        new_name = _staged_basename(path, today=day)
        dest = dest_dir / new_name

        if dest.exists():
            print(
                f"Skip (destination exists): {dest}",
                file=sys.stderr,
            )
            skipped += 1
            continue

        if dry_run:
            print(f"Would move: {path} -> {dest}")
            moved += 1
            continue

        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
        print(f"Moved: {path.name} -> {dest}")
        moved += 1

    return (moved, skipped, unmatched)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Move mdd_downloads CSVs into files_to_data_bricks by processor and farm."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned moves without moving files.",
    )
    args = parser.parse_args()
    moved, skipped, unmatched = organize_downloads(dry_run=args.dry_run)
    print(
        f"Done. moved={moved}, skipped_existing={skipped}, unmatched={unmatched}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
