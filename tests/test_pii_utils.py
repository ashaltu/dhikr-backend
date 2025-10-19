import pytest
from app.services.pii_utils import redact_pii, redact_url, redact_title


class TestRedactPII:
    """Tests for PII redaction functionality"""
    
    def test_redact_email_basic(self):
        """Test basic email redaction"""
        text = "Contact me at john.doe@example.com for details"
        result = redact_pii(text)
        assert "[EMAIL_REDACTED]" in result
        assert "john.doe@example.com" not in result
        assert "Contact me at" in result
    
    def test_redact_multiple_emails(self):
        """Test redaction of multiple emails"""
        text = "Email alice@test.com or bob@company.org"
        result = redact_pii(text)
        assert result.count("[EMAIL_REDACTED]") == 2
        assert "alice@test.com" not in result
        assert "bob@company.org" not in result
    
    def test_redact_email_with_special_chars(self):
        """Test email with plus and underscore"""
        text = "Send to user+tag@example.co.uk and test_user@domain.com"
        result = redact_pii(text)
        assert result.count("[EMAIL_REDACTED]") == 2
        assert "@" not in result.replace("[EMAIL_REDACTED]", "")
    
    def test_redact_phone_basic_formats(self):
        """Test various phone number formats"""
        text = "Call 555-123-4567 or 555.123.4567 or 5551234567"
        result = redact_pii(text)
        assert result.count("[PHONE_REDACTED]") == 3
        assert "555-123-4567" not in result
    
    def test_redact_phone_with_spaces(self):
        """Test phone with spaces"""
        text = "Call 555 123 4567 today"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result
        assert "555 123 4567" not in result
        assert "today" in result
    
    def test_redact_international_phone(self):
        """Test international phone format"""
        text = "Call +1-555-123-4567 or +44 20 1234 5678"
        result = redact_pii(text)
        assert result.count("[PHONE_REDACTED]") == 2
        assert "+1-555" not in result

    def test_redact_phone_with_parentheses(self):
        """Test phone number with parentheses"""
        text = "My number is (555) 123-4567"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result
        assert "(555) 123-4567" not in result

        text = "My number is (212) 555 7890"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result
        assert "(212) 555 7890" not in result
    
    def test_redact_uuid(self):
        """Test UUID redaction"""
        text = "Session ID: 550e8400-e29b-41d4-a716-446655440000"
        result = redact_pii(text)
        assert "[UUID_REDACTED]" in result
        assert "550e8400-e29b-41d4-a716-446655440000" not in result
    
    def test_redact_multiple_uuids(self):
        """Test multiple UUID redaction"""
        text = "ID1: 123e4567-e89b-12d3-a456-426614174000 ID2: 987fcdeb-51a2-43f1-b456-123456789abc"
        result = redact_pii(text)
        assert result.count("[UUID_REDACTED]") == 2
    
    def test_redact_bearer_token(self):
        """Test Bearer token redaction"""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = redact_pii(text)
        assert "[TOKEN_REDACTED]" in result
        assert "Bearer" not in result or "[TOKEN_REDACTED]" in result
        assert "eyJhbGc" not in result
    
    def test_redact_long_token(self):
        """Test long alphanumeric token"""
        text = "Token: abc123def456ghi789jkl012mno345"
        result = redact_pii(text)
        assert "[TOKEN_REDACTED]" in result
        assert "abc123def456" not in result
    
    def test_redact_api_key_patterns(self):
        """Test API key pattern redaction"""
        text = "api_key=sk_test_1234567890abcdef and token:ghijk67890lmnop"
        result = redact_pii(text)
        assert "[TOKEN_REDACTED]" in result
        assert "sk_test" not in result
    
    def test_redact_ssn(self):
        """Test SSN redaction"""
        text = "SSN: 123-45-6789"
        result = redact_pii(text)
        assert "[SSN_REDACTED]" in result
        assert "123-45-6789" not in result
    
    def test_redact_multiple_ssn(self):
        """Test multiple SSN redaction"""
        text = "SSN1: 111-22-3333 and SSN2: 444-55-6666"
        result = redact_pii(text)
        assert result.count("[SSN_REDACTED]") == 2
    
    def test_redact_credit_card_with_spaces(self):
        """Test credit card with spaces"""
        text = "Card: 4532 1234 5678 9010"
        result = redact_pii(text)
        assert "[CARD_REDACTED]" in result
        assert "4532 1234" not in result
    
    def test_redact_credit_card_with_dashes(self):
        """Test credit card with dashes"""
        text = "Card: 4532-1234-5678-9010"
        result = redact_pii(text)
        assert "[CARD_REDACTED]" in result
        assert "4532-1234" not in result
    
    def test_redact_credit_card_no_separator(self):
        """Test credit card without separators"""
        text = "Card: 4532123456789010"
        result = redact_pii(text)
        assert "[CARD_REDACTED]" in result
        assert "4532123456789010" not in result
    
    def test_redact_mixed_pii(self):
        """Test text with multiple PII types"""
        text = "Contact john@example.com at 555-123-4567 or use card 4532-1234-5678-9010"
        result = redact_pii(text)
        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "[CARD_REDACTED]" in result
        assert "john@example.com" not in result
        assert "555-123-4567" not in result
        assert "4532-1234-5678-9010" not in result
    
    def test_redact_empty_string(self):
        """Test empty string handling"""
        result = redact_pii("")
        assert result == ""
    
    def test_redact_none(self):
        """Test None handling"""
        result = redact_pii(None)
        assert result is None
    
    def test_redact_no_pii(self):
        """Test text without PII"""
        text = "This is a normal sentence without any PII"
        result = redact_pii(text)
        assert result == text
    
    def test_redact_preserves_structure(self):
        """Test that redaction preserves text structure"""
        text = "Hello, my email is test@example.com and phone is 555-1234."
        result = redact_pii(text)
        assert result.startswith("Hello, my email is")
        assert "and phone is" in result


