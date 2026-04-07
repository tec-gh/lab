import json
from typing import Optional

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.core.config import settings
from app.core.database import get_db
from app.repositories.template_repository import get_template_by_name, list_templates, upsert_template
from app.services.app_setting_service import get_sftp_settings, save_sftp_settings
from app.services.mapping_service import dump_template_spec, get_selected_template, load_template_spec
from app.services.record_service import resync_records

router = APIRouter(tags=["settings"])
templates = Jinja2Templates(directory="app/templates")


# テンプレート設定画面の初期表示。
@router.get("/settings/mappings")
def mappings_page(request: Request, template_name: Optional[str] = None, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    available_templates = list_templates(db)
    selected_template = get_selected_template(db, template_name)
    return templates.TemplateResponse(
        request,
        "settings_mappings.html",
        {
            "app_name": settings.app_name,
            "available_templates": available_templates,
            "selected_template": selected_template,
            "fields": sorted(selected_template.fields, key=lambda item: (item.sort_order, item.id)) if selected_template else [],
            "sftp_settings": get_sftp_settings(db),
        },
    )


# 管理画面からテンプレート JSON をアップロードする。
@router.post("/settings/templates/upload")
async def upload_template(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    form = await request.form()
    upload = form.get("template_file")
    if not isinstance(upload, UploadFile):
        return RedirectResponse(url="/settings/mappings", status_code=303)
    spec = load_template_spec(await upload.read())
    template = upsert_template(db, dump_template_spec(spec))
    db.commit()
    return RedirectResponse(url=f"/settings/mappings?template_name={template.template_name}", status_code=303)


# 画面上で編集したテンプレート設定を保存する。
@router.post("/settings/mappings/save")
async def save_mappings(request: Request, db: Session = Depends(get_db), username: str = Depends(require_admin)):
    form = await request.form()
    template_name = str(form.get("template_name") or "")
    template = get_template_by_name(db, template_name)
    if template is None:
        return RedirectResponse(url="/settings/mappings", status_code=303)

    spec = {
        "template_name": str(form.get("template_name_value") or template.template_name),
        "api_name": str(form.get("api_name") or template.api_name),
        "unique_key_field": str(form.get("unique_key_field") or template.unique_key_field),
        "external_api": {
            "enabled": form.get("external_api_enabled") == "on",
            "url": str(form.get("external_api_url") or ""),
            "headers": json.loads(str(form.get("external_api_headers_json") or "{}")),
            "body": json.loads(str(form.get("external_api_body_json") or "{}")),
        },
        "fields": [],
    }
    for item in sorted(template.fields, key=lambda row: (row.sort_order, row.id)):
        field_key = item.field_key
        spec["fields"].append(
            {
                "field_key": field_key,
                "display_name": str(form.get(f"display_name_{field_key}", item.display_name)),
                "json_path": str(form.get(f"json_path_{field_key}", item.json_path)),
                "is_visible": form.get(f"is_visible_{field_key}") == "on",
                "is_searchable": form.get(f"is_searchable_{field_key}") == "on",
                "is_exportable": form.get(f"is_exportable_{field_key}") == "on",
                "update_mode": "overwrite" if form.get(f"update_mode_{field_key}") == "on" else "skip",
                "sort_order": int(form.get(f"sort_order_{field_key}", item.sort_order)),
            }
        )

    updated = upsert_template(db, spec)
    db.commit()
    return RedirectResponse(url=f"/settings/mappings?template_name={updated.template_name}", status_code=303)


# 保存済み payload から正規化データを再生成する管理操作。
@router.post("/settings/mappings/resync")
def run_resync(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    template_name = request.query_params.get("template_name")
    template = get_selected_template(db, template_name)
    if template is not None:
        resync_records(db, template)
        db.commit()
        return RedirectResponse(url=f"/settings/mappings?template_name={template.template_name}", status_code=303)
    return RedirectResponse(url="/settings/mappings", status_code=303)


# SFTP 接続先や転送先パスを保存する。
@router.post("/settings/sftp/save")
async def save_sftp_settings_route(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    form = await request.form()
    values = {
        "sftp_host": str(form.get("sftp_host", "")).strip(),
        "sftp_username": str(form.get("sftp_username", "")).strip(),
        "sftp_password": str(form.get("sftp_password", "")).strip(),
        "sftp_frequency_minutes": str(form.get("sftp_frequency_minutes", settings.sftp_frequency_minutes)).strip(),
        "sftp_remote_path": str(form.get("sftp_remote_path", settings.sftp_remote_path or settings.sftp_remote_filename)).strip(),
    }
    save_sftp_settings(db, values)
    db.commit()
    template_name = str(form.get("template_name") or "")
    suffix = f"?template_name={template_name}" if template_name else ""
    return RedirectResponse(url=f"/settings/mappings{suffix}", status_code=303)
