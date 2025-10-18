from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base


class ReminderRule(Base):
    __tablename__ = "reminder_rules"

    id = Column(Integer, primary_key=True, index=True)
    domain_pattern = Column(String(255), nullable=False, index=True)
    path_pattern = Column(String(255), nullable=True)
    category_key = Column(String(50), nullable=False, index=True)
    reference = Column(String(50), nullable=False)


class ReminderCache(Base):
    __tablename__ = "reminder_cache"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), nullable=False, unique=True, index=True)
    verse_text = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    lang = Column(String(10), nullable=False, default="en")
    last_fetched = Column(DateTime(timezone=True), server_default=func.now())


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(String(64), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    category_key = Column(String(50), nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=False)
    region = Column(String(100), nullable=True)
    day = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class RequestLog(Base):
    __tablename__ = "requests_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    domain = Column(String(255), nullable=False, index=True)
    path = Column(String(500), nullable=True)
    category_key = Column(String(50), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
