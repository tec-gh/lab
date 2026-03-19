from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class RecordCreateResponse(BaseModel):
    id: int
    message: str
    mapping_version: int


class RecordItemResponse(BaseModel):
    id: int
    hostname: Optional[str]
    ipaddress: Optional[str]
    area: Optional[str]
    building: Optional[str]
    category: Optional[str]
    model: Optional[str]
    ping_test_result: Optional[str]
    exec_result: Optional[str]
    received_at: datetime


class RecordListResponse(BaseModel):
    items: list[RecordItemResponse]
    page: int
    page_size: int
    total: int


class RecordDetailResponse(RecordItemResponse):
    payload: dict[str, Any]
    mapping_version: int
