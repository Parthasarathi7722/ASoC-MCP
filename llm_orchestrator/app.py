from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import redis
import openai
from typing import Optional, List
import json

app = FastAPI(title="LLM Orchestrator")

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# OAuth2 scheme for JWT validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth-service:8000/token")

class LLMRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    context: Optional[dict] = None

class LLMResponse(BaseModel):
    response: str
    context_used: Optional[dict] = None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@app.post("/ask", response_model=LLMResponse)
async def ask_llm(
    request: LLMRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Ask the LLM a question with optional context from memory.
    """
    # Get context from memory if session_id provided
    context = {}
    if request.session_id:
        stored_context = redis_client.get(f"session:{request.session_id}:context")
        if stored_context:
            context = json.loads(stored_context)
    
    # Merge provided context with stored context
    if request.context:
        context.update(request.context)
    
    # Prepare the prompt with context
    full_prompt = f"Context: {json.dumps(context)}\n\nQuestion: {request.prompt}"
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity assistant helping with incident response."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # Store updated context if session_id provided
        if request.session_id:
            redis_client.set(
                f"session:{request.session_id}:context",
                json.dumps(context)
            )
        
        return LLMResponse(
            response=answer,
            context_used=context if context else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calling LLM: {str(e)}"
        )

@app.post("/analyze_log")
async def analyze_log(
    log_data: dict,
    current_user: str = Depends(get_current_user)
):
    """
    Analyze a security log entry using the LLM.
    """
    try:
        # Format the log data for the LLM
        prompt = f"""
        Analyze this security log entry and provide:
        1. Severity level (Low/Medium/High)
        2. Potential threat type
        3. Recommended actions
        
        Log data: {json.dumps(log_data)}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security analyst analyzing log entries."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            "analysis": response.choices[0].message.content
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing log: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 