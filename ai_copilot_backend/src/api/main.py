import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .gemini_service import GeminiClient

# Configure module-level logger (concise, safe logging)
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Basic configuration only if not set by the runtime
    logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Read allowed origins from environment variable (comma-separated), trimming whitespace
# Default to the specified origin if not set
raw = os.getenv('ALLOWED_ORIGINS', 'https://vscode-internal-26947-beta.beta01.cloud.kavia.ai:4000')
ALLOWED_ORIGINS = [o.strip() for o in raw.split(',') if o.strip()]

# Log resolved origins immediately after env is loaded (no secrets)
logger.info("CORS ALLOWED_ORIGINS (env-load): %s", ALLOWED_ORIGINS)

# Development mode detection
DEV_MODE = os.getenv("ENV", "development").lower() == "development"

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for AI Copilot chat application with Gemini integration",
    version="0.1.0"
)

# Parse configured origins (already trimmed)
configured_origins = ALLOWED_ORIGINS

# Dev-friendly CORS: In development, also allow specific preview domains pattern for ports 3000/4000
if DEV_MODE:
    logger.info("[CORS] Development mode: enabling preview-domain allowance for ports 3000/4000 matching vscode-internal-<id>-beta.beta01.cloud.kavia.ai")
    
    # Middleware with custom origin validation (adds headers for matched dev origins too)
    @app.middleware("http")
    async def cors_dev_middleware(request, call_next):
        origin = request.headers.get("origin")
        
        # Check if origin matches configured list or dev pattern
        allowed = False
        if origin and origin in configured_origins:
            allowed = True
        elif origin and DEV_MODE:
            pattern = r'^https://vscode-internal-\d+-beta\.beta01\.cloud\.kavia\.ai:(3000|4000)$'
            if re.match(pattern, origin):
                allowed = True
                logger.info("[CORS] Dev pattern match allowed for origin: %s", origin)
        
        response = await call_next(request)
        
        # Add CORS headers if allowed
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response

# Standard CORS middleware (for OPTIONS handling and baseline CORS)
# Ensure we don't use wildcard '*' when allow_credentials=True; use the env-driven list.
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Log again on application startup to confirm runtime value
@app.on_event("startup")
async def log_cors_config_startup():
    """
    Confirm the active CORS configuration at application startup.
    Prints only the list of allowed origins, no secrets.
    """
    logger.info("CORS ALLOWED_ORIGINS (startup): %s", configured_origins)

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
        logger.info("Using Gemini model: %s", client.actual_model)
    
    reply = await client.chat(req.message.strip())
    
    return ChatResponse(reply=reply)
