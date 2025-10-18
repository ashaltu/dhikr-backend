from fastapi import APIRouter

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("")
async def get_privacy_policy():
    return {
        "status": "success",
        "message": "Privacy policy",
        "data": {
            "policy": "Dhikr Extension Privacy Policy",
            "principles": [
                "We never store raw IP addresses beyond initial geolocation lookup",
                "All URLs are hashed using HMAC-SHA256 before storage",
                "PII (emails, phone numbers, tokens) is automatically redacted from URLs and titles",
                "Raw URLs are purged after 24 hours, only hashed IDs and metadata are retained",
                "Geolocation is coarse (country/city level only)",
                "Analytics data is aggregated and anonymized",
                "No personally identifiable information is collected or stored"
            ],
            "data_collected": {
                "url_id": "HMAC-SHA256 hash of redacted URL",
                "domain": "Domain name only (e.g., youtube.com)",
                "category_key": "Site classification (waste, haram, distraction, etc.)",
                "duration_seconds": "Time spent on site",
                "region": "Coarse location (city, country)",
                "day": "Date in YYYY-MM-DD format"
            },
            "data_not_collected": [
                "Raw URLs after 24 hours",
                "IP addresses (discarded after geolocation)",
                "Personal identifiers (emails, phone numbers)",
                "Authentication tokens or session data",
                "Exact browsing history"
            ],
            "contact": "For privacy concerns, please contact the extension developer"
        }
    }
