from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import ReminderRule

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("")
async def get_rules(db: AsyncSession = Depends(get_db)):
    stmt = select(ReminderRule)
    result = await db.execute(stmt)
    rules = result.scalars().all()
    
    rules_data = [
        {
            "id": rule.id,
            "domain_pattern": rule.domain_pattern,
            "path_pattern": rule.path_pattern,
            "category_key": rule.category_key,
            "reference": rule.reference
        }
        for rule in rules
    ]
    
    return {
        "status": "success",
        "message": f"Found {len(rules_data)} reminder rules",
        "data": rules_data
    }
