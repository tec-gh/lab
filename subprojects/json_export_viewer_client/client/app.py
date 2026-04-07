from __future__ import annotations

import asyncio
import json
from typing import Optional

import flet as ft

from client.config import load_config
from client.loader import LoadResult, LoadedRecord, TemplateDataset, TemplateFieldDefinition, load_json_folder

SUCCESS_VALUES = {"success", "ok", "passed"}
TABLE_LIMIT = 300
LABEL_RECORD_COUNT = "\u30ec\u30b3\u30fc\u30c9\u6570"
LABEL_RECORD_SUFFIX = "\u30ec\u30b3\u30fc\u30c9"
LABEL_SEARCH_RESULTS = "\u691c\u7d22\u7d50\u679c"
LABEL_RESULT_SUFFIX = "\u4ef6"
LABEL_DISPLAY_SETTINGS = "\u8868\u793a\u9805\u76ee\u8a2d\u5b9a"
LABEL_VISIBILITY = "\u8868\u793a/\u975e\u8868\u793a\u5207\u308a\u66ff\u3048"
LABEL_SEARCH = "\u691c\u7d22"
LABEL_RELOAD = "\u4eca\u3059\u3050\u518d\u8aad\u307f\u8fbc\u307f"
LABEL_NO_DATA = "\u8868\u793a\u3067\u304d\u308b\u30c7\u30fc\u30bf\u304c\u3042\u308a\u307e\u305b\u3093\u3002"
LABEL_SUMMARY = "\u30e1\u30a4\u30f3\u30a2\u30d7\u30ea\u306b\u5408\u308f\u305b\u305f\u4e00\u89a7\u753b\u9762\u3067 JSON \u3092\u691c\u7d22\u30fb\u53c2\u7167\u3057\u307e\u3059\u3002"
LABEL_TEMPLATE = "\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8"
LABEL_TEMPLATE_FILE = "\u8aad\u307f\u8fbc\u307f\u30d5\u30a1\u30a4\u30eb"
LABEL_REFRESH = "\u66f4\u65b0\u9593\u9694"
LABEL_LAST_LOADED = "\u6700\u7d42\u8aad\u307f\u8fbc\u307f"
LABEL_SEARCH_RESULTS_TABLE = "\u691c\u7d22\u7d50\u679c"

METADATA_FIELDS = [
    ("record_id", "\u30ec\u30b3\u30fc\u30c9ID", True),
    ("received_at", "\u53d7\u4fe1\u65e5\u6642", True),
    ("source_file", "\u30d5\u30a1\u30a4\u30eb\u540d", True),
    ("source_path", "\u30d5\u30a1\u30a4\u30eb\u30d1\u30b9", False),
    ("row_index", "\u884c\u756a\u53f7", False),
    ("file_modified_at", "\u30d5\u30a1\u30a4\u30eb\u66f4\u65b0\u65e5\u6642", False),
]


def _record_value(record: LoadedRecord, field_key: str) -> str:
    value = record.values.get(field_key, "")
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _metadata_value(record: LoadedRecord, field: str) -> str:
    value = getattr(record, field, "")
    if value is None:
        return ""
    return str(value)


def _template_options(result: LoadResult) -> list[ft.dropdown.Option]:
    return [ft.dropdown.Option(key=dataset.template_name, text=dataset.template_name) for dataset in result.templates]


def _get_selected_dataset(result: LoadResult, template_name: str) -> Optional[TemplateDataset]:
    for dataset in result.templates:
        if dataset.template_name == template_name:
            return dataset
    return result.templates[0] if result.templates else None


def _visible_fields(dataset: Optional[TemplateDataset]) -> list[TemplateFieldDefinition]:
    if dataset is None:
        return []
    fields = [field for field in dataset.fields if field.is_visible]
    return fields or dataset.fields


def _searchable_text(record: LoadedRecord, dataset: Optional[TemplateDataset], metadata_keys: list[str]) -> str:
    parts: list[str] = []
    for key in metadata_keys:
        parts.append(_metadata_value(record, key))
    if dataset is not None:
        for field in dataset.fields:
            if field.is_searchable:
                parts.append(_record_value(record, field.field_key))
    parts.append(json.dumps(record.payload, ensure_ascii=False, default=str))
    return "\\n".join(parts).casefold()


def _status_chip(value: str) -> ft.Control:
    normalized = value.strip().lower()
    if not value:
        background = ft.Colors.BLUE_GREY_400
    elif normalized in SUCCESS_VALUES:
        background = ft.Colors.GREEN_600
    else:
        background = ft.Colors.RED_600
    return ft.Container(
        content=ft.Text(value or "-", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.W_600),
        bgcolor=background,
        border_radius=999,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def _build_stat_card(title: str, value: str, accent: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=14,
        padding=16,
        content=ft.Column(
            [
                ft.Text(title, size=12, color=ft.Colors.BLUE_GREY_500),
                ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=accent),
            ],
            spacing=6,
        ),
        expand=1,
    )


