from __future__ import annotations

import asyncio
import json

import flet as ft

from client.config import AppConfig, load_config
from client.loader import LoadResult, LoadedRecord, load_json_folder


DISPLAY_FIELDS = [
    "id",
    "hostname",
    "ipaddress",
    "area",
    "building",
    "category",
    "model",
    "ping_test_result",
    "exec_result",
    "received_at",
]


def _record_value(record: LoadedRecord, field: str) -> str:
    value = record.item.get(field, "")
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _summary_text(config: AppConfig, result: LoadResult) -> str:
    latest_file = result.files[0].name if result.files else "-"
    return (
        f"モード: {config.mode} / 監視フォルダ: {config.json_folder} / "
        f"更新間隔: {config.refresh_minutes}分 / ファイル数: {len(result.files)} / "
        f"レコード数: {len(result.records)} / 最新ファイル: {latest_file}"
    )


async def build_ui(page: ft.Page) -> None:
    config = load_config()
    page.title = config.title
    page.window_width = 1440
    page.window_height = 920
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    summary = ft.Text(size=14, color=ft.Colors.BLUE_GREY_700)
    status = ft.Text(size=13, color=ft.Colors.BLUE_GREY_500)
    config_info = ft.Text(
        value=f"設定ファイル: {config.config_path}",
        size=12,
        color=ft.Colors.BLUE_GREY_400,
    )
    json_detail = ft.TextField(
        label="選択レコード詳細",
        multiline=True,
        min_lines=14,
        max_lines=24,
        read_only=True,
        value="レコードを選択してください。",
    )
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def update_table(result: LoadResult) -> None:
        rows: list[ft.DataRow] = []
        for record in result.records[:500]:
            cells = [ft.DataCell(ft.Text(record.source_file))]
            cells.extend(ft.DataCell(ft.Text(_record_value(record, field))) for field in DISPLAY_FIELDS)
            rows.append(
                ft.DataRow(
                    cells=cells,
                    on_select_changed=lambda e, current=record: show_detail(current),
                )
            )

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("source_file"))]
            + [ft.DataColumn(ft.Text(field)) for field in DISPLAY_FIELDS],
            rows=rows,
            column_spacing=18,
            heading_row_color=ft.Colors.BLUE_GREY_50,
        )
        table_container.controls = [table] if rows else [ft.Text("表示できるデータがありません。")]

    def show_detail(record: LoadedRecord) -> None:
        json_detail.value = json.dumps(record.item, ensure_ascii=False, indent=2, default=str)
        page.update()

    def reload_data() -> None:
        result = load_json_folder(config.json_folder)
        summary.value = _summary_text(config, result)
        status.value = f"最終読み込み: {result.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
        if result.error_message:
            status.value += f" / エラー: {result.error_message}"
        update_table(result)
        if result.records:
            if json_detail.value == "レコードを選択してください。":
                show_detail(result.records[0])
            else:
                page.update()
        else:
            json_detail.value = "レコードを選択してください。"
            page.update()

    reload_button = ft.ElevatedButton("今すぐ再読み込み", on_click=lambda _: reload_data())
    header = ft.Container(
        content=ft.Column(
            [
                ft.Text(config.title, size=28, weight=ft.FontWeight.BOLD),
                summary,
                status,
                config_info,
                reload_button,
            ],
            spacing=8,
        ),
        padding=ft.padding.only(bottom=12),
    )

    page.add(
        header,
        ft.Container(content=table_container, expand=True),
        json_detail,
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
