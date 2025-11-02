from fastapi import APIRouter, HTTPException
from backend.models.stats_model import TableCount
from backend.services.stats_service import get_table_count_by_db

router = APIRouter(tags=["Statistics"])

@router.get("/databases/{db_id}/tables/count", response_model=TableCount)
def get_table_count(db_id: int):
    """
    Returns number of tables in specified database (using db_id).
    """
    try:
        return get_table_count_by_db(db_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
