from __future__ import annotations

import asyncio
import json
from typing import Iterable

import flet as ft

from client.config import AppConfig, load_config
from client.loader import LoadResult, LoadedRecord, load_json_folder


DISPLAY_FIELDS = [
    ("id", "ID"),
    ("hostname", "Hostname"),
    ("ipaddress", "IP Address"),
    ("area", "Area"),
    ("building", "Building"),
    ("category", "Category"),
    ("model", "Model"),
    ("ping_test_result", "Ping Test Result"),
    ("exec_result", "Exec Result"),
    ("received_at", "Received At"),
]

METADATA_FIELDS = [
    ("source_file", "Source File"),
    ("source_path", "Source Path"),
    ("row_index", "Row Index"),
    ("file_modified_at", "File Modified At"),
]

SUCCESS_VALUES = {"success", "ok", "passed"}
TABLE_LIMIT = 300


def _record_key(record: LoadedRecord) -> str:
    return f"{record.source_path}:{record.row_index}"


def _record_value(record: LoadedRecord, field: str) -> str:
    value = record.item.get(field, "")
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _metadata_value(record: LoadedRecord, field: str) -> str:
    return str(getattr(record, field, "") or "")


def _summary_text(config: AppConfig, result: LoadResult, filtered_count: int) -> str:
    latest_file = result.files[0].name if result.files else "-"
    return (
        f"Mode: {config.mode} / Folder: {config.json_folder} / Refresh: {config.refresh_minutes} min / "
        f"JSON files: {len(result.files)} / Loaded records: {len(result.records)} / Visible records: {filtered_count} / Latest file: {latest_file}"
    )


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


def _matches_search(record: LoadedRecord, query: str) -> bool:
    normalized = query.strip().casefold()
    if not normalized:
        return True

    haystack: list[str] = [
        record.source_file,
        record.source_path,
        str(record.row_index),
        record.file_modified_at,
        json.dumps(record.item, ensure_ascii=False, default=str),
    ]
    haystack.extend(_record_value(record, field_key) for field_key, _ in DISPLAY_FIELDS)
    return normalized in "\n".join(haystack).casefold()


async def build_ui(page: ft.Page) -> None:
    config = load_config()
    page.title = config.title
    page.window_width = 1480
    page.window_height = 940
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f4f7fb"

    state: dict[str, object] = {
        "result": LoadResult(files=[], records=[], loaded_at=load_json_folder(config.json_folder).loaded_at),
        "selected_key": None,
    }

    summary = ft.Text(size=13, color=ft.Colors.BLUE_GREY_700)
    status = ft.Text(size=13, color=ft.Colors.BLUE_GREY_500)
    search_input = ft.TextField(label="Search", hint_text="Search hostname, ipaddress, JSON text, or file metadata", expand=True)
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    detail_meta = ft.Column(spacing=8)
    detail_json = ft.TextField(
        label="JSON Detail",
        multiline=True,
        min_lines=14,
        max_lines=26,
        read_only=True,
        value="Select a record to view details.",
    )
    stats_row = ft.Row(spacing=12)

    metadata_toggles: dict[str, ft.Checkbox] = {
        field: ft.Checkbox(label=label, value=(field in {"source_file", "row_index"}))
        for field, label in METADATA_FIELDS
    }

    def filtered_records() -> list[LoadedRecord]:
        result = state["result"]
        assert isinstance(result, LoadResult)
        return [record for record in result.records if _matches_search(record, search_input.value or "")]

    def find_record(records: Iterable[LoadedRecord], record_key: str | None) -> LoadedRecord | None:
        if not record_key:
            return None
        for record in records:
            if _record_key(record) == record_key:
                return record
        return None

    def show_detail(record: LoadedRecord | None, *, should_update: bool = True) -> None:
        detail_meta.controls.clear()
        if record is None:
            detail_json.value = "Select a record to view details."
            if should_update:
                page.update()
            return

        state["selected_key"] = _record_key(record)
        for field, label in METADATA_FIELDS:
            toggle = metadata_toggles[field]
            if toggle.value:
                detail_meta.controls.append(
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                        content=ft.Column(
                            [
                                ft.Text(label, size=11, color=ft.Colors.BLUE_GREY_500),
                                ft.Text(_metadata_value(record, field) or "-", size=13, color=ft.Colors.BLUE_GREY_900),
                            ],
                            spacing=4,
                        ),
                    )
                )

        detail_json.value = json.dumps(record.item, ensure_ascii=False, indent=2, default=str)
        if should_update:
            page.update()

    def update_table() -> None:
        records = filtered_records()
        result = state["result"]
        assert isinstance(result, LoadResult)

        summary.value = _summary_text(config, result, len(records))
        stats_row.controls = [
            _build_stat_card("JSON Files", str(len(result.files)), ft.Colors.BLUE_700),
            _build_stat_card("Loaded Records", str(len(result.records)), ft.Colors.BLUE_900),
            _build_stat_card("Search Results", str(len(records)), ft.Colors.TEAL_700),
        ]
        status.value = f"Last loaded: {result.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
        if result.error_message:
            status.value += f" / Error: {result.error_message}"

        rows: list[ft.DataRow] = []
        visible_metadata = [(field, label) for field, label in METADATA_FIELDS if metadata_toggles[field].value]
        for record in records[:TABLE_LIMIT]:
            cells: list[ft.DataCell] = []
            for field, _ in visible_metadata:
                cells.append(ft.DataCell(ft.Text(_metadata_value(record, field) or "-")))
            for field_key, _ in DISPLAY_FIELDS:
                value = _record_value(record, field_key)
                if field_key in {"ping_test_result", "exec_result"}:
                    cells.append(ft.DataCell(_status_chip(value)))
                else:
                    cells.append(ft.DataCell(ft.Text(value or "-")))
            cells.append(
                ft.DataCell(
                    ft.TextButton(
                        "Detail",
                        on_click=lambda _, current=record: show_detail(current),
                    )
                )
            )
            rows.append(ft.DataRow(cells=cells))

        columns = [ft.DataColumn(ft.Text(label)) for _, label in visible_metadata]
        columns.extend(ft.DataColumn(ft.Text(label)) for _, label in DISPLAY_FIELDS)
        columns.append(ft.DataColumn(ft.Text("")))

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
                    content=ft.Text("No records available.", color=ft.Colors.BLUE_GREY_500),
                )
            ]

        selected = find_record(records, state.get("selected_key"))
        if selected is None:
            selected = records[0] if records else None
        show_detail(selected, should_update=False)
        page.update()

    def reload_data(*_args) -> None:
        previous_selected = state.get("selected_key")
        result = load_json_folder(config.json_folder)
        state["result"] = result
        state["selected_key"] = previous_selected
        update_table()

    search_input.on_change = lambda _: update_table()
    for toggle in metadata_toggles.values():
        toggle.on_change = lambda _: update_table()

    reload_button = ft.ElevatedButton("Reload Now", on_click=reload_data, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)

    header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=16,
        padding=20,
        content=ft.Column(
            [
                ft.Text(config.title, size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                ft.Text("View JSON export files with a layout aligned to the main application.", color=ft.Colors.BLUE_GREY_600),
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
                ft.Text("Search and Display Settings", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                search_input,
                ft.Text("Metadata visibility", size=13, color=ft.Colors.BLUE_GREY_600),
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
                        ft.Text("Search Results", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                        ft.Container(
                            content=ft.Text("Up to 300 rows", color=ft.Colors.WHITE, size=12),
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

    detail_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=16,
        padding=20,
        content=ft.Column(
            [
                ft.Text("Detail", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                detail_meta,
                detail_json,
            ],
            spacing=14,
        ),
    )

    page.add(
        header,
        stats_row,
        filter_card,
        records_card,
        detail_card,
    )

    reload_data()

    async def periodic_reload() -> None:
        while True:
            await asyncio.sleep(config.refresh_minutes * 60)
            reload_data()

    page.run_task(periodic_reload)



def run() -> None:
    config = load_config()
    view = ft.AppView.WEB_BROWSER if config.mode == "web" else ft.AppView.FLET_APP
    ft.app(target=build_ui, view=view, port=config.web_port if config.mode == "web" else 0)
