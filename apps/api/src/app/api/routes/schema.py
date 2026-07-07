from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.db.engine import get_engine
from app.db.introspect import introspect_schema

router = APIRouter()


class ColumnResponse(BaseModel):
    name: str
    type: str
    primary_key: bool
    sample_values: list[str]


class TableResponse(BaseModel):
    name: str
    columns: list[ColumnResponse]


@router.get("/schema", response_model=list[TableResponse])
def get_schema(settings: Settings = Depends(get_settings)) -> list[TableResponse]:
    engine = get_engine(settings.database_url)
    db_schema = introspect_schema(engine)
    return [
        TableResponse(
            name=table.name,
            columns=[
                ColumnResponse(
                    name=c.name, type=c.type, primary_key=c.primary_key, sample_values=c.sample_values
                )
                for c in table.columns
            ],
        )
        for table in db_schema.tables
    ]
