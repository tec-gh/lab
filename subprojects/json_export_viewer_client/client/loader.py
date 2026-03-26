from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class LoadedRecord:
    source_file: str
    source_path: str
    row_index: int
    file_modified_at: str
    item: dict[str, Any]


@dataclass
class LoadResult:
    files: list[Path]
    records: list[LoadedRecord]
    loaded_at: datetime
    error_message: str = ""


def _format_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_records(data: Any, source_file: Path) -> list[LoadedRecord]:
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        items = [{"value": data}]

    records: list[LoadedRecord] = []
    modified_at = _format_timestamp(source_file)
    for index, item in enumerate(items, start=1):
        record = item if isinstance(item, dict) else {"value": item}
        records.append(
            LoadedRecord(
                source_file=source_file.name,
                source_path=str(source_file.resolve()),
                row_index=index,
                file_modified_at=modified_at,
                item=record,
            )
        )
    return records


def load_json_folder(folder: Path) -> LoadResult:
    loaded_at = datetime.now()
    if not folder.exists():
        return LoadResult(files=[], records=[], loaded_at=loaded_at, error_message=f"Folder not found: {folder}")

    files = sorted(folder.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    records: list[LoadedRecord] = []
    for file_path in files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return LoadResult(files=files, records=records, loaded_at=loaded_at, error_message=f"{file_path.name}: {exc}")
        records.extend(_normalize_records(data, file_path))

    return LoadResult(files=files, records=records, loaded_at=loaded_at)
