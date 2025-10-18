from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import RequestLog

router = APIRouter(prefix="/log-trigger", tags=["logging"])


class TriggerLogRequest(BaseModel):
    domain: str
    path: str | None = None
    category_key: str
    duration_seconds: int


@router.post("")
async def log_trigger(
    data: TriggerLogRequest,
    db: AsyncSession = Depends(get_db)
):
    log_entry = RequestLog(
        domain=data.domain,
        path=data.path,
        category_key=data.category_key,
        duration_seconds=data.duration_seconds
    )
    
    db.add(log_entry)
    await db.commit()
    
    return {
        "status": "success",
        "message": "Trigger logged successfully",
        "data": {
            "domain": data.domain,
            "category": data.category_key
        }
    }
