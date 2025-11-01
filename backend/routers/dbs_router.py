from fastapi import APIRouter
from typing import List
from backend.models.db_models import DatabaseItem
from backend.services.db_service import get_all_databases

router = APIRouter(tags=["Databases"])

@router.get("/databases/", response_model=List[DatabaseItem])
def list_databases():
    """Returns list of databases."""
    return get_all_databases()
