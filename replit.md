# Dhikr Extension Backend API

## Overview

This is a privacy-focused FastAPI backend for a Muslim browser extension that provides Quranic reminders when users visit distracting or harmful websites. The system matches visited domains/paths against predefined rules, fetches relevant Quranic verses, and logs analytics while maintaining strict privacy guarantees through URL hashing, PII redaction, and anonymized data collection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **FastAPI with async/await**: Chosen for high-performance async request handling and automatic OpenAPI documentation. FastAPI provides built-in request validation through Pydantic models and native async support for database and HTTP operations.
- **ASGI server (Uvicorn)**: Production-ready async server that handles concurrent connections efficiently.

### Data Persistence Layer
- **SQLAlchemy 2.0 with AsyncSession**: Provides async ORM capabilities for non-blocking database operations. Uses declarative base models for schema definition.
- **asyncpg driver**: High-performance async PostgreSQL driver that integrates with SQLAlchemy's async engine.
- **Database connection string normalization**: Automatically converts `postgres://` URLs to `postgresql+asyncpg://` format and strips incompatible SSL parameters for Replit compatibility.

### Core Data Models
The system defines four primary database tables:

1. **ReminderRule**: Stores domain/path pattern matching rules with associated Quranic verse references and category classifications (waste, haram, distraction, etc.)
2. **ReminderCache**: Caches fetched Quranic verses to reduce external API calls and improve response times
3. **AnalyticsEvent**: Stores anonymized browsing analytics with hashed URL IDs, coarse geolocation, and time spent data
4. **RequestLog**: Logs reminder trigger events with domain, category, and duration information

### Privacy Architecture

**URL Anonymization Pipeline**:
- **PII Redaction**: Regex-based removal of emails, phone numbers, UUIDs, authentication tokens, SSNs, and credit card numbers from URLs and page titles before processing
- **HMAC-SHA256 Hashing**: All redacted URLs are hashed using a server-side secret key (SERVER_HMAC_KEY) before storage, creating non-reversible URL identifiers
- **IP Address Handling**: Client IPs are used only for immediate geolocation lookup, then discarded without storage

**Data Minimization Strategy**:
- Only coarse geolocation stored (city/country level via ip-api.com)
- Domain names stored separately from full URLs
- Category classifications abstracted from specific content
- No retention of raw URLs beyond initial processing

### API Route Architecture

**Modular Router Design**: Separated into focused routers for single-responsibility endpoints:

1. **/reminder**: Pattern matching and Quran verse retrieval endpoint
   - Accepts domain and optional path parameters
   - Queries ReminderRule table for matching patterns with path precedence
   - Delegates verse fetching to QuranService with caching

2. **/rules**: Read-only access to all configured reminder rules

3. **/analytics/log**: Anonymized event logging endpoint
   - Accepts URL, title, domain, path, and duration
   - Applies PII redaction and URL hashing
   - Performs geolocation lookup without storing IPs
   - Classifies site category based on rules

4. **/log-trigger**: Simple trigger event logging for reminder displays

5. **/privacy**: Static privacy policy endpoint documenting data handling practices

### Quran API Integration

**Multi-Source Strategy with Fallback**:
- Primary: Quran.com API (api.quran.com/api/v4)
- Fallback: AlQuran Cloud API (api.alquran.cloud/v1)
- Uses httpx async HTTP client for non-blocking external requests

**Caching Layer**: 
- Two-tier lookup: check ReminderCache table first, fetch from API on cache miss
- Stores Arabic text, translation, and audio URLs
- Reduces external API dependency and improves response times

### CORS Configuration
Regex-based origin allowlist supporting:
- Local development (localhost with any port)
- Replit deployments (*.replit.dev, *.replit.app)
- Browser extensions (chrome-extension://, moz-extension://)

### Application Lifecycle
- **Startup**: Automatic database initialization via lifespan context manager
- **Database migrations**: Uses SQLAlchemy's `create_all()` for schema creation (seed_data.py demonstrates pattern)

## External Dependencies

### Database
- **PostgreSQL**: Primary data store, accessed via asyncpg driver with SQLAlchemy async ORM
- **Connection handling**: Async session factory with automatic cleanup via dependency injection

### Third-Party APIs
- **Quran.com API**: Primary source for Quranic verses, translations, and audio
- **AlQuran Cloud API**: Fallback Quran data source
- **ip-api.com**: Free geolocation service for coarse location lookup (no API key required)

### Python Libraries
- **FastAPI 0.119.0**: Web framework and request routing
- **SQLAlchemy 2.0.44**: Async ORM with PostgreSQL support
- **asyncpg 0.30.0**: Async PostgreSQL driver
- **httpx 0.28.1**: Async HTTP client for external API calls
- **Pydantic 2.12.3**: Request/response validation and serialization
- **python-dotenv 1.1.1**: Environment variable management
- **Uvicorn 0.38.0**: ASGI server
- **passlib 1.7.4**: Cryptographic utilities (though not actively used in current codebase)

### Environment Variables
- **DATABASE_URL**: PostgreSQL connection string (provided by Replit)
- **SERVER_HMAC_KEY**: Secret key for HMAC-SHA256 URL hashing (must be set for security)