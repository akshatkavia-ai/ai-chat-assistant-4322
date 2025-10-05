import os
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
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for AI Copilot chat application with Gemini integration",
    version="0.1.0"
)

# Configure CORS to allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
