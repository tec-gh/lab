from datetime import datetime
from typing import Any

from pydantic import BaseModel


class RecordCreateResponse(BaseModel):
    id: int
    message: str
    mapping_version: int


class RecordItemResponse(BaseModel):
    id: int
    hostname: str | None
    ipaddress: str | None
    area: str | None
    building: str | None
    category: str | None
    model: str | None
    ping_test_result: str | None
    exec_result: str | None
    received_at: datetime


class RecordListResponse(BaseModel):
    items: list[RecordItemResponse]
    page: int
    page_size: int
    total: int


class RecordDetailResponse(RecordItemResponse):
    payload: dict[str, Any]
    mapping_version: int
