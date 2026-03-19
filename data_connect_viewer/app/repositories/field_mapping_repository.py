from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.field_mapping import FieldMapping
from app.models.setting_history import SettingHistory
from app.schemas.field_mapping import FieldMappingUpdateItem


def get_active_mappings(session: Session) -> list[FieldMapping]:
    stmt = (
        select(FieldMapping)
        .where(FieldMapping.is_active.is_(True))
        .order_by(FieldMapping.sort_order.asc(), FieldMapping.id.asc())
    )
    return list(session.scalars(stmt).all())


def get_current_version(session: Session) -> int:
    active = get_active_mappings(session)
    return max((item.version for item in active), default=0)


def replace_active_mappings(
    session: Session, mappings: list[FieldMappingUpdateItem], changed_by: str | None, change_summary: str | None
) -> int:
    new_version = get_current_version(session) + 1
    session.execute(update(FieldMapping).where(FieldMapping.is_active.is_(True)).values(is_active=False))
    for item in mappings:
        session.add(
            FieldMapping(
                field_key=item.field_key,
                display_name=item.display_name,
                json_path=item.json_path,
                is_visible=item.is_visible,
                is_searchable=item.is_searchable,
                is_exportable=item.is_exportable,
                sort_order=item.sort_order,
                version=new_version,
                is_active=True,
            )
        )
    session.add(
        SettingHistory(
            setting_type="field_mappings",
            version=new_version,
            changed_by=changed_by,
            change_summary=change_summary,
        )
    )
    session.flush()
    return new_version
