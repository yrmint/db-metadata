from pydantic import BaseModel

class TableCount(BaseModel):
    db_id: int
    table_count: int
