from celery import Celery
import os
import httpx
import json
from typing import Dict, List

# Initialize Celery app
celery_app = Celery(
    "mcp_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://memory:6379/0")
)

@celery_app.task(name="playbook.investigate")
def run_investigation_task(alert: Dict, triage: Dict, threat_intel: Dict) -> Dict:
    """Background task to run investigation agent."""
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://investigation-agent:8000/investigate",
                json={
                    "alert": alert,
                    "triage": triage,
                    "threat_intel": threat_intel
                }
            )
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@celery_app.task(name="playbook.remediate")
def run_remediation_task(alert: Dict, investigation: Dict) -> Dict:
    """Background task to run remediation agent."""
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://remediation-agent:8000/remediate",
                json={
                    "alert": alert,
                    "investigation": investigation
                }
            )
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@celery_app.task(name="playbook.threat_intel")
def run_threat_intel_task(indicators: List[Dict]) -> Dict:
    """Background task to run threat intelligence enrichment."""
    if not indicators:
        return {}
    
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://threat-intel-agent:8000/enrich",
                json={"indicators": indicators}
            )
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@celery_app.task(name="notifications.send")
def send_notification_task(message: str, channels: List[str] = ["slack", "email"]):
    """Background task to send notifications."""
    try:
        with httpx.Client() as client:
            client.post(
                "http://notifications:8000/notify",
                json={"message": message, "channels": channels}
            )
    except Exception:
        # Log error but don't fail the task
        pass 