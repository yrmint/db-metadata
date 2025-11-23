from fastapi import APIRouter, HTTPException
from backend.models.timestamp_model import TimestampRecord
from backend.services.timestamps_service import save_timestamp

router = APIRouter(tags=["Timestamps"])

@router.post("/timestamps/save")
def save_stats(record: TimestampRecord):
    try:
        return save_timestamp(record)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
