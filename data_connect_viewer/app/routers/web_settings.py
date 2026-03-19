from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.core.config import settings
from app.core.database import get_db
from app.repositories.field_mapping_repository import get_active_mappings, replace_active_mappings
from app.repositories.record_repository import resync_records
from app.schemas.field_mapping import FieldMappingUpdateItem
from app.services.app_setting_service import get_sftp_settings, save_sftp_settings
from app.services.mapping_service import MappingExtractor

router = APIRouter(tags=["settings"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings/mappings")
def mappings_page(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return templates.TemplateResponse(
        request,
        "settings_mappings.html",
        {
            "app_name": settings.app_name,
            "mappings": get_active_mappings(db),
            "sftp_settings": get_sftp_settings(db),
        },
    )


@router.post("/settings/mappings/save")
async def save_mappings(request: Request, db: Session = Depends(get_db), username: str = Depends(require_admin)):
    form = await request.form()
    current = get_active_mappings(db)
    mappings: list[FieldMappingUpdateItem] = []
    for item in current:
        field_key = item.field_key
        mappings.append(
            FieldMappingUpdateItem(
                field_key=field_key,
                display_name=str(form.get(f"display_name_{field_key}", item.display_name)),
                json_path=str(form.get(f"json_path_{field_key}", item.json_path)),
                is_visible=form.get(f"is_visible_{field_key}") == "on",
                is_searchable=form.get(f"is_searchable_{field_key}") == "on",
                is_exportable=form.get(f"is_exportable_{field_key}") == "on",
                sort_order=int(form.get(f"sort_order_{field_key}", item.sort_order)),
            )
        )
    replace_active_mappings(
        db,
        mappings,
        changed_by=username,
        change_summary=str(form.get("change_summary") or "Updated from UI"),
    )
    db.commit()
    return RedirectResponse(url="/settings/mappings", status_code=303)


@router.post("/settings/mappings/resync")
def run_resync(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    active = get_active_mappings(db)
    mapping_dict = {item.field_key: item.json_path for item in active}
    version = max((item.version for item in active), default=1)
    extractor = MappingExtractor()
    resync_records(db, extractor, mapping_dict, version)
    db.commit()
    return RedirectResponse(url="/settings/mappings", status_code=303)


@router.post("/settings/sftp/save")
async def save_sftp_settings_route(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    form = await request.form()
    values = {
        "sftp_host": str(form.get("sftp_host", "")).strip(),
        "sftp_username": str(form.get("sftp_username", "")).strip(),
        "sftp_password": str(form.get("sftp_password", "")).strip(),
        "sftp_frequency_minutes": str(form.get("sftp_frequency_minutes", settings.sftp_frequency_minutes)).strip(),
    }
    save_sftp_settings(db, values)
    db.commit()
    return RedirectResponse(url="/settings/mappings", status_code=303)
