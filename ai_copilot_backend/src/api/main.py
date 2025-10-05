import os
import re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .gemini_service import GeminiClient

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Read allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://vscode-internal-38356-beta.beta01.cloud.kavia.ai:3000").split(",")

# Development mode detection
DEV_MODE = os.getenv("ENV", "development").lower() == "development"

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for AI Copilot chat application with Gemini integration",
    version="0.1.0"
)

# Parse configured origins
configured_origins = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

# Dev-friendly CORS: In development, also allow *.beta01.cloud.kavia.ai with ports 3000/4000
if DEV_MODE:
    print("[CORS] Development mode: allowing *.beta01.cloud.kavia.ai with ports 3000/4000")
    
    # Middleware with custom origin validation
    @app.middleware("http")
    async def cors_dev_middleware(request, call_next):
        origin = request.headers.get("origin")
        
        # Check if origin matches dev pattern
        allowed = False
        if origin in configured_origins:
            allowed = True
        elif origin and DEV_MODE:
            # Allow preview domains with ports 3000 or 4000
            pattern = r'^https://vscode-internal-\d+-beta\.beta01\.cloud\.kavia\.ai:(3000|4000)$'
            if re.match(pattern, origin):
                allowed = True
                print(f"[CORS] Dev pattern match: {origin}")
        
        response = await call_next(request)
        
        # Add CORS headers if allowed
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response

# Standard CORS middleware (as fallback and for OPTIONS handling)
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    reply: str

# PUBLIC_INTERFACE
@app.get("/")
async def root():
    """Root endpoint redirect to health check."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/api/health")
async def health():
    """
    Health check endpoint.
    
    Returns:
        Status message indicating service health
    """
    return {"status": "ok"}

# PUBLIC_INTERFACE
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat endpoint for sending messages to AI assistant.
    
    Args:
        req: ChatRequest containing the user's message
        
    Returns:
        ChatResponse with AI-generated reply
        
    Raises:
        HTTPException: If message is empty or invalid
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Initialize Gemini client and get response
    client = GeminiClient()
    
    # Log which model is being used (without exposing API key)
    if client.usable:
        print(f"[INFO] Using Gemini model: {client.actual_model}")
    
    reply = await client.chat(req.message.strip())
    
    return ChatResponse(reply=reply)
