from collections.abc import Sequence

from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from app.models.record import Record


SEARCHABLE_COLUMNS = (
    "hostname",
    "ipaddress",
    "area",
    "building",
    "category",
    "model",
    "ping_test_result",
    "exec_result",
)


def create_record(session: Session, record: Record) -> Record:
    session.add(record)
    session.flush()
    return record


def get_record_by_id(session: Session, record_id: int) -> Record | None:
    return session.get(Record, record_id)


def build_record_filters(filters: dict) -> list:
    conditions = []
    for field in SEARCHABLE_COLUMNS:
        value = filters.get(field)
        if value:
            conditions.append(cast(getattr(Record, field), String).ilike(f"%{value}%"))
    if filters.get("keyword"):
        conditions.append(Record.payload_json.ilike(f"%{filters['keyword']}%"))
    if filters.get("date_from"):
        conditions.append(Record.received_at >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(Record.received_at <= filters["date_to"])
    return conditions


def list_records(session: Session, filters: dict, page: int, page_size: int) -> tuple[Sequence[Record], int]:
    conditions = build_record_filters(filters)
    stmt = select(Record)
    count_stmt = select(func.count(Record.id))
    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)
    stmt = stmt.order_by(Record.received_at.desc(), Record.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    return list(session.scalars(stmt).all()), int(session.scalar(count_stmt) or 0)


def list_records_for_export(session: Session, filters: dict, limit: int) -> Sequence[Record]:
    conditions = build_record_filters(filters)
    stmt = select(Record)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.order_by(Record.received_at.desc(), Record.id.desc()).limit(limit)
    return list(session.scalars(stmt).all())


def resync_records(session: Session, extractor, mappings: dict[str, str], version: int) -> int:
    records = list(session.scalars(select(Record)).all())
    for record in records:
        payload = extractor.load_payload(record.payload_json)
        extracted = extractor.extract(payload, mappings)
        for key, value in extracted.items():
            setattr(record, key, value)
        record.mapping_version = version
    session.flush()
    return len(records)
