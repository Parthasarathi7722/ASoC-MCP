from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
from typing import List, Optional
import json

app = FastAPI(title="Triage Agent")

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# OAuth2 scheme for JWT validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth-service:8000/token")

class Alert(BaseModel):
    source: str
    event_type: str
    timestamp: float
    details: dict

class TriageResult(BaseModel):
    category: str
    severity: str
    indicators: List[dict]

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def extract_indicators(alert: Alert) -> List[dict]:
    """Extract potential indicators from the alert details."""
    indicators = []
    details = alert.details
    
    # Common indicator patterns
    if "ip" in details:
        indicators.append({"type": "ip", "value": details["ip"]})
    if "domain" in details:
        indicators.append({"type": "domain", "value": details["domain"]})
    if "hash" in details:
        indicators.append({"type": "hash", "value": details["hash"]})
    if "url" in details:
        indicators.append({"type": "url", "value": details["url"]})
    if "user" in details:
        indicators.append({"type": "user", "value": details["user"]})
    
    return indicators

def determine_severity(event_type: str, details: dict) -> str:
    """Determine alert severity based on event type and details."""
    event_type = event_type.lower()
    
    # High severity events
    if any(term in event_type for term in ["malware", "ransomware", "breach", "exploit"]):
        return "high"
    
    # Medium severity events
    if any(term in event_type for term in ["failed", "error", "warning", "suspicious"]):
        return "medium"
    
    # Check details for severity indicators
    if "severity" in details:
        sev = details["severity"].lower()
        if sev in ["critical", "high"]:
            return "high"
        if sev in ["medium", "moderate"]:
            return "medium"
    
    return "low"

def categorize_alert(event_type: str, details: dict) -> str:
    """Categorize the alert based on event type and details."""
    event_type = event_type.lower()
    
    # Define category mappings
    categories = {
        "authentication": ["login", "auth", "password", "credential"],
        "malware": ["malware", "virus", "ransomware", "trojan"],
        "network": ["firewall", "network", "connection", "traffic"],
        "access": ["access", "permission", "authorization"],
        "system": ["system", "host", "endpoint", "machine"],
        "application": ["app", "application", "service", "api"],
        "data": ["data", "file", "document", "database"],
        "compliance": ["compliance", "audit", "policy", "regulation"]
    }
    
    # Check event type against categories
    for category, keywords in categories.items():
        if any(keyword in event_type for keyword in keywords):
            return category
    
    # Check details for category indicators
    if "category" in details:
        return details["category"].lower()
    
    return "other"

@app.post("/triage", response_model=TriageResult)
async def triage_alert(
    alert: Alert,
    current_user: str = Depends(get_current_user)
):
    """
    Triage a security alert by determining its category, severity, and extracting indicators.
    """
    try:
        # Extract indicators
        indicators = extract_indicators(alert)
        
        # Determine severity
        severity = determine_severity(alert.event_type, alert.details)
        
        # Categorize the alert
        category = categorize_alert(alert.event_type, alert.details)
        
        # Store triage result in memory
        triage_result = TriageResult(
            category=category,
            severity=severity,
            indicators=indicators
        )
        
        # Store in Redis for potential future reference
        redis_client.set(
            f"triage:{alert.source}:{alert.timestamp}",
            json.dumps(triage_result.dict())
        )
        
        return triage_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 