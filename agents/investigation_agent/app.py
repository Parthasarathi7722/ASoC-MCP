from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
import httpx
from typing import List, Optional, Dict
import json

app = FastAPI(title="Investigation Agent")

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

class InvestigationRequest(BaseModel):
    alert: Alert
    triage: TriageResult
    threat_intel: Optional[Dict] = None

class InvestigationResult(BaseModel):
    summary: str
    findings: List[Dict]
    confidence: float
    recommended_actions: List[str]

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def query_llm_orchestrator(prompt: str) -> str:
    """Query the LLM Orchestrator for analysis."""
    llm_url = os.getenv("LLM_ORCHESTRATOR_URL", "http://llm_orchestrator:8000")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{llm_url}/ask",
                json={"prompt": prompt}
            )
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "Error querying LLM Orchestrator"
        except Exception:
            return "Error connecting to LLM Orchestrator"

def analyze_indicators(indicators: List[dict], threat_intel: Optional[Dict] = None) -> List[Dict]:
    """Analyze indicators with threat intelligence data."""
    findings = []
    
    for indicator in indicators:
        finding = {
            "indicator": indicator,
            "analysis": "No additional information available",
            "risk_level": "unknown"
        }
        
        # If threat intel is available, enrich the finding
        if threat_intel and "indicators" in threat_intel:
            for ti_indicator in threat_intel["indicators"]:
                if (ti_indicator["type"] == indicator["type"] and 
                    ti_indicator["value"] == indicator["value"]):
                    finding["analysis"] = ti_indicator.get("description", finding["analysis"])
                    finding["risk_level"] = ti_indicator.get("risk_level", finding["risk_level"])
                    break
        
        findings.append(finding)
    
    return findings

def generate_recommended_actions(findings: List[Dict], severity: str) -> List[str]:
    """Generate recommended actions based on findings and severity."""
    actions = []
    
    # Add severity-based actions
    if severity == "high":
        actions.append("Escalate to security team immediately")
        actions.append("Initiate incident response plan")
    elif severity == "medium":
        actions.append("Review and analyze in detail")
        actions.append("Monitor for similar events")
    
    # Add indicator-based actions
    for finding in findings:
        if finding["risk_level"] == "high":
            actions.append(f"Block indicator: {finding['indicator']['value']}")
        elif finding["risk_level"] == "medium":
            actions.append(f"Monitor indicator: {finding['indicator']['value']}")
    
    # Add general actions
    actions.append("Update security documentation")
    actions.append("Review and update detection rules")
    
    return list(set(actions))  # Remove duplicates

@app.post("/investigate", response_model=InvestigationResult)
async def investigate_alert(
    request: InvestigationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Investigate a security alert with triage results and threat intelligence.
    """
    try:
        # Prepare data for LLM analysis
        alert_data = request.alert.dict()
        triage_data = request.triage.dict()
        threat_intel_data = request.threat_intel or {}
        
        # Create a prompt for the LLM
        prompt = f"""
        Analyze this security alert and provide a detailed investigation:
        
        Alert: {json.dumps(alert_data)}
        Triage: {json.dumps(triage_data)}
        Threat Intelligence: {json.dumps(threat_intel_data)}
        
        Provide a concise summary of the investigation findings.
        """
        
        # Get LLM analysis
        llm_summary = await query_llm_orchestrator(prompt)
        
        # Analyze indicators
        findings = analyze_indicators(request.triage.indicators, request.threat_intel)
        
        # Generate recommended actions
        recommended_actions = generate_recommended_actions(findings, request.triage.severity)
        
        # Calculate confidence based on available data
        confidence = 0.7  # Base confidence
        if request.threat_intel:
            confidence += 0.2  # Increase confidence if threat intel is available
        if len(findings) > 0:
            confidence += 0.1  # Increase confidence if indicators were found
        
        # Create investigation result
        investigation_result = InvestigationResult(
            summary=llm_summary,
            findings=findings,
            confidence=min(confidence, 1.0),  # Cap at 1.0
            recommended_actions=recommended_actions
        )
        
        # Store in Redis for potential future reference
        redis_client.set(
            f"investigation:{request.alert.source}:{request.alert.timestamp}",
            json.dumps(investigation_result.dict())
        )
        
        return investigation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 