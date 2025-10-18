import httpx


async def get_location_from_ip(ip_address: str) -> dict:
    if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
        return {"country": "Unknown", "city": "Unknown", "region": "Unknown"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip_address}", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    return {
                        "country": data.get("country", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "region": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
                    }
    except Exception as e:
        pass
    
    return {"country": "Unknown", "city": "Unknown", "region": "Unknown"}
