from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
import os
import redis
import httpx
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Union
import asyncio
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader

app = FastAPI(title="Notifications Service")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# OAuth2 scheme for JWT validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth-service:8000/token")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "notifications@example.com")

# Slack configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Initialize Jinja2 environment for email templates
env = Environment(loader=FileSystemLoader("templates"))

# Models
class NotificationRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    message: str
    notification_type: str = "email"  # email, slack, or both
    template_name: Optional[str] = None
    template_data: Optional[Dict] = None
    priority: str = "normal"  # low, normal, high, urgent

class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    message: str
    timestamp: str

class NotificationStatus(BaseModel):
    notification_id: str
    status: str
    sent_to: List[str]
    failed_to: List[str]
    timestamp: str

# Mock user database for demo purposes
# In a real application, this would be fetched from a database
user_preferences = {
    "admin@example.com": {
        "email": True,
        "slack": True,
        "priority": "high"
    },
    "analyst@example.com": {
        "email": True,
        "slack": False,
        "priority": "normal"
    },
    "user@example.com": {
        "email": True,
        "slack": False,
        "priority": "low"
    }
}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def send_email(recipients: List[str], subject: str, body: str):
    """Send an email to the specified recipients."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured, email sending simulated")
        return True
    
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent to {recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

async def send_slack_notification(message: str):
    """Send a notification to Slack."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured, Slack notification simulated")
        return True
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SLACK_WEBHOOK_URL,
                json={"text": message}
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")
        return False

def render_template(template_name: str, data: Dict) -> str:
    """Render an email template with the provided data."""
    try:
        template = env.get_template(f"{template_name}.html")
        return template.render(**data)
    except Exception as e:
        logger.error(f"Failed to render template: {str(e)}")
        return data.get("message", "Notification")

async def process_notification(
    notification_id: str,
    recipients: List[str],
    subject: str,
    message: str,
    notification_type: str,
    template_name: Optional[str],
    template_data: Optional[Dict],
    priority: str
):
    """Process a notification in the background."""
    sent_to = []
    failed_to = []
    
    # Render template if provided
    if template_name and template_data:
        message = render_template(template_name, template_data)
    
    # Send email notifications
    if notification_type in ["email", "both"]:
        for recipient in recipients:
            if await send_email([recipient], subject, message):
                sent_to.append(recipient)
            else:
                failed_to.append(recipient)
    
    # Send Slack notifications
    if notification_type in ["slack", "both"]:
        slack_message = f"*{subject}*\n{message}"
        if await send_slack_notification(slack_message):
            sent_to.append("slack")
        else:
            failed_to.append("slack")
    
    # Update notification status in Redis
    status = "completed" if not failed_to else "partial" if sent_to else "failed"
    notification_status = {
        "notification_id": notification_id,
        "status": status,
        "sent_to": sent_to,
        "failed_to": failed_to,
        "timestamp": datetime.now().isoformat()
    }
    
    redis_client.set(
        f"notification:{notification_id}",
        json.dumps(notification_status),
        ex=86400  # Expire after 24 hours
    )
    
    logger.info(f"Notification {notification_id} processed with status: {status}")

@app.post("/notify", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """
    Send a notification to the specified recipients.
    """
    try:
        # Generate a unique notification ID
        import uuid
        notification_id = str(uuid.uuid4())
        
        # Add notification to background tasks
        background_tasks.add_task(
            process_notification,
            notification_id,
            request.recipients,
            request.subject,
            request.message,
            request.notification_type,
            request.template_name,
            request.template_data,
            request.priority
        )
        
        # Store initial notification status
        initial_status = {
            "notification_id": notification_id,
            "status": "pending",
            "sent_to": [],
            "failed_to": [],
            "timestamp": datetime.now().isoformat()
        }
        
        redis_client.set(
            f"notification:{notification_id}",
            json.dumps(initial_status),
            ex=86400  # Expire after 24 hours
        )
        
        return NotificationResponse(
            notification_id=notification_id,
            status="pending",
            message="Notification queued for delivery",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/notifications/{notification_id}", response_model=NotificationStatus)
async def get_notification_status(
    notification_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get the status of a notification.
    """
    try:
        notification_data = redis_client.get(f"notification:{notification_id}")
        
        if not notification_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return NotificationStatus(**json.loads(notification_data))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/templates")
async def list_templates(current_user: str = Depends(get_current_user)):
    """
    List available notification templates.
    """
    try:
        templates = []
        for template in env.list_templates():
            if template.endswith(".html"):
                templates.append(template.replace(".html", ""))
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 