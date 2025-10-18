import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.database import init_db
from app.routers import reminder, rules, analytics, logging, privacy

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Dhikr Extension API",
    description="Privacy-focused backend for Muslim browser extension with Quran reminders",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"(http://localhost(:\d+)?|https://.*\.replit\.(dev|app)|chrome-extension://.*|moz-extension://.*)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(reminder.router)
app.include_router(rules.router)
app.include_router(analytics.router)
app.include_router(logging.router)
app.include_router(privacy.router)


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Dhikr Extension API is running",
        "data": {
            "version": "1.0.0",
            "endpoints": [
                "/reminder - Get Quran reminder for a domain/path",
                "/rules - Get all reminder rules",
                "/analytics/log - Log anonymized browsing event",
                "/analytics/summary - Get analytics summary",
                "/log-trigger - Log reminder trigger event",
                "/privacy - View privacy policy"
            ]
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "success",
        "message": "API is healthy",
        "data": {"healthy": True}
    }
