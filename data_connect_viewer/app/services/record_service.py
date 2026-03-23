import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.record import Record
from app.repositories.record_repository import (
    create_record,
    get_record_by_hostname,
    get_record_by_id,
    list_records,
    list_records_for_export,
)
from app.services.mapping_service import MappingExtractor, get_active_mapping_config

UPDATE_POLICY_FILL_IF_EMPTY = "fill_if_empty"
UPDATE_POLICY_OVERWRITE = "overwrite"
UPDATE_POLICY_SKIP = "skip"

# Change this map when field-level update rules need to be adjusted.
FIELD_UPDATE_POLICIES = {
    "hostname": UPDATE_POLICY_SKIP,
    "ipaddress": UPDATE_POLICY_FILL_IF_EMPTY,
    "area": UPDATE_POLICY_FILL_IF_EMPTY,
    "building": UPDATE_POLICY_FILL_IF_EMPTY,
    "category": UPDATE_POLICY_FILL_IF_EMPTY,
    "model": UPDATE_POLICY_FILL_IF_EMPTY,
    "ping_test_result": UPDATE_POLICY_OVERWRITE,
    "exec_result": UPDATE_POLICY_OVERWRITE,
}


def is_empty_value(value: Optional[str]) -> bool:
    return value is None or value == ""



def apply_field_update_policy(record: Record, extracted: Dict[str, Optional[str]]) -> None:
    for field_name, new_value in extracted.items():
        policy = FIELD_UPDATE_POLICIES.get(field_name, UPDATE_POLICY_OVERWRITE)
        current_value = getattr(record, field_name)

        if policy == UPDATE_POLICY_SKIP:
            continue
        if policy == UPDATE_POLICY_FILL_IF_EMPTY:
            if is_empty_value(current_value) and not is_empty_value(new_value):
                setattr(record, field_name, new_value)
            continue
        if policy == UPDATE_POLICY_OVERWRITE:
            setattr(record, field_name, new_value)



def create_record_from_payload(session: Session, payload: Dict[str, Any]) -> Tuple[Record, bool]:
    _, mapping_dict, version = get_active_mapping_config(session)
    extractor = MappingExtractor()
    extracted = extractor.extract(payload, mapping_dict)
    received_at = datetime.utcnow()
    hostname = extracted.get("hostname")

    if hostname:
        existing_record = get_record_by_hostname(session, hostname)
        if existing_record:
            apply_field_update_policy(existing_record, extracted)
            existing_record.payload_json = json.dumps(payload, ensure_ascii=False)
            existing_record.mapping_version = version
            existing_record.received_at = received_at
            session.flush()
            return existing_record, False

    record = Record(
        **extracted,
        payload_json=json.dumps(payload, ensure_ascii=False),
        mapping_version=version,
        received_at=received_at,
    )
    return create_record(session, record), True



def get_record_detail(session: Session, record_id: int) -> Tuple[Optional[Record], Optional[Dict[str, Any]]]:
    record = get_record_by_id(session, record_id)
    if not record:
        return None, None
    return record, MappingExtractor.load_payload(record.payload_json)



def search_records(session: Session, filters: dict, page: int, page_size: int):
    return list_records(session, filters, page, page_size)



def export_records(session: Session, filters: dict, limit: int):
    return list_records_for_export(session, filters, limit)
