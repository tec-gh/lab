import json
from datetime import datetime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.repositories.field_mapping_repository import get_active_mappings
from app.services.record_service import get_record_detail, search_records

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


def build_filters(request: Request) -> dict:
    values = {}
    for field in [
        "hostname",
        "ipaddress",
        "area",
        "building",
        "category",
        "model",
        "ping_test_result",
        "exec_result",
        "keyword",
    ]:
        values[field] = request.query_params.get(field) or None
    for field in ["date_from", "date_to"]:
        raw = request.query_params.get(field)
        values[field] = datetime.fromisoformat(raw) if raw else None
    return values


def build_query_without_paging(request: Request) -> str:
    params = [(key, value) for key, value in request.query_params.multi_items() if key not in {"page", "page_size"}]
    return urlencode(params)


@router.get("/")
def root():
    return RedirectResponse(url="/records")


@router.get("/records")
def records_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.page_size_default, ge=1, le=200),
    db: Session = Depends(get_db),
):
    filters = build_filters(request)
    records, total = search_records(db, filters, page, page_size)
    mappings = get_active_mappings(db)
    display_filters = {}
    for key, value in filters.items():
        if isinstance(value, datetime):
            display_filters[key] = value.strftime("%Y-%m-%dT%H:%M")
        else:
            display_filters[key] = value or ""
    return templates.TemplateResponse(
        request,
        "records.html",
        {
            "app_name": settings.app_name,
            "records": records,
            "mappings": mappings,
            "filters": display_filters,
            "query_without_paging": build_query_without_paging(request),
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_prev": page > 1,
            "has_next": page * page_size < total,
            "auto_refresh_seconds": 30,
        },
    )


@router.get("/records/{record_id}")
def record_detail_page(request: Request, record_id: int, db: Session = Depends(get_db)):
    record, payload = get_record_detail(db, record_id)
    return templates.TemplateResponse(
        request,
        "record_detail.html",
        {
            "app_name": settings.app_name,
            "record": record,
            "payload_pretty": json.dumps(payload or {}, ensure_ascii=False, indent=2),
        },
        status_code=404 if record is None else 200,
    )
