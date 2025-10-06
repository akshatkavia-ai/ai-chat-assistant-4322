"""
AI Copilot Backend - FastAPI Application

Main application module providing REST API endpoints for AI chat functionality.
Includes Gemini integration, CORS configuration, and comprehensive error handling.
"""
import os
import re
import time
import logging
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from .gemini_service import GeminiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
logger.info(f"Loading environment from: {env_path}")

# Resolve allowed origins from environment
env_origins_str = os.getenv("ALLOWED_ORIGINS", "").strip()
env_origins = [origin.strip() for origin in env_origins_str.split(",") if origin.strip()]

# Default fallback origin for development
default_origin = "http://localhost:3000"

# Use env origins if provided, otherwise use default
ALLOWED_ORIGINS = env_origins if env_origins else [default_origin]

logger.info(f"ALLOWED_ORIGINS configured: {ALLOWED_ORIGINS}")

# Development mode detection
ENV_MODE = os.getenv("ENV", "development").lower()
DEV_MODE = ENV_MODE == "development"

if DEV_MODE:
    logger.info("Running in DEVELOPMENT mode - enhanced CORS enabled")
else:
    logger.info("Running in PRODUCTION mode")

# Initialize FastAPI application
app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for AI Copilot chat application with Gemini integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# In development mode, add middleware to handle dynamic preview domains
if DEV_MODE:
    @app.middleware("http")
    async def dev_cors_middleware(request: Request, call_next):
        """
        Development CORS middleware for handling dynamic preview domains.
        
        Allows origins matching the pattern:
        https://vscode-internal-{port}-beta.beta01.cloud.kavia.ai:{3000|4000}
        """
        origin = request.headers.get("origin", "")
        allowed = False
        
        # Check if origin is in configured list
        if origin in ALLOWED_ORIGINS:
            allowed = True
            logger.debug(f"Origin allowed by config: {origin}")
        elif origin:
            # Allow preview origins on ports 3000 and 4000 for beta01.cloud.kavia.ai
            pattern = r"^https://vscode-internal-\d+-beta\.beta01\.cloud\.kavia\.ai:(3000|4000)$"
            if re.match(pattern, origin):
                allowed = True
                logger.debug(f"Origin allowed by dev pattern: {origin}")
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers if allowed
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response

# Standard CORS middleware with explicit allowlist
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (took {process_time:.3f}s)")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    
    return response


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.
    
    Attributes:
        message: User's message to send to the AI (required, non-empty)
    """
    message: str = Field(
        ...,
        description="User's message to send to the AI assistant",
        min_length=1,
        max_length=10000
    )
    
    @validator('message')
    def message_not_empty(cls, v):
        """Validate that message is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    
    Attributes:
        reply: AI-generated response
        model: Model used to generate the response
        latency_ms: Time taken to generate response in milliseconds
    """
    reply: str = Field(
        ...,
        description="AI-generated response"
    )
    model: str = Field(
        default="none",
        description="Gemini model used for generation"
    )
    latency_ms: int = Field(
        default=0,
        description="Response generation time in milliseconds"
    )


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Attributes:
        status: Service health status
        gemini_configured: Whether Gemini API is configured
        model: Active Gemini model (if configured)
    """
    status: str = Field(
        default="ok",
        description="Service health status"
    )
    gemini_configured: bool = Field(
        default=False,
        description="Whether Gemini API key is configured"
    )
    model: str = Field(
        default="none",
        description="Active Gemini model name"
    )


# ==================== API Endpoints ====================

# PUBLIC_INTERFACE
@app.get("/", response_model=Dict[str, str], tags=["Root"])
async def root():
    """
    Root endpoint providing basic service information.
    
    Returns:
        Simple message indicating service is running
    """
    return {
        "message": "AI Copilot Backend API",
        "version": "0.1.0",
        "status": "running"
    }


# PUBLIC_INTERFACE
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """
    Health check endpoint.
    
    Verifies that the service is running and checks Gemini API configuration status.
    Useful for load balancers, monitoring systems, and debugging.
    
    Returns:
        JSON object with service status and configuration details
    """
    client = GeminiClient()
    
    return HealthResponse(
        status="ok",
        gemini_configured=client.usable,
        model=client.actual_model
    )


# PUBLIC_INTERFACE
@app.options("/api/health", tags=["Health"])
async def health_options():
    """
    OPTIONS preflight handler for /api/health to support CORS diagnostics.
    """
    return JSONResponse(status_code=200, content={"status": "ok"})

# PUBLIC_INTERFACE
@app.options("/api/chat", tags=["Chat"])
async def chat_options():
    """
    OPTIONS preflight handler for /api/chat to support CORS diagnostics.
    """
    return JSONResponse(status_code=200, content={"ok": True})

# PUBLIC_INTERFACE
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Chat endpoint for sending messages to AI assistant.
    
    Accepts user messages and returns AI-generated responses using Google Gemini.
    Includes automatic model fallback and comprehensive error handling.
    
    Args:
        req: ChatRequest containing the user's message
        
    Returns:
        ChatResponse with AI-generated reply, model info, and latency
        
    Raises:
        HTTPException 400: If message is empty or invalid
        HTTPException 500: If an unexpected error occurs
    """
    # Validate message
    if not req.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    logger.info(f"Chat request received: {req.message[:50]}...")
    
    try:
        # Initialize Gemini client
        client = GeminiClient()
        
        # Measure response time
        start_time = time.time()
        
        # Generate reply
        reply = await client.generate_reply(req.message)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Response generated in {latency_ms}ms using model: {client.actual_model}")
        
        return ChatResponse(
            reply=reply,
            model=client.actual_model,
            latency_ms=latency_ms
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

# PUBLIC_INTERFACE
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_alias(req: ChatRequest):
    """
    Alias endpoint for clients using /chat instead of /api/chat.

    Forwards the request to the primary /api/chat handler to maintain compatibility
    with examples or local code that expect /chat.

    Args:
        req: ChatRequest containing the user's message

    Returns:
        ChatResponse as produced by the main /api/chat endpoint
    """
    return await chat(req)


# ==================== Error Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    
    Logs configuration and performs initial health checks.
    """
    logger.info("=" * 50)
    logger.info("AI Copilot Backend Starting Up")
    logger.info("=" * 50)
    logger.info(f"Environment: {ENV_MODE}")
    logger.info(f"CORS Origins: {ALLOWED_ORIGINS}")
    logger.info(f"Dev Mode: {DEV_MODE}")
    
    # Check Gemini configuration
    client = GeminiClient()
    if client.usable:
        logger.info(f"✓ Gemini API configured with model: {client.actual_model}")
    else:
        logger.warning("⚠ Gemini API not configured - will return stub responses")
        logger.warning("  Set GOOGLE_GEMINI_API_KEY in .env to enable AI features")
    
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("AI Copilot Backend Shutting Down")
