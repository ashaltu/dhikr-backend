# Test Suite for Dhikr Extension Backend

This directory contains comprehensive tests for the privacy and security features of the Dhikr Extension Backend.

## Test Files

- `test_pii_utils.py` - Tests for PII redaction functionality (34 tests)
- `test_geo_utils.py` - Tests for IP geolocation functionality (17 tests)  
- `test_hashing.py` - Tests for HMAC-SHA256 URL hashing (26 tests)

**Total: 77 tests**

## Running Tests

```bash
# Install dependencies first
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pii_utils.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Coverage

### PII Redaction (`test_pii_utils.py`)
- Email address redaction
- Phone number redaction (multiple formats)
- UUID redaction
- Bearer token and API key redaction
- SSN redaction
- Credit card number redaction
- Mixed PII scenarios
- Edge cases (None, empty, no PII)

### Geolocation (`test_geo_utils.py`)
- Localhost/private IP handling
- Successful API responses
- API failure scenarios
- Network errors and timeouts
- Missing data field handling
- JSON parsing errors
- Request parameter validation

### URL Hashing (`test_hashing.py`)
- HMAC-SHA256 hashing
- Deterministic behavior
- Case sensitivity
- URL component handling (protocol, port, path, query, fragment)
- Environment variable integration
- Error handling for missing keys
- Unicode and special character support

## Notes

- All tests use proper mocking to avoid external API calls
- Async tests are properly marked with `@pytest.mark.asyncio`
- Python 3.9+ compatibility ensured
- Tests follow AAA pattern (Arrange, Act, Assert)
- No existing code was modified

## Test Results

All 77 tests passing ✓
