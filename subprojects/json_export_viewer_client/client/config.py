from __future__ import annotations

import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    mode: str
    title: str
    refresh_minutes: int
    json_folder: Path
    web_port: int
    config_path: Path
    app_root: Path


def get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def get_default_config_path() -> Path:
    return get_app_root() / "config.ini"


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    path = (config_path or get_default_config_path()).resolve()
    parser = ConfigParser()
    parser.read(path, encoding="utf-8")

    mode = parser.get("app", "mode", fallback="native").strip().lower()
    if mode not in {"native", "web"}:
        mode = "native"

    refresh_minutes = max(1, parser.getint("app", "refresh_minutes", fallback=5))
    web_port = parser.getint("app", "web_port", fallback=8550)
    if web_port < 1 or web_port > 65535:
        web_port = 8550

    json_folder = Path(parser.get("app", "json_folder", fallback="./sample_data")).expanduser()
    if not json_folder.is_absolute():
        json_folder = (path.parent / json_folder).resolve()

    return AppConfig(
        mode=mode,
        title=parser.get("app", "title", fallback="JSON Export Viewer").strip() or "JSON Export Viewer",
        refresh_minutes=refresh_minutes,
        json_folder=json_folder,
        web_port=web_port,
        config_path=path,
        app_root=get_app_root(),
    )