class TestRedactURL:
    """Tests for URL-specific redaction"""
    
    def test_redact_url_with_email_param(self):
        """Test URL with email parameter"""
        url = "https://example.com/reset?email=user@test.com"
        result = redact_url(url)
        assert "[EMAIL_REDACTED]" in result
        assert "user@test.com" not in result
    
    def test_redact_url_with_token(self):
        """Test URL with token"""
        url = "https://api.example.com/auth?token=abc123def456ghi789jkl012"
        result = redact_url(url)
        assert "[TOKEN_REDACTED]" in result
        assert "abc123def456ghi789jkl012" not in result
    
    def test_redact_url_with_uuid(self):
        """Test URL with UUID"""
        url = "https://example.com/users/550e8400-e29b-41d4-a716-446655440000"
        result = redact_url(url)
        assert "[UUID_REDACTED]" in result
    
    def test_redact_clean_url(self):
        """Test clean URL without PII"""
        url = "https://example.com/page"
        result = redact_url(url)
        assert result == url


class TestRedactTitle:
    """Tests for title-specific redaction"""
    
    def test_redact_title_with_email(self):
        """Test title containing email"""
        title = "Message from john@example.com"
        result = redact_title(title)
        assert "[EMAIL_REDACTED]" in result
        assert "john@example.com" not in result
    
    def test_redact_title_with_phone(self):
        """Test title containing phone"""
        title = "Call 555-123-4567 now!"
        result = redact_title(title)
        assert "[PHONE_REDACTED]" in result
    
    def test_redact_title_clean(self):
        """Test clean title"""
        title = "Normal Video Title"
        result = redact_title(title)
        assert result == title


class TestEdgeCases:
    """Edge cases and boundary conditions"""
    
    def test_partial_email_not_redacted(self):
        """Test that incomplete emails are not redacted"""
        text = "test@incomplete or @nodomain.com"
        result = redact_pii(text)
        # These should not be redacted as they're not valid emails
        assert text == result or "@" in result
    
    def test_short_numbers_not_phone(self):
        """Test that short numbers aren't treated as phone"""
        text = "The code is 123 or 456"
        result = redact_pii(text)
        # Short numbers should not be redacted
        assert "123" in result or "[PHONE_REDACTED]" not in result
    
    def test_uuid_case_insensitive(self):
        """Test UUID with mixed case"""
        text = "ID: 550E8400-E29B-41D4-A716-446655440000"
        result = redact_pii(text)
        assert "[UUID_REDACTED]" in result
    
    def test_token_pattern_case_insensitive(self):
        """Test token pattern with different cases"""
        text = "API_KEY=test12345678901234567890 and Api_Key=another1234567890"
        result = redact_pii(text)
        assert "[TOKEN_REDACTED]" in result
    
    def test_whitespace_preservation(self):
        """Test that whitespace is preserved"""
        text = "Email:  test@example.com  Phone:  555-1234567"
        result = redact_pii(text)
        assert "  " in result  # Multiple spaces preserved
    
    def test_special_characters_preserved(self):
        """Test special characters are preserved"""
        text = "Contact: user@test.com! (Important)"
        result = redact_pii(text)
        assert "!" in result
        assert "(" in result
        assert ")" in result
