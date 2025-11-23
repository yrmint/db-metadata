from pydantic import BaseModel, field_validator
from typing import Optional

class TimestampRecord(BaseModel):
    db_id: int
    tables_count: Optional[float] = None
    columns_count: Optional[float] = None
    pk_count: Optional[float] = None
    fk_count: Optional[float] = None
    uk_count: Optional[float] = None
    records_count: Optional[float] = None

    # @field_validator("tables_count", "columns_count", "pk_count", "fk_count", "uk_count", "records_count", mode="after")
    # def ensure_at_least_one_selected(cls, v, values):
    #     if all(values.get(f) is None for f in ["tables_count", "columns_count", "pk_count", "fk_count", "uk_count", "records_count"]):
    #         raise ValueError("At least one stats field must be provided")
    #     return v

