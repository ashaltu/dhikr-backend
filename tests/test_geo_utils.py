import pytest
from unittest.mock import AsyncMock, patch, Mock
from app.services.geo_utils import get_location_from_ip


class TestGetLocationFromIP:
    """Tests for IP geolocation functionality"""
    
    @pytest.mark.asyncio
    async def test_localhost_returns_unknown(self):
        """Test that localhost returns Unknown location"""
        result = await get_location_from_ip("127.0.0.1")
        assert result["country"] == "Unknown"
        assert result["city"] == "Unknown"
        assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_localhost_ipv6_returns_unknown(self):
        """Test that IPv6 localhost returns Unknown"""
        result = await get_location_from_ip("::1")
        assert result["country"] == "Unknown"
        assert result["city"] == "Unknown"
        assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_localhost_string_returns_unknown(self):
        """Test that 'localhost' string returns Unknown"""
        result = await get_location_from_ip("localhost")
        assert result["country"] == "Unknown"
        assert result["city"] == "Unknown"
        assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_empty_ip_returns_unknown(self):
        """Test that empty IP returns Unknown"""
        result = await get_location_from_ip("")
        assert result["country"] == "Unknown"
        assert result["city"] == "Unknown"
        assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_none_ip_returns_unknown(self):
        """Test that None IP returns Unknown"""
        result = await get_location_from_ip(None)
        assert result["country"] == "Unknown"
        assert result["city"] == "Unknown"
        assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_successful_geolocation(self):
        """Test successful geolocation response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "United States",
            "city": "New York"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            assert result["country"] == "United States"
            assert result["city"] == "New York"
            assert result["region"] == "New York, United States"
    
    @pytest.mark.asyncio
    async def test_api_failure_status(self):
        """Test API returns failure status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "fail",
            "message": "invalid query"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("invalid.ip")
            
            assert result["country"] == "Unknown"
            assert result["city"] == "Unknown"
            assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_http_error_status_code(self):
        """Test non-200 status code"""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("1.2.3.4")
            
            assert result["country"] == "Unknown"
            assert result["city"] == "Unknown"
            assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Test network timeout handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Timeout")
            )
            
            result = await get_location_from_ip("1.2.3.4")
            
            assert result["country"] == "Unknown"
            assert result["city"] == "Unknown"
            assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_missing_country_field(self):
        """Test response missing country field"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "city": "London"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            assert result["country"] == "Unknown"
            assert result["city"] == "London"
            assert result["region"] == "London, Unknown"
    
    @pytest.mark.asyncio
    async def test_missing_city_field(self):
        """Test response missing city field"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "Canada"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            assert result["country"] == "Canada"
            assert result["city"] == "Unknown"
            assert result["region"] == "Unknown, Canada"
    
    @pytest.mark.asyncio
    async def test_json_decode_error(self):
        """Test invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            assert result["country"] == "Unknown"
            assert result["city"] == "Unknown"
            assert result["region"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_complete_location_data(self):
        """Test complete location data with all fields"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "United Kingdom",
            "city": "London",
            "regionName": "England",
            "zip": "EC1A",
            "lat": 51.5074,
            "lon": -0.1278
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            assert result["country"] == "United Kingdom"
            assert result["city"] == "London"
            assert result["region"] == "London, United Kingdom"
    
    @pytest.mark.asyncio
    async def test_timeout_parameter(self):
        """Test that timeout parameter is set correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "France",
            "city": "Paris"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            await get_location_from_ip("1.2.3.4")
            
            # Verify timeout is set to 5.0 seconds
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.kwargs.get("timeout") == 5.0
    
    @pytest.mark.asyncio
    async def test_correct_api_endpoint(self):
        """Test that correct API endpoint is called"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "Germany",
            "city": "Berlin"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            test_ip = "1.2.3.4"
            await get_location_from_ip(test_ip)
            
            # Verify correct URL is called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert f"http://ip-api.com/json/{test_ip}" in call_args[0]
    
    @pytest.mark.asyncio
    async def test_private_ip_ranges(self):
        """Test various private IP ranges"""
        # Note: These should still attempt lookup (current implementation)
        # but in production might want to handle them like localhost
        private_ips = ["10.0.0.1", "172.16.0.1", "192.168.1.1"]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "fail",
            "message": "private range"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            for ip in private_ips:
                result = await get_location_from_ip(ip)
                assert result["country"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_region_format(self):
        """Test that region is formatted correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "Japan",
            "city": "Tokyo"
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_location_from_ip("8.8.8.8")
            
            # Region should be "city, country"
            assert result["region"] == "Tokyo, Japan"
            assert ", " in result["region"]