async def build_ui(page: ft.Page) -> None:
    config = load_config()
    page.title = config.title
    page.window_width = 1480
    page.window_height = 940
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f4f7fb"

    initial_result = load_json_folder(config.json_folder)
    initial_template = initial_result.templates[0].template_name if initial_result.templates else ""
    state: dict[str, object] = {"result": initial_result, "selected_template": initial_template}

    summary = ft.Text(size=13, color=ft.Colors.BLUE_GREY_700)
    status = ft.Text(size=13, color=ft.Colors.BLUE_GREY_500)
    search_input = ft.TextField(label=LABEL_SEARCH, hint_text="hostname / ipaddress / JSON text / metadata", expand=True)
    template_dropdown = ft.Dropdown(label=LABEL_TEMPLATE, options=_template_options(initial_result), value=initial_template, width=280)
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    stats_row = ft.Row(spacing=12)

    metadata_toggles: dict[str, ft.Checkbox] = {
        field: ft.Checkbox(label=label, value=default_value) for field, label, default_value in METADATA_FIELDS
    }

    def current_result() -> LoadResult:
        result = state["result"]
        assert isinstance(result, LoadResult)
        return result

    def current_dataset() -> Optional[TemplateDataset]:
        dataset = _get_selected_dataset(current_result(), str(state.get("selected_template") or ""))
        if dataset is not None:
            state["selected_template"] = dataset.template_name
        return dataset

    def filtered_records() -> list[LoadedRecord]:
        dataset = current_dataset()
        if dataset is None:
            return []
        query = (search_input.value or "").strip().casefold()
        metadata_keys = [key for key, _, _ in METADATA_FIELDS if metadata_toggles[key].value]
        if not query:
            return dataset.records
        return [record for record in dataset.records if query in _searchable_text(record, dataset, metadata_keys)]

    def update_table() -> None:
        result = current_result()
        dataset = current_dataset()
        records = filtered_records()
        fields = _visible_fields(dataset)

        template_dropdown.options = _template_options(result)
        template_dropdown.value = dataset.template_name if dataset else None

        summary.value = LABEL_SUMMARY
        stats_row.controls = [
            _build_stat_card(LABEL_RECORD_COUNT, f"{len(dataset.records) if dataset else 0}{LABEL_RECORD_SUFFIX}", ft.Colors.BLUE_900),
            _build_stat_card(LABEL_SEARCH_RESULTS, f"{len(records)}{LABEL_RESULT_SUFFIX}", ft.Colors.TEAL_700),
        ]

        status_parts = []
        if dataset is not None:
            status_parts.append(f"{LABEL_TEMPLATE_FILE}: {dataset.source_file}")
        status_parts.append(f"{LABEL_REFRESH}: {config.refresh_minutes}\u5206")
        status_parts.append(f"{LABEL_LAST_LOADED}: {result.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if result.error_message:
            status_parts.append(f"Error: {result.error_message}")
        status.value = " / ".join(status_parts)

        visible_metadata = [(field, label) for field, label, _ in METADATA_FIELDS if metadata_toggles[field].value]
        columns = [ft.DataColumn(ft.Text(label)) for _, label in visible_metadata]
        columns.extend(ft.DataColumn(ft.Text(field.display_name)) for field in fields)

        rows: list[ft.DataRow] = []
        for record in records[:TABLE_LIMIT]:
            cells: list[ft.DataCell] = []
            for field, _ in visible_metadata:
                cells.append(ft.DataCell(ft.Text(_metadata_value(record, field) or "-")))
            for field in fields:
                value = _record_value(record, field.field_key)
                if field.field_key in {"ping_test_result", "exec_result"}:
                    cells.append(ft.DataCell(_status_chip(value)))
                else:
                    cells.append(ft.DataCell(ft.Text(value or "-")))
            rows.append(ft.DataRow(cells=cells))

        if rows:
            table_container.controls = [
                ft.DataTable(
                    columns=columns,
                    rows=rows,
                    column_spacing=18,
                    heading_row_color=ft.Colors.BLUE_GREY_50,
                    data_row_min_height=48,
                    data_row_max_height=60,
                )
            ]
        else:
            table_container.controls = [
                ft.Container(
                    padding=20,
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Text(LABEL_NO_DATA, color=ft.Colors.BLUE_GREY_500),
                )
            ]

        page.update()

    def reload_data(*_args) -> None:
        result = load_json_folder(config.json_folder)
        state["result"] = result
        current_name = str(state.get("selected_template") or "")
        selected = _get_selected_dataset(result, current_name)
        state["selected_template"] = selected.template_name if selected else ""
        update_table()

    def on_template_change(event: ft.ControlEvent) -> None:
        state["selected_template"] = event.control.value or ""
        update_table()

    search_input.on_change = lambda _: update_table()
    template_dropdown.on_change = on_template_change
    for toggle in metadata_toggles.values():
        toggle.on_change = lambda _: update_table()

    reload_button = ft.ElevatedButton(LABEL_RELOAD, on_click=reload_data, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)

    header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=16,
        padding=20,
        content=ft.Column(
            [
                ft.Text(config.title, size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                summary,
                status,
                ft.Row([reload_button], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=8,
        ),
    )

    filter_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=16,
        padding=20,
        content=ft.Column(
            [
                ft.Text(LABEL_DISPLAY_SETTINGS, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                ft.Row([template_dropdown, search_input], wrap=True, spacing=12),
                ft.Text(LABEL_VISIBILITY, size=13, color=ft.Colors.BLUE_GREY_600),
                ft.Row(list(metadata_toggles.values()), wrap=True, spacing=12, run_spacing=8),
            ],
            spacing=14,
        ),
    )

    records_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=16,
        padding=20,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(LABEL_SEARCH_RESULTS_TABLE, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                        ft.Container(
                            content=ft.Text(f"Up to {TABLE_LIMIT} rows", color=ft.Colors.WHITE, size=12),
                            bgcolor=ft.Colors.BLUE_GREY_600,
                            border_radius=999,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                table_container,
            ],
            spacing=14,
        ),
        expand=True,
    )

    page.add(header, stats_row, filter_card, records_card)
    update_table()

    async def periodic_reload() -> None:
        while True:
            await asyncio.sleep(config.refresh_minutes * 60)
            reload_data()

    page.run_task(periodic_reload)



def run() -> None:
    config = load_config()
    view = ft.AppView.WEB_BROWSER if config.mode == "web" else ft.AppView.FLET_APP
    ft.app(target=build_ui, view=view, port=config.web_port if config.mode == "web" else 0)
