# Dhikr Extension Backend API

A privacy-focused FastAPI backend for a Muslim browser extension that provides Quranic reminders when users spend time on distracting or harmful websites. The backend handles Quran API proxying, event logging, and anonymized analytics aggregation.

## Features

- **Quran API Proxy**: Fetches Quranic ayahs from multiple sources with intelligent caching
- **Rule-Based Reminders**: Domain and path pattern matching for contextual Islamic reminders
- **Privacy-First Analytics**: PII redaction, URL hashing, and anonymized data collection
- **Event Logging**: Track reminder triggers and browsing patterns
- **Geolocation**: Coarse location tracking (country/city only) without storing IP addresses
- **CORS Support**: Ready for browser extension integration

## Tech Stack

- **FastAPI**: Modern async Python web framework
- **PostgreSQL**: Robust database with async support (asyncpg)
- **SQLAlchemy**: Powerful ORM with async capabilities
- **httpx**: Async HTTP client for Quran API calls
- **Uvicorn**: ASGI server for production-ready deployment

## Privacy Guarantees

1. **No IP Storage**: IPs discarded immediately after geolocation
2. **URL Hashing**: All URLs hashed using HMAC-SHA256 before storage
3. **PII Redaction**: Automatic removal of emails, phones, tokens, SSNs, credit cards
4. **Data Retention**: Raw URLs purged after 24 hours (design principle)
5. **Coarse Location**: Only country/city level geolocation
6. **Anonymized Analytics**: All data aggregated without personal identifiers

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database (provided by Replit)

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   
   Create a `.env` file or use the existing environment variables:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SERVER_HMAC_KEY=your_long_random_secret_key_here
   QURAN_API_URL=https://api.quran.com/api/v4
   ```

3. **Initialize Database**:
   
   Run the seed script to create tables and add initial reminder rules:
   ```bash
   python seed_data.py
   ```

4. **Start the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Root Endpoint
- **GET** `/`
- Returns API status and available endpoints

### 2. Health Check
- **GET** `/health`
- Returns health status of the API

### 3. Get Reminder
- **GET** `/reminder?domain=youtube.com&path=/shorts&lang=en`
- Fetches a Quranic reminder for a specific domain/path
- **Query Parameters**:
  - `domain` (required): Domain to match (e.g., youtube.com)
  - `path` (optional): Path to match (e.g., /shorts)
  - `lang` (optional): Language code (default: en)
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Reminder fetched successfully",
    "data": {
      "category": "waste",
      "reference": "103:1-3",
      "verse_text": "وَٱلْعَصْرِ",
      "translation": "By time...",
      "audio_url": "https://..."
    }
  }
  ```

### 4. Get All Rules
- **GET** `/rules`
- Returns all reminder rules in the database
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Found 8 reminder rules",
    "data": [
      {
        "id": 1,
        "domain_pattern": "youtube.com",
        "path_pattern": "/shorts",
        "category_key": "waste",
        "reference": "103:1-3"
      }
    ]
  }
  ```

### 5. Log Analytics Event
- **POST** `/analytics/log`
- Logs an anonymized browsing event
- **Request Body**:
  ```json
  {
    "url": "https://youtube.com/shorts/abc123",
    "title": "Video Title",
    "domain": "youtube.com",
    "path": "/shorts/abc123",
    "duration_seconds": 300
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Analytics logged successfully",
    "data": {
      "url_id": "a1b2c3d4...",
      "category": "waste",
      "region": "New York, United States"
    }
  }
  ```

### 6. Get Analytics Summary
- **GET** `/analytics/summary?period=7d`
- Returns aggregated analytics for a time period
- **Query Parameters**:
  - `period` (optional): Time period (e.g., 7d, 30d) - default: 7d
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Analytics summary for the last 7d",
    "data": {
      "waste": {"count": 1245, "hours": 195.5},
      "haram": {"count": 298, "hours": 48.2},
      "distraction": {"count": 567, "hours": 89.3}
    }
  }
  ```

### 7. Log Reminder Trigger
- **POST** `/log-trigger`
- Logs when a reminder is shown to a user
- **Request Body**:
  ```json
  {
    "domain": "youtube.com",
    "path": "/shorts",
    "category_key": "waste",
    "duration_seconds": 300
  }
  ```

### 8. Privacy Policy
- **GET** `/privacy`
- Returns detailed privacy policy and data handling practices

## Database Schema

### Tables

1. **reminder_rules**: Stores domain/path patterns with Quranic references
   - `id`, `domain_pattern`, `path_pattern`, `category_key`, `reference`

2. **reminder_cache**: Caches fetched Quran verses for performance
   - `id`, `reference`, `verse_text`, `translation`, `audio_url`, `lang`, `last_fetched`

3. **analytics_events**: Stores anonymized browsing events
   - `id`, `url_id` (hashed), `domain`, `category_key`, `duration_seconds`, `region`, `day`, `timestamp`

4. **requests_log**: Logs reminder trigger events
   - `id`, `timestamp`, `domain`, `path`, `category_key`, `duration_seconds`

## Development

### Project Structure

```
app/
├── main.py              # FastAPI application and CORS config
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy database models
├── routers/
│   ├── reminder.py      # Quran reminder endpoints
│   ├── rules.py         # Rule management endpoints
│   ├── analytics.py     # Analytics logging and summary
│   ├── logging.py       # Trigger event logging
│   └── privacy.py       # Privacy policy endpoint
├── services/
│   ├── quran_service.py # Quran API integration with caching
│   ├── pii_utils.py     # PII detection and redaction
│   └── geo_utils.py     # IP geolocation utilities
└── utils/
    └── hashing.py       # HMAC-SHA256 URL hashing

seed_data.py             # Database initialization script
requirements.txt         # Python dependencies
.env.example            # Environment variable template
```

### Testing Endpoints

You can test the API using curl:

```bash
# Get a reminder
curl "http://localhost:5000/reminder?domain=youtube.com&path=/shorts"

# View all rules
curl "http://localhost:5000/rules"

# Log analytics
curl -X POST "http://localhost:5000/analytics/log" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/shorts/test",
    "title": "Test Video",
    "domain": "youtube.com",
    "path": "/shorts/test",
    "duration_seconds": 120
  }'

# Get analytics summary
curl "http://localhost:5000/analytics/summary?period=7d"
```

## Default Reminder Rules

The seed data includes these rules:

| Domain | Path | Category | Reference | Description |
|--------|------|----------|-----------|-------------|
| youtube.com | /shorts | waste | 103:1-3 | Surah Al-Asr (Time) |
| tiktok.com | /discover | waste | 23:5 | Guarding private parts |
| instagram.com | /reels | gaze | 24:30 | Lower your gaze |
| twitter.com / x.com | - | distraction | 29:45 | Remembrance of Allah |
| facebook.com | - | waste | 62:9-10 | Friday prayer reminder |
| reddit.com | /r/all | distraction | 2:286 | Allah burdens not |
| twitch.tv | - | waste | 103:1-3 | Surah Al-Asr |

## External APIs Used

1. **Quran.com API** (Primary): https://api.quran.com/api/v4
2. **AlQuran.cloud API** (Fallback): https://api.alquran.cloud/v1
3. **ip-api.com** (Geolocation): http://ip-api.com/json/

## License

This project is designed for educational and Islamic purposes. Use responsibly and respect user privacy.

## Contributing

When contributing, ensure you:
- Maintain privacy-first principles
- Add tests for new features
- Update documentation
- Follow PEP 8 Python style guide

---

**May Allah accept this work and make it beneficial for the Muslim Ummah.**
