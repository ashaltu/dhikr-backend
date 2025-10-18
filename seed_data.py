import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from app.models import Base, ReminderRule

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if "?" in DATABASE_URL and "sslmode=" in DATABASE_URL:
    parts = DATABASE_URL.split("?")
    params = [p for p in parts[1].split("&") if not p.startswith("sslmode=")]
    DATABASE_URL = parts[0] + ("?" + "&".join(params) if params else "")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(ReminderRule))
        existing_count = result.scalar() or 0
        
        if existing_count > 0:
            print(f"✓ Database already contains {existing_count} reminder rules. Skipping seed.")
            return
        
        seed_rules = [
            ReminderRule(
                domain_pattern="youtube.com",
                path_pattern="/shorts",
                category_key="waste",
                reference="103:1-3"
            ),
            ReminderRule(
                domain_pattern="tiktok.com",
                path_pattern="/discover",
                category_key="waste",
                reference="23:5"
            ),
            ReminderRule(
                domain_pattern="instagram.com",
                path_pattern="/reels",
                category_key="gaze",
                reference="24:30"
            ),
            ReminderRule(
                domain_pattern="twitter.com",
                path_pattern=None,
                category_key="distraction",
                reference="29:45"
            ),
            ReminderRule(
                domain_pattern="x.com",
                path_pattern=None,
                category_key="distraction",
                reference="29:45"
            ),
            ReminderRule(
                domain_pattern="facebook.com",
                path_pattern=None,
                category_key="waste",
                reference="62:9-10"
            ),
            ReminderRule(
                domain_pattern="reddit.com",
                path_pattern="/r/all",
                category_key="distraction",
                reference="2:286"
            ),
            ReminderRule(
                domain_pattern="twitch.tv",
                path_pattern=None,
                category_key="waste",
                reference="103:1-3"
            ),
        ]
        
        for rule in seed_rules:
            session.add(rule)
        
        await session.commit()
        print(f"✓ Seeded {len(seed_rules)} reminder rules")


if __name__ == "__main__":
    print("Starting database seed...")
    asyncio.run(seed_database())
    print("Database seeding complete!")
