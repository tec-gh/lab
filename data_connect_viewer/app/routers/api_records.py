from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import verify_api_key
from app.core.config import settings
from app.core.database import get_db
from app.repositories.field_mapping_repository import get_active_mappings, replace_active_mappings
from app.repositories.record_repository import resync_records
from app.schemas.field_mapping import FieldMappingUpdateItem, FieldMappingUpdateRequest
from app.schemas.record import RecordCreateResponse, RecordDetailResponse, RecordItemResponse, RecordListResponse
from app.services.mapping_service import MappingExtractor
from app.services.export_service import render_csv, render_json
from app.services.record_service import create_record_from_payload, export_records, get_record_detail, search_records

router = APIRouter(prefix="/api/v1", tags=["api"])


def parse_filters(
    hostname: Optional[str] = None,
    ipaddress: Optional[str] = None,
    area: Optional[str] = None,
    building: Optional[str] = None,
    category: Optional[str] = None,
    model: Optional[str] = None,
    ping_test_result: Optional[str] = None,
    exec_result: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> Dict[str, Any]:
    return {
        "hostname": hostname,
        "ipaddress": ipaddress,
        "area": area,
        "building": building,
        "category": category,
        "model": model,
        "ping_test_result": ping_test_result,
        "exec_result": exec_result,
        "keyword": keyword,
        "date_from": date_from,
        "date_to": date_to,
    }


@router.post("/records", response_model=RecordCreateResponse, dependencies=[Depends(verify_api_key)])
def create_record(payload: Dict[str, Any], response: Response, db: Session = Depends(get_db)):
    record, created = create_record_from_payload(db, payload)
    db.commit()
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return RecordCreateResponse(
        id=record.id,
        message="created" if created else "updated",
        mapping_version=record.mapping_version,
    )


@router.get("/records", response_model=RecordListResponse)
def get_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.page_size_default, ge=1, le=200),
    hostname: Optional[str] = None,
    ipaddress: Optional[str] = None,
    area: Optional[str] = None,
    building: Optional[str] = None,
    category: Optional[str] = None,
    model: Optional[str] = None,
    ping_test_result: Optional[str] = None,
    exec_result: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    filters = parse_filters(
        hostname, ipaddress, area, building, category, model, ping_test_result, exec_result, keyword, date_from, date_to
    )
    records, total = search_records(db, filters, page, page_size)
    items = [
        RecordItemResponse(
            id=record.id,
            hostname=record.hostname,
            ipaddress=record.ipaddress,
            area=record.area,
            building=record.building,
            category=record.category,
            model=record.model,
            ping_test_result=record.ping_test_result,
            exec_result=record.exec_result,
            received_at=record.received_at,
        )
        for record in records
    ]
    return RecordListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/records/export.csv")
def export_csv(
    hostname: Optional[str] = None,
    ipaddress: Optional[str] = None,
    area: Optional[str] = None,
    building: Optional[str] = None,
    category: Optional[str] = None,
    model: Optional[str] = None,
    ping_test_result: Optional[str] = None,
    exec_result: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    filters = parse_filters(
        hostname, ipaddress, area, building, category, model, ping_test_result, exec_result, keyword, date_from, date_to
    )
    content = render_csv(list(export_records(db, filters, settings.export_max_rows)))
    headers = {
        "Content-Disposition": "attachment; filename=records.csv",
        "Cache-Control": "no-store",
    }
    return Response(content=content.encode("utf-8"), media_type="application/octet-stream", headers=headers)


@router.get("/records/export.json")
def export_json_file(
    hostname: Optional[str] = None,
    ipaddress: Optional[str] = None,
    area: Optional[str] = None,
    building: Optional[str] = None,
    category: Optional[str] = None,
    model: Optional[str] = None,
    ping_test_result: Optional[str] = None,
    exec_result: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    filters = parse_filters(
        hostname, ipaddress, area, building, category, model, ping_test_result, exec_result, keyword, date_from, date_to
    )
    content = render_json(list(export_records(db, filters, settings.export_max_rows)))
    headers = {
        "Content-Disposition": "attachment; filename=records.json",
        "Cache-Control": "no-store",
    }
    return Response(content=content.encode("utf-8"), media_type="application/octet-stream", headers=headers)


@router.get("/records/{record_id}", response_model=RecordDetailResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record, payload = get_record_detail(db, record_id)
    if not record or payload is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordDetailResponse(
        id=record.id,
        hostname=record.hostname,
        ipaddress=record.ipaddress,
        area=record.area,
        building=record.building,
        category=record.category,
        model=record.model,
        ping_test_result=record.ping_test_result,
        exec_result=record.exec_result,
        received_at=record.received_at,
        payload=payload,
        mapping_version=record.mapping_version,
    )


@router.get("/settings/mappings")
def get_mappings(db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    items = get_active_mappings(db)
    return {
        "items": [
            {
                "field_key": item.field_key,
                "display_name": item.display_name,
                "json_path": item.json_path,
                "is_visible": item.is_visible,
                "is_searchable": item.is_searchable,
                "is_exportable": item.is_exportable,
                "sort_order": item.sort_order,
                "version": item.version,
            }
            for item in items
        ]
    }


@router.put("/settings/mappings")
def update_mappings(
    request: FieldMappingUpdateRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    version = replace_active_mappings(db, request.mappings, changed_by="api", change_summary=request.change_summary)
    db.commit()
    return {"message": "updated", "version": version}


@router.post("/settings/mappings/resync")
def api_resync_mappings(db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    active = get_active_mappings(db)
    mapping_dict = {item.field_key: item.json_path for item in active}
    version = max((item.version for item in active), default=1)
    count = resync_records(db, MappingExtractor(), mapping_dict, version)
    db.commit()
    return {"message": "resynced", "count": count, "version": version}
