from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TemplateFieldDefinition:
    field_key: str
    display_name: str
    json_path: str = ""
    is_visible: bool = True
    is_searchable: bool = True
    is_exportable: bool = True
    update_mode: str = "overwrite"
    sort_order: int = 0


@dataclass
class LoadedRecord:
    source_file: str
    source_path: str
    row_index: int
    file_modified_at: str
    record_id: str
    received_at: str
    values: dict[str, Any]
    payload: dict[str, Any]


@dataclass
class TemplateDataset:
    template_name: str
    api_name: str
    unique_key_field: str
    fields: list[TemplateFieldDefinition]
    records: list[LoadedRecord]
    source_file: str
    source_path: str
    file_modified_at: str


@dataclass
class LoadResult:
    files: list[Path]
    templates: list[TemplateDataset]
    loaded_at: datetime
    error_message: str = ""


def _format_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _coerce_display_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _infer_fields(items: list[dict[str, Any]]) -> list[TemplateFieldDefinition]:
    seen: list[str] = []
    for item in items:
        for key in item.keys():
            if key not in seen:
                seen.append(key)
    return [
        TemplateFieldDefinition(
            field_key=key,
            display_name=key,
            json_path=key,
            is_visible=True,
            is_searchable=True,
            is_exportable=True,
            update_mode="overwrite",
            sort_order=index + 1,
        )
        for index, key in enumerate(seen)
    ]


def _normalize_fields(raw_fields: Any, records: list[dict[str, Any]]) -> list[TemplateFieldDefinition]:
    if not isinstance(raw_fields, list):
        return _infer_fields(records)

    normalized: list[TemplateFieldDefinition] = []
    for index, item in enumerate(raw_fields):
        if not isinstance(item, dict):
            continue
        normalized.append(
            TemplateFieldDefinition(
                field_key=str(item.get("field_key") or "").strip(),
                display_name=str(item.get("display_name") or item.get("field_key") or "").strip(),
                json_path=str(item.get("json_path") or item.get("field_key") or "").strip(),
                is_visible=bool(item.get("is_visible", True)),
                is_searchable=bool(item.get("is_searchable", True)),
                is_exportable=bool(item.get("is_exportable", True)),
                update_mode=str(item.get("update_mode") or "overwrite"),
                sort_order=int(item.get("sort_order", index + 1)),
            )
        )
    return [field for field in normalized if field.field_key] or _infer_fields(records)


def _normalize_record_item(item: Any, source_file: Path, row_index: int) -> LoadedRecord:
    modified_at = _format_timestamp(source_file)
    record = item if isinstance(item, dict) else {"value": item}
    values = record.get("values") if isinstance(record.get("values"), dict) else record
    payload = record.get("payload") if isinstance(record.get("payload"), dict) else record
    return LoadedRecord(
        source_file=source_file.name,
        source_path=str(source_file.resolve()),
        row_index=row_index,
        file_modified_at=modified_at,
        record_id=str(record.get("id") or ""),
        received_at=str(record.get("received_at") or ""),
        values={key: _coerce_display_value(value) for key, value in dict(values).items()},
        payload=dict(payload),
    )


def _normalize_template_dataset(data: Any, source_file: Path) -> TemplateDataset:
    modified_at = _format_timestamp(source_file)

    if isinstance(data, dict) and isinstance(data.get("records"), list):
        raw_records = data.get("records") or []
        records = [_normalize_record_item(item, source_file, index) for index, item in enumerate(raw_records, start=1)]
        normalized_values = [record.values for record in records]
        fields = _normalize_fields(data.get("fields"), normalized_values)
        return TemplateDataset(
            template_name=str(data.get("template_name") or source_file.stem),
            api_name=str(data.get("api_name") or data.get("template_name") or source_file.stem),
            unique_key_field=str(data.get("unique_key_field") or "hostname"),
            fields=sorted(fields, key=lambda item: (item.sort_order, item.field_key)),
            records=records,
            source_file=source_file.name,
            source_path=str(source_file.resolve()),
            file_modified_at=modified_at,
        )

    if isinstance(data, list):
        items = [item if isinstance(item, dict) else {"value": item} for item in data]
    elif isinstance(data, dict):
        items = [data]
    else:
        items = [{"value": data}]

    fields = _infer_fields(items)
    records = [_normalize_record_item(item, source_file, index) for index, item in enumerate(items, start=1)]
    return TemplateDataset(
        template_name=source_file.stem,
        api_name=source_file.stem,
        unique_key_field="hostname",
        fields=fields,
        records=records,
        source_file=source_file.name,
        source_path=str(source_file.resolve()),
        file_modified_at=modified_at,
    )


def load_json_folder(folder: Path) -> LoadResult:
    loaded_at = datetime.now()
    if not folder.exists():
        return LoadResult(files=[], templates=[], loaded_at=loaded_at, error_message=f"Folder not found: {folder}")

    files = sorted(folder.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    templates: list[TemplateDataset] = []
    for file_path in files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            templates.append(_normalize_template_dataset(data, file_path))
        except Exception as exc:
            return LoadResult(files=files, templates=templates, loaded_at=loaded_at, error_message=f"{file_path.name}: {exc}")

    return LoadResult(files=files, templates=templates, loaded_at=loaded_at)
