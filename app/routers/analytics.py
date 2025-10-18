from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime, timedelta
from app.database import get_db
from app.models import AnalyticsEvent, ReminderRule
from app.services.pii_utils import redact_url, redact_title
from app.services.geo_utils import get_location_from_ip
from app.utils.hashing import hash_url

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsLogRequest(BaseModel):
    url: str
    title: str | None = None
    domain: str
    path: str | None = None
    duration_seconds: int


@router.post("/log")
async def log_analytics(
    data: AnalyticsLogRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    redacted_url = redact_url(data.url)
    redacted_title = redact_title(data.title) if data.title else None
    
    url_id = hash_url(redacted_url)
    
    client_ip = request.client.host if request.client else "127.0.0.1"
    location = await get_location_from_ip(client_ip)
    region = location.get("region", "Unknown")
    
    category_key = await _classify_site(data.domain, data.path, db)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    event = AnalyticsEvent(
        url_id=url_id,
        domain=data.domain,
        category_key=category_key,
        duration_seconds=data.duration_seconds,
        region=region,
        day=today
    )
    
    db.add(event)
    await db.commit()
    
    return {
        "status": "success",
        "message": "Analytics logged successfully",
        "data": {
            "url_id": url_id,
            "category": category_key,
            "region": region
        }
    }


@router.get("/summary")
async def get_analytics_summary(
    period: str = "7d",
    db: AsyncSession = Depends(get_db)
):
    days = int(period.replace("d", ""))
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    stmt = select(
        AnalyticsEvent.category_key,
        func.count(AnalyticsEvent.id).label("count"),
        func.sum(AnalyticsEvent.duration_seconds).label("total_seconds")
    ).where(
        AnalyticsEvent.day >= start_date
    ).group_by(
        AnalyticsEvent.category_key
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    summary = {}
    for row in rows:
        category = row.category_key or "uncategorized"
        total_hours = round((row.total_seconds or 0) / 3600, 2)
        summary[category] = {
            "count": row.count,
            "hours": total_hours
        }
    
    return {
        "status": "success",
        "message": f"Analytics summary for the last {period}",
        "data": summary
    }


async def _classify_site(domain: str, path: str | None, db: AsyncSession) -> str | None:
    try:
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
        
        if rule:
            return rule[0].category_key
    except Exception:
        pass
    
    return None
