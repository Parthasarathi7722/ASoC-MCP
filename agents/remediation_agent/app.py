from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
import httpx
import paramiko
import json
from typing import List, Dict, Optional
import time

app = FastAPI(title="Remediation Agent")

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

class InvestigationResult(BaseModel):
    summary: str
    findings: List[Dict]
    confidence: float
    recommended_actions: List[str]

class RemediationRequest(BaseModel):
    alert: Alert
    investigation: Dict

class RemediationResult(BaseModel):
    actions_taken: List[Dict]
    status: str
    message: str
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

async def block_ip_firewall(ip: str) -> Dict:
    """Block an IP address in the firewall."""
    firewall_url = os.getenv("FIREWALL_API_URL")
    firewall_key = os.getenv("FIREWALL_API_KEY")
    
    if not firewall_url or not firewall_key:
        return {
            "action": "block_ip",
            "target": ip,
            "status": "skipped",
            "message": "Firewall API not configured"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{firewall_url}/block",
                json={"ip": ip},
                headers={"Authorization": f"Bearer {firewall_key}"}
            )
            
            if response.status_code == 200:
                return {
                    "action": "block_ip",
                    "target": ip,
                    "status": "success",
                    "message": "IP blocked successfully"
                }
            else:
                return {
                    "action": "block_ip",
                    "target": ip,
                    "status": "failed",
                    "message": f"Failed to block IP: {response.text}"
                }
    except Exception as e:
        return {
            "action": "block_ip",
            "target": ip,
            "status": "error",
            "message": f"Error blocking IP: {str(e)}"
        }

async def block_domain_dns(domain: str) -> Dict:
    """Block a domain in DNS."""
    # This would typically involve updating DNS or firewall rules
    # For demo purposes, we'll just return a success message
    return {
        "action": "block_domain",
        "target": domain,
        "status": "success",
        "message": "Domain blocked successfully (simulated)"
    }

async def isolate_host(host: str) -> Dict:
    """Isolate a host from the network."""
    # This would typically involve network segmentation or firewall rules
    # For demo purposes, we'll just return a success message
    return {
        "action": "isolate_host",
        "target": host,
        "status": "success",
        "message": "Host isolated successfully (simulated)"
    }

async def reset_password(username: str) -> Dict:
    """Reset a user's password."""
    # This would typically involve calling an identity management system
    # For demo purposes, we'll just return a success message
    return {
        "action": "reset_password",
        "target": username,
        "status": "success",
        "message": "Password reset successfully (simulated)"
    }

async def run_scan(host: str) -> Dict:
    """Run a security scan on a host."""
    # This would typically involve running a vulnerability scanner
    # For demo purposes, we'll just return a success message
    return {
        "action": "run_scan",
        "target": host,
        "status": "success",
        "message": "Security scan completed successfully (simulated)"
    }

async def execute_ssh_command(host: str, command: str) -> Dict:
    """Execute a command via SSH."""
    ssh_host = os.getenv("SSH_HOST")
    ssh_user = os.getenv("SSH_USER")
    ssh_key = os.getenv("SSH_KEY")
    
    if not all([ssh_host, ssh_user, ssh_key]):
        return {
            "action": "ssh_command",
            "target": host,
            "status": "skipped",
            "message": "SSH configuration not available"
        }
    
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the host
        ssh.connect(host, username=ssh_user, key_filename=ssh_key)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Get the output
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        # Close the connection
        ssh.close()
        
        if error:
            return {
                "action": "ssh_command",
                "target": host,
                "status": "failed",
                "message": f"Command failed: {error}"
            }
        else:
            return {
                "action": "ssh_command",
                "target": host,
                "status": "success",
                "message": f"Command executed successfully: {output}"
            }
    except Exception as e:
        return {
            "action": "ssh_command",
            "target": host,
            "status": "error",
            "message": f"SSH error: {str(e)}"
        }

@app.post("/remediate", response_model=RemediationResult)
async def remediate_alert(
    request: RemediationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Remediate a security alert based on investigation results.
    """
    try:
        actions_taken = []
        
        # Extract recommended actions from investigation
        recommended_actions = request.investigation.get("recommended_actions", [])
        
        # Process each recommended action
        for action in recommended_actions:
            action_result = {"action": "unknown", "status": "skipped", "message": "Action not implemented"}
            
            # Block IP action
            if action.startswith("Block indicator: ") and "ip" in action.lower():
                ip = action.split(": ")[1]
                action_result = await block_ip_firewall(ip)
            
            # Block domain action
            elif action.startswith("Block indicator: ") and "domain" in action.lower():
                domain = action.split(": ")[1]
                action_result = await block_domain_dns(domain)
            
            # Isolate host action
            elif "isolate" in action.lower() and "host" in action.lower():
                # Extract host from the action or use a default
                host = "target-host"  # In a real implementation, extract from action or alert
                action_result = await isolate_host(host)
            
            # Reset password action
            elif "reset" in action.lower() and "password" in action.lower():
                # Extract username from the action or use a default
                username = "target-user"  # In a real implementation, extract from action or alert
                action_result = await reset_password(username)
            
            # Run scan action
            elif "scan" in action.lower():
                # Extract host from the action or use a default
                host = "target-host"  # In a real implementation, extract from action or alert
                action_result = await run_scan(host)
            
            # Generic command execution
            elif "execute" in action.lower() and "command" in action.lower():
                # Extract command from the action or use a default
                command = "ls -la"  # In a real implementation, extract from action
                host = "target-host"  # In a real implementation, extract from alert
                action_result = await execute_ssh_command(host, command)
            
            actions_taken.append(action_result)
        
        # Determine overall status
        if not actions_taken:
            status = "skipped"
            message = "No remediation actions were taken"
        elif all(a["status"] == "success" for a in actions_taken):
            status = "success"
            message = "All remediation actions completed successfully"
        elif any(a["status"] == "error" for a in actions_taken):
            status = "error"
            message = "Some remediation actions failed with errors"
        else:
            status = "partial"
            message = "Some remediation actions were skipped or failed"
        
        # Create remediation result
        result = RemediationResult(
            actions_taken=actions_taken,
            status=status,
            message=message,
            timestamp=time.time()
        )
        
        # Store in Redis for potential future reference
        redis_client.set(
            f"remediation:{request.alert.source}:{request.alert.timestamp}",
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