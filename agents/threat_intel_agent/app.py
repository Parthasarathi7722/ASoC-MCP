from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
import httpx
import requests
from typing import List, Dict, Optional
import json

app = FastAPI(title="Threat Intel Agent")

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# OAuth2 scheme for JWT validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth-service:8000/token")

class Indicator(BaseModel):
    type: str
    value: str

class EnrichmentRequest(BaseModel):
    indicators: List[Indicator]

class EnrichmentResult(BaseModel):
    indicators: List[Dict]
    sources: List[str]
    timestamp: float

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def query_virustotal(indicator: Indicator) -> Optional[Dict]:
    """Query VirusTotal API for threat intelligence."""
    vt_api_key = os.getenv("VT_API_KEY")
    if not vt_api_key:
        return None
    
    headers = {
        "x-apikey": vt_api_key
    }
    
    # Determine the appropriate endpoint based on indicator type
    if indicator.type == "ip":
        endpoint = f"https://www.virustotal.com/api/v3/ip_addresses/{indicator.value}"
    elif indicator.type == "domain":
        endpoint = f"https://www.virustotal.com/api/v3/domains/{indicator.value}"
    elif indicator.type == "hash":
        endpoint = f"https://www.virustotal.com/api/v3/files/{indicator.value}"
    elif indicator.type == "url":
        # For URLs, we need to encode it
        import base64
        encoded_url = base64.urlsafe_b64encode(indicator.value.encode()).decode().strip("=")
        endpoint = f"https://www.virustotal.com/api/v3/urls/{encoded_url}"
    else:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                result = {
                    "type": indicator.type,
                    "value": indicator.value,
                    "description": "VirusTotal Analysis",
                    "risk_level": "unknown",
                    "details": {}
                }
                
                # Determine risk level based on detection ratio
                if "data" in data and "attributes" in data["data"]:
                    attrs = data["data"]["attributes"]
                    
                    if "last_analysis_stats" in attrs:
                        stats = attrs["last_analysis_stats"]
                        malicious = stats.get("malicious", 0)
                        total = sum(stats.values())
                        
                        if total > 0:
                            ratio = malicious / total
                            if ratio > 0.5:
                                result["risk_level"] = "high"
                            elif ratio > 0.1:
                                result["risk_level"] = "medium"
                            else:
                                result["risk_level"] = "low"
                    
                    # Add additional details
                    result["details"] = {
                        "first_seen": attrs.get("first_submission_date"),
                        "last_seen": attrs.get("last_analysis_date"),
                        "reputation": attrs.get("reputation"),
                        "tags": attrs.get("tags", [])
                    }
                
                return result
    except Exception:
        return None
    
    return None

async def query_abuseipdb(indicator: Indicator) -> Optional[Dict]:
    """Query AbuseIPDB API for IP intelligence."""
    if indicator.type != "ip":
        return None
    
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        return None
    
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.abuseipdb.com/api/v2/check",
                params={"ipAddress": indicator.value, "maxAgeInDays": 90},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "type": "ip",
                    "value": indicator.value,
                    "description": "AbuseIPDB Analysis",
                    "risk_level": "unknown",
                    "details": {}
                }
                
                # Determine risk level based on abuse confidence score
                if "data" in data:
                    confidence_score = data["data"].get("abuseConfidenceScore", 0)
                    
                    if confidence_score > 50:
                        result["risk_level"] = "high"
                    elif confidence_score > 25:
                        result["risk_level"] = "medium"
                    else:
                        result["risk_level"] = "low"
                    
                    # Add additional details
                    result["details"] = {
                        "country": data["data"].get("countryCode"),
                        "isp": data["data"].get("isp"),
                        "usage_type": data["data"].get("usageType"),
                        "total_reports": data["data"].get("totalReports"),
                        "last_reported": data["data"].get("lastReportedAt")
                    }
                
                return result
    except Exception:
        return None
    
    return None

async def query_whois(indicator: Indicator) -> Optional[Dict]:
    """Query WHOIS data for domain intelligence."""
    if indicator.type != "domain":
        return None
    
    try:
        # Use a WHOIS API service
        api_key = os.getenv("WHOIS_API_KEY")
        if not api_key:
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://whois.whoisxmlapi.com/api/v1",
                params={"apiKey": api_key, "domainName": indicator.value}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "type": "domain",
                    "value": indicator.value,
                    "description": "WHOIS Analysis",
                    "risk_level": "low",  # WHOIS data is typically low risk
                    "details": {}
                }
                
                # Extract relevant information
                if "WhoisRecord" in data:
                    record = data["WhoisRecord"]
                    result["details"] = {
                        "registrar": record.get("registrarName"),
                        "creation_date": record.get("creationDate"),
                        "expiration_date": record.get("expirationDate"),
                        "name_servers": record.get("nameServers", {}).get("hostNames", [])
                    }
                
                return result
    except Exception:
        return None
    
    return None

@app.post("/enrich", response_model=EnrichmentResult)
async def enrich_indicators(
    request: EnrichmentRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Enrich security indicators with threat intelligence data.
    """
    try:
        enriched_indicators = []
        sources = []
        
        for indicator in request.indicators:
            # Try different intelligence sources based on indicator type
            if indicator.type == "ip":
                # Try AbuseIPDB first
                result = await query_abuseipdb(indicator)
                if result:
                    enriched_indicators.append(result)
                    if "AbuseIPDB" not in sources:
                        sources.append("AbuseIPDB")
                
                # Then try VirusTotal
                result = await query_virustotal(indicator)
                if result:
                    enriched_indicators.append(result)
                    if "VirusTotal" not in sources:
                        sources.append("VirusTotal")
            
            elif indicator.type == "domain":
                # Try WHOIS first
                result = await query_whois(indicator)
                if result:
                    enriched_indicators.append(result)
                    if "WHOIS" not in sources:
                        sources.append("WHOIS")
                
                # Then try VirusTotal
                result = await query_virustotal(indicator)
                if result:
                    enriched_indicators.append(result)
                    if "VirusTotal" not in sources:
                        sources.append("VirusTotal")
            
            elif indicator.type in ["hash", "url"]:
                # Try VirusTotal
                result = await query_virustotal(indicator)
                if result:
                    enriched_indicators.append(result)
                    if "VirusTotal" not in sources:
                        sources.append("VirusTotal")
            
            # If no enrichment was found, add the original indicator
            if not any(ei["value"] == indicator.value for ei in enriched_indicators):
                enriched_indicators.append({
                    "type": indicator.type,
                    "value": indicator.value,
                    "description": "No additional information available",
                    "risk_level": "unknown",
                    "details": {}
                })
        
        # Create enrichment result
        import time
        result = EnrichmentResult(
            indicators=enriched_indicators,
            sources=sources,
            timestamp=time.time()
        )
        
        # Store in Redis for potential future reference
        redis_client.set(
            f"threat_intel:{','.join([i.value for i in request.indicators])}",
            json.dumps(result.dict())
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 