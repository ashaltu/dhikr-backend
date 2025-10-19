import pytest
import os
from unittest.mock import patch
from app.utils.hashing import hash_url


class TestHashURL:
    """Tests for URL hashing functionality"""
    
    def test_hash_url_with_explicit_key(self):
        """Test hashing with explicitly provided key"""
        url = "https://example.com/page"
        secret = "my_secret_key"
        
        result = hash_url(url, secret)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64 hex characters
    
    def test_hash_url_deterministic(self):
        """Test that same URL and key produce same hash"""
        url = "https://example.com/page"
        secret = "my_secret_key"
        
        hash1 = hash_url(url, secret)
        hash2 = hash_url(url, secret)
        
        assert hash1 == hash2
    
    def test_hash_url_different_urls(self):
        """Test that different URLs produce different hashes"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page1", secret)
        hash2 = hash_url("https://example.com/page2", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_different_keys(self):
        """Test that different keys produce different hashes"""
        url = "https://example.com/page"
        
        hash1 = hash_url(url, "key1")
        hash2 = hash_url(url, "key2")
        
        assert hash1 != hash2
    
    def test_hash_url_case_sensitive(self):
        """Test that hashing is case sensitive"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/Page", secret)
        hash2 = hash_url("https://example.com/page", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_query_params(self):
        """Test hashing URLs with query parameters"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page?id=123", secret)
        hash2 = hash_url("https://example.com/page?id=456", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_with_fragment(self):
        """Test hashing URLs with fragments"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page#section1", secret)
        hash2 = hash_url("https://example.com/page#section2", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_empty_string(self):
        """Test hashing empty string"""
        secret = "my_secret_key"
        
        result = hash_url("", secret)
        
        assert result is not None
        assert len(result) == 64
    
    def test_hash_url_unicode(self):
        """Test hashing URLs with unicode characters"""
        secret = "my_secret_key"
        
        url = "https://example.com/页面"
        result = hash_url(url, secret)
        
        assert result is not None
        assert len(result) == 64
    
    def test_hash_url_special_characters(self):
        """Test hashing URLs with special characters"""
        secret = "my_secret_key"
        
        url = "https://example.com/page?name=John&email=test@example.com&token=abc123"
        result = hash_url(url, secret)
        
        assert result is not None
        assert len(result) == 64
    
    def test_hash_url_uses_env_variable(self):
        """Test that hash_url uses environment variable when key not provided"""
        url = "https://example.com/page"
        expected_key = "env_secret_key"
        
        with patch.dict(os.environ, {"SERVER_HMAC_KEY": expected_key}):
            result1 = hash_url(url)
            result2 = hash_url(url, expected_key)
            
            assert result1 == result2
    
    def test_hash_url_missing_env_variable(self):
        """Test that missing env variable raises ValueError"""
        url = "https://example.com/page"
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                hash_url(url)
            
            assert "SERVER_HMAC_KEY" in str(exc_info.value)
            assert "environment variable" in str(exc_info.value)
    
    def test_hash_url_error_message_helpful(self):
        """Test that error message is helpful"""
        url = "https://example.com/page"
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                hash_url(url)
            
            error_msg = str(exc_info.value)
            assert ".env" in error_msg or "environment variable" in error_msg
    
    def test_hash_url_hexadecimal_output(self):
        """Test that output is valid hexadecimal"""
        url = "https://example.com/page"
        secret = "my_secret_key"
        
        result = hash_url(url, secret)
        
        # Should only contain hex characters (0-9, a-f)
        assert all(c in "0123456789abcdef" for c in result)
    
    def test_hash_url_long_url(self):
        """Test hashing very long URL"""
        secret = "my_secret_key"
        long_url = "https://example.com/" + "a" * 10000
        
        result = hash_url(long_url, secret)
        
        assert result is not None
        assert len(result) == 64  # Hash length is constant
    
    def test_hash_url_whitespace_differences(self):
        """Test that whitespace differences affect hash"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page test", secret)
        hash2 = hash_url("https://example.com/page%20test", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_protocol_matters(self):
        """Test that protocol (http vs https) affects hash"""
        secret = "my_secret_key"
        
        hash1 = hash_url("http://example.com/page", secret)
        hash2 = hash_url("https://example.com/page", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_port_matters(self):
        """Test that port number affects hash"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com:80/page", secret)
        hash2 = hash_url("https://example.com:443/page", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_trailing_slash(self):
        """Test that trailing slash affects hash"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page", secret)
        hash2 = hash_url("https://example.com/page/", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_consistency_across_calls(self):
        """Test consistency across multiple calls"""
        url = "https://example.com/test"
        secret = "test_key"
        
        hashes = [hash_url(url, secret) for _ in range(10)]
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
    
    def test_hash_url_different_parameter_order(self):
        """Test that query parameter order affects hash"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/page?a=1&b=2", secret)
        hash2 = hash_url("https://example.com/page?b=2&a=1", secret)
        
        # HMAC is sensitive to exact byte sequence
        assert hash1 != hash2
    
    def test_hash_url_numeric_strings(self):
        """Test hashing URLs with numeric strings"""
        secret = "my_secret_key"
        
        hash1 = hash_url("https://example.com/123", secret)
        hash2 = hash_url("https://example.com/456", secret)
        
        assert hash1 != hash2
    
    def test_hash_url_special_domains(self):
        """Test hashing various domain types"""
        secret = "my_secret_key"
        
        domains = [
            "https://example.com",
            "https://subdomain.example.com",
            "https://example.co.uk",
            "https://localhost:8000",
            "https://192.168.1.1"
        ]
        
        hashes = [hash_url(domain, secret) for domain in domains]
        
        # All should produce unique hashes
        assert len(set(hashes)) == len(domains)
    
    def test_hash_url_with_credentials(self):
        """Test hashing URL with embedded credentials"""
        secret = "my_secret_key"
        
        url = "https://user:pass@example.com/page"
        result = hash_url(url, secret)
        
        assert result is not None
        assert len(result) == 64
    
    def test_hash_url_secret_key_types(self):
        """Test various secret key formats"""
        url = "https://example.com/page"
        
        keys = [
            "simple",
            "with spaces",
            "with-dashes",
            "with_underscores",
            "UPPERCASE",
            "MiXeDcAsE",
            "123456789",
            "special!@#$%^&*()",
        ]
        
        hashes = [hash_url(url, key) for key in keys]
        
        # All different keys should produce different hashes
        assert len(set(hashes)) == len(keys)
    
    def test_hash_url_empty_secret_produces_hash(self):
        """Test that empty secret still produces a hash (though not secure)"""
        url = "https://example.com/page"
        
        result = hash_url(url, "")
        
        assert result is not None
        assert len(result) == 64
