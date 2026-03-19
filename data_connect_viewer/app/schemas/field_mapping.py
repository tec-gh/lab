from pydantic import BaseModel, Field


class FieldMappingUpdateItem(BaseModel):
    field_key: str
    display_name: str = Field(min_length=1, max_length=128)
    json_path: str = Field(min_length=1, max_length=255)
    is_visible: bool = True
    is_searchable: bool = True
    is_exportable: bool = True
    sort_order: int = 0


class FieldMappingUpdateRequest(BaseModel):
    mappings: list[FieldMappingUpdateItem]
    change_summary: str | None = None
