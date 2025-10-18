from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models import ReminderRule
from app.services.quran_service import QuranService

router = APIRouter(prefix="/reminder", tags=["reminder"])


@router.get("")
async def get_reminder(
    domain: str = Query(..., description="Domain to match"),
    path: str = Query(None, description="Path to match"),
    lang: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ReminderRule).where(ReminderRule.domain_pattern == domain)
    
    if path:
        stmt = stmt.where(
            or_(
                ReminderRule.path_pattern == path,
                ReminderRule.path_pattern.is_(None)
            )
        ).order_by(ReminderRule.path_pattern.desc())
    else:
        stmt = stmt.where(ReminderRule.path_pattern.is_(None))
    
    result = await db.execute(stmt)
    rule = result.first()
    
    if not rule:
        raise HTTPException(
            status_code=404,
            detail="No reminder rule found for this domain/path"
        )
    
    rule = rule[0]
    
    quran_service = QuranService()
    ayah_data = await quran_service.get_ayah(rule.reference, lang, db)
    
    if not ayah_data:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch ayah from Quran API"
        )
    
    return {
        "status": "success",
        "message": "Reminder fetched successfully",
        "data": {
            "category": rule.category_key,
            "reference": rule.reference,
            **ayah_data
        }
    }
