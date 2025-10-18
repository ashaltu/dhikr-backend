import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ReminderCache


class QuranService:
    def __init__(self):
        self.quran_foundation_api = "https://api.quran.com/api/v4"
        self.fallback_api = "https://api.alquran.cloud/v1"
    
    async def get_ayah(
        self, 
        reference: str, 
        lang: str = "en",
        db: AsyncSession | None = None
    ) -> dict | None:
        if db:
            cached = await self._get_from_cache(reference, lang, db)
            if cached:
                return cached
        
        ayah_data = await self._fetch_from_api(reference, lang)
        
        if db and ayah_data:
            await self._save_to_cache(reference, lang, ayah_data, db)
        
        return ayah_data
    
    async def _get_from_cache(
        self, 
        reference: str, 
        lang: str,
        db: AsyncSession
    ) -> dict | None:
        try:
            stmt = select(ReminderCache).where(
                ReminderCache.reference == reference,
                ReminderCache.lang == lang
            )
            result = await db.execute(stmt)
            cached = result.scalar_one_or_none()
            
            if cached:
                return {
                    "verse_text": cached.verse_text,
                    "translation": cached.translation,
                    "audio_url": cached.audio_url,
                    "reference": reference
                }
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        
        return None
    
    async def _save_to_cache(
        self,
        reference: str,
        lang: str,
        ayah_data: dict,
        db: AsyncSession
    ):
        try:
            stmt = select(ReminderCache).where(
                ReminderCache.reference == reference,
                ReminderCache.lang == lang
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.verse_text = ayah_data.get("verse_text", "")
                existing.translation = ayah_data.get("translation", "")
                existing.audio_url = ayah_data.get("audio_url", "")
            else:
                cache_entry = ReminderCache(
                    reference=reference,
                    verse_text=ayah_data.get("verse_text", ""),
                    translation=ayah_data.get("translation", ""),
                    audio_url=ayah_data.get("audio_url", ""),
                    lang=lang
                )
                db.add(cache_entry)
            
            await db.commit()
        except Exception as e:
            print(f"Cache save error: {e}")
            await db.rollback()
    
    async def _fetch_from_api(self, reference: str, lang: str) -> dict | None:
        try:
            return await self._fetch_from_quran_com(reference, lang)
        except Exception as e:
            print(f"Quran.com API error: {e}")
            try:
                return await self._fetch_from_alquran_cloud(reference, lang)
            except Exception as e2:
                print(f"AlQuran.cloud API error: {e2}")
                return None
    
    async def _fetch_from_quran_com(self, reference: str, lang: str) -> dict:
        parts = reference.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid reference format: {reference}")
        
        surah, ayah_range = parts[0], parts[1]
        
        if "-" in ayah_range:
            start_ayah, end_ayah = ayah_range.split("-")
            ayah_number = start_ayah
        else:
            ayah_number = ayah_range
        
        async with httpx.AsyncClient() as client:
            verse_response = await client.get(
                f"{self.quran_foundation_api}/verses/by_key/{surah}:{ayah_number}",
                params={"language": lang, "words": "false", "translations": "131"},
                timeout=10.0
            )
            verse_response.raise_for_status()
            verse_data = verse_response.json()
            
            verse_text = verse_data.get("verse", {}).get("text_uthmani", "")
            translation = ""
            
            if "verse" in verse_data and "translations" in verse_data["verse"]:
                translations = verse_data["verse"]["translations"]
                if translations and len(translations) > 0:
                    translation = translations[0].get("text", "")
            
            audio_url = verse_data.get("verse", {}).get("audio", {}).get("url", "")
            
            return {
                "verse_text": verse_text,
                "translation": translation,
                "audio_url": audio_url,
                "reference": reference
            }
    
    async def _fetch_from_alquran_cloud(self, reference: str, lang: str) -> dict:
        parts = reference.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid reference format: {reference}")
        
        surah, ayah_range = parts[0], parts[1]
        
        if "-" in ayah_range:
            start_ayah, end_ayah = ayah_range.split("-")
            ayah_number = start_ayah
        else:
            ayah_number = ayah_range
        
        async with httpx.AsyncClient() as client:
            arabic_response = await client.get(
                f"{self.fallback_api}/ayah/{surah}:{ayah_number}",
                timeout=10.0
            )
            arabic_response.raise_for_status()
            arabic_data = arabic_response.json()
            
            english_response = await client.get(
                f"{self.fallback_api}/ayah/{surah}:{ayah_number}/en.asad",
                timeout=10.0
            )
            english_data = english_response.json() if english_response.status_code == 200 else {}
            
            verse_text = arabic_data.get("data", {}).get("text", "")
            translation = english_data.get("data", {}).get("text", "")
            audio_url = ""
            
            return {
                "verse_text": verse_text,
                "translation": translation,
                "audio_url": audio_url,
                "reference": reference
            }
