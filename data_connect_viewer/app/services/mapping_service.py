import json
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.field_mapping_repository import get_active_mappings, replace_active_mappings
from app.schemas.field_mapping import FieldMappingUpdateItem


DEFAULT_FIELDS = [
    ("hostname", "Hostname"),
    ("ipaddress", "IP Address"),
    ("area", "Area"),
    ("building", "Building"),
    ("category", "Category"),
    ("model", "Model"),
    ("ping_test_result", "Ping Test Result"),
    ("exec_result", "Exec Result"),
]


class MappingExtractor:
    @staticmethod
    def load_payload(payload_json: str) -> dict[str, Any]:
        loaded = json.loads(payload_json)
        return loaded if isinstance(loaded, dict) else {"value": loaded}

    @staticmethod
    def get_value_by_path(payload: dict[str, Any], path: str) -> str | None:
        current: Any = payload
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        if current is None:
            return None
        if isinstance(current, (dict, list)):
            return json.dumps(current, ensure_ascii=False)
        return str(current)

    def extract(self, payload: dict[str, Any], mappings: dict[str, str]) -> dict[str, str | None]:
        return {field_key: self.get_value_by_path(payload, path) for field_key, path in mappings.items()}


def ensure_default_mappings(session: Session) -> None:
    if get_active_mappings(session):
        return
    replace_active_mappings(
        session,
        [
            FieldMappingUpdateItem(
                field_key=field_key,
                display_name=display_name,
                json_path=field_key,
                is_visible=True,
                is_searchable=True,
                is_exportable=True,
                sort_order=index,
            )
            for index, (field_key, display_name) in enumerate(DEFAULT_FIELDS, start=1)
        ],
        changed_by="system",
        change_summary="Initial default mappings",
    )


def get_active_mapping_config(session: Session) -> tuple[list, dict[str, str], int]:
    mappings = get_active_mappings(session)
    version = max((item.version for item in mappings), default=1)
    return mappings, {item.field_key: item.json_path for item in mappings}, version
