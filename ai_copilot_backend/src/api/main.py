import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .gemini_service import GeminiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Read allowed origins from environment variable
# Support FRONTEND_ORIGIN for explicit origin setting
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "")
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")

# Build allowed origins list
if FRONTEND_ORIGIN:
    # If FRONTEND_ORIGIN is set, use it as primary
    allowed_origins_list = [FRONTEND_ORIGIN]
elif ALLOWED_ORIGINS_ENV:
    # Parse comma-separated list
    allowed_origins_list = [o.strip() for o in ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
else:
    # Use wildcard for development if nothing is set
    allowed_origins_list = ["*"]

# Add localhost fallbacks for local development
if allowed_origins_list != ["*"]:
    localhost_origins = [
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4000"
    ]
    for origin in localhost_origins:
        if origin not in allowed_origins_list:
            allowed_origins_list.append(origin)

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for AI Copilot chat application with Gemini integration",
    version="0.1.0"
)

# Configure CORS to allow frontend origin
# This MUST be added before any routes to handle OPTIONS preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=False,  # Set to False unless cookies/auth are needed
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["Content-Type", "Authorization"],
)

# Log CORS configuration on startup
@app.on_event("startup")
async def startup_event():
    """Log configuration on startup for visibility."""
    logger.info("=" * 60)
    logger.info("AI Copilot Backend Starting")
    logger.info("=" * 60)
    if allowed_origins_list == ["*"]:
        logger.warning("CORS: Allowing ALL origins (*) - Development mode")
        logger.warning("Set FRONTEND_ORIGIN or ALLOWED_ORIGINS env var for production")
    else:
        logger.info("CORS: Configured allowed origins:")
        for origin in allowed_origins_list:
            logger.info(f"  - {origin}")
    logger.info("=" * 60)

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
    return {"message": "Healthy", "version": "0.1.0"}

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
        logger.info(f"Using Gemini model: {client.actual_model}")
    
    reply = await client.chat(req.message.strip())
    
    return ChatResponse(reply=reply)
