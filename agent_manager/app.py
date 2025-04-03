from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
import httpx
from typing import Optional, List, Dict
import json
from datetime import datetime

app = FastAPI(title="Agent Manager")

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

async def call_triage_agent(alert: Alert) -> TriageResult:
    """Call the Triage Agent to classify an alert."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://triage-agent:8000/triage",
            json=alert.dict()
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error calling Triage Agent"
            )
        return TriageResult(**response.json())

async def call_threat_intel(indicators: List[dict]) -> dict:
    """Call the Threat Intel Agent to enrich indicators."""
    if not indicators:
        return {}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://threat-intel-agent:8000/enrich",
            json={"indicators": indicators}
        )
        if response.status_code != 200:
            return {}  # Return empty if threat intel fails
        return response.json()

async def call_investigation(alert: Alert, triage: TriageResult, threat_intel: dict) -> dict:
    """Call the Investigation Agent for deeper analysis."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://investigation-agent:8000/investigate",
            json={
                "alert": alert.dict(),
                "triage": triage.dict(),
                "threat_intel": threat_intel
            }
        )
        if response.status_code != 200:
            return {"error": "Investigation failed"}
        return response.json()

async def call_remediation(alert: Alert, investigation: dict) -> dict:
    """Call the Remediation Agent for response actions."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://remediation-agent:8000/remediate",
            json={
                "alert": alert.dict(),
                "investigation": investigation
            }
        )
        if response.status_code != 200:
            return {"error": "Remediation failed"}
        return response.json()

async def send_notification(message: str, channels: List[str] = ["slack", "email"]):
    """Send notification via the Notifications service."""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://notifications:8000/notify",
                json={"message": message, "channels": channels}
            )
        except Exception:
            # Log error but don't fail the workflow
            pass

@app.post("/alert")
async def process_alert(
    alert: Alert,
    current_user: str = Depends(get_current_user)
):
    """
    Process a new security alert through the workflow.
    """
    try:
        # Store alert in memory
        alert_id = f"alert:{datetime.now().timestamp()}"
        redis_client.set(alert_id, json.dumps(alert.dict()))
        
        # Step 1: Triage
        triage_result = await call_triage_agent(alert)
        redis_client.set(f"{alert_id}:triage", json.dumps(triage_result.dict()))
        
        # Step 2: Threat Intelligence (if indicators found)
        threat_intel = await call_threat_intel(triage_result.indicators)
        if threat_intel:
            redis_client.set(f"{alert_id}:threat_intel", json.dumps(threat_intel))
        
        # Step 3: Investigation
        investigation = await call_investigation(alert, triage_result, threat_intel)
        redis_client.set(f"{alert_id}:investigation", json.dumps(investigation))
        
        # Step 4: Remediation
        remediation = await call_remediation(alert, investigation)
        redis_client.set(f"{alert_id}:remediation", json.dumps(remediation))
        
        # Send notification
        notification = f"""
        New Security Alert Processed:
        - Source: {alert.source}
        - Type: {alert.event_type}
        - Severity: {triage_result.severity}
        - Category: {triage_result.category}
        
        Investigation Findings:
        {investigation.get('summary', 'No summary available')}
        
        Recommended Actions:
        {remediation.get('recommended_actions', ['No actions recommended'])}
        """
        await send_notification(notification)
        
        return {
            "alert_id": alert_id,
            "status": "completed",
            "triage": triage_result.dict(),
            "investigation": investigation,
            "remediation": remediation
        }
        
    except Exception as e:
        # Send notification about failure
        await send_notification(
            f"Error processing alert from {alert.source}: {str(e)}",
            channels=["slack"]  # Only notify on Slack for errors
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/alert/{alert_id}")
async def get_alert_status(
    alert_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get the status and results of a processed alert.
    """
    try:
        # Get all components from memory
        alert_data = redis_client.get(alert_id)
        if not alert_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
            
        triage_data = redis_client.get(f"{alert_id}:triage")
        threat_intel_data = redis_client.get(f"{alert_id}:threat_intel")
        investigation_data = redis_client.get(f"{alert_id}:investigation")
        remediation_data = redis_client.get(f"{alert_id}:remediation")
        
        return {
            "alert": json.loads(alert_data),
            "triage": json.loads(triage_data) if triage_data else None,
            "threat_intel": json.loads(threat_intel_data) if threat_intel_data else None,
            "investigation": json.loads(investigation_data) if investigation_data else None,
            "remediation": json.loads(remediation_data) if remediation_data else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 