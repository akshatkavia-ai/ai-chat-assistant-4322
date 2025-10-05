"""
Gemini AI Service Module

This module provides integration with Google's Gemini AI API.
Supports multiple models with automatic fallback mechanism.
"""
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logger.info("Google Generative AI SDK loaded successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"Google Generative AI SDK not available: {e}")

# Get API key from environment
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "").strip()


class GeminiClient:
    """
    Service for interacting with Google Gemini API.
    
    Supports automatic model fallback if primary model is unavailable.
    
    Supported models (in order of preference):
    - gemini-2.0-flash: Fast and versatile multimodal model (default)
    - gemini-2.5-flash: Mid-size multimodal model
    - gemini-2.5-pro: Advanced stable model
    
    Environment Variables:
        GOOGLE_GEMINI_API_KEY: Required API key for Gemini
        GEMINI_MODEL: Optional model name override (default: gemini-2.0-flash)
    """
    
    # Fallback model sequence if primary model fails
    FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            model_name: Optional model name to use. If None, uses GEMINI_MODEL env var
                       or defaults to gemini-2.0-flash.
        """
        # Use environment variable if set, otherwise default to gemini-2.0-flash
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
        
        self.model_name = model_name
        self._usable = GEMINI_AVAILABLE and bool(API_KEY)
        self.model = None
        self._actual_model_used = None
        
        # Log initialization status
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini SDK not available - will return stub responses")
        elif not API_KEY:
            logger.warning("GOOGLE_GEMINI_API_KEY not configured - will return stub responses")
        
        if self._usable:
            try:
                genai.configure(api_key=API_KEY)
                logger.info("Gemini API configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {e}")
                self._usable = False
                return
            
            # Try to initialize with the requested model
            if not self._initialize_model(model_name):
                # If that fails, try fallback models
                logger.warning(f"Failed to initialize model '{model_name}', trying fallbacks...")
                for fallback in self.FALLBACK_MODELS:
                    if fallback != model_name and self._initialize_model(fallback):
                        logger.info(f"Successfully initialized with fallback model: {fallback}")
                        break
                else:
                    logger.error("All model initialization attempts failed")
                    self._usable = False

    def _initialize_model(self, model_name: str) -> bool:
        """
        Try to initialize a specific model.
        
        Args:
            model_name: Name of the model to initialize
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            self.model = genai.GenerativeModel(model_name)
            self._actual_model_used = model_name
            logger.info(f"Initialized Gemini model: {model_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize model '{model_name}': {e}")
            return False

    @property
    def usable(self) -> bool:
        """
        Check if Gemini API is available and configured.
        
        Returns:
            True if API is ready to use, False otherwise
        """
        return self._usable

    @property
    def actual_model(self) -> str:
        """
        Get the actual model being used (may differ from requested due to fallback).
        
        Returns:
            Model name currently in use, or "none" if no model is available
        """
        return self._actual_model_used or "none"

    async def generate_reply(self, prompt: str) -> str:
        """
        Generate a reply from Gemini AI.
        
        This is the main public interface for generating AI responses.
        Includes automatic fallback and comprehensive error handling.
        
        Args:
            prompt: User's message/prompt
            
        Returns:
            AI-generated response or stub message if API not available
        """
        if not self._usable:
            stub_message = (
                "[Stubbed AI Response] The Gemini API is not currently configured.\n\n"
                "To get real AI responses:\n"
                "1. Get an API key from: https://makersuite.google.com/app/apikey\n"
                "2. Add it to the backend .env file: GOOGLE_GEMINI_API_KEY=your_key_here\n"
                "3. Restart the backend service\n\n"
                f"Your message was: {prompt}"
            )
            logger.info("Returning stub response - API not configured")
            return stub_message
        
        # Try to generate with current model
        try:
            response = await self._generate_async(prompt)
            logger.info(f"Successfully generated response using model: {self._actual_model_used}")
            return response
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating content with model '{self._actual_model_used}': {error_msg}")
            
            # Check if it's a 404 model not found error
            if "404" in error_msg or "not found" in error_msg.lower():
                logger.warning(f"Model '{self._actual_model_used}' not found (404), trying fallback...")
                
                # Try fallback models
                for fallback_model in self.FALLBACK_MODELS:
                    if fallback_model == self._actual_model_used:
                        continue  # Skip the model that just failed
                    
                    logger.info(f"Attempting fallback to model: {fallback_model}")
                    if self._initialize_model(fallback_model):
                        try:
                            response = await self._generate_async(prompt)
                            logger.info(f"Successfully generated response with fallback model: {fallback_model}")
                            return response
                        except Exception as fallback_error:
                            logger.warning(f"Fallback model '{fallback_model}' also failed: {fallback_error}")
                            continue
                
                # All fallbacks failed
                return (
                    f"[AI Error] Model '{self.model_name}' not found (404) and all fallback models failed. "
                    f"Please check supported models for your API version or update GEMINI_MODEL in .env"
                )
            
            # Other errors - return helpful message
            return f"[AI Error] Failed to generate response: {error_msg}"

    async def _generate_async(self, prompt: str) -> str:
        """
        Generate content asynchronously using Gemini API.
        
        The google-generativeai SDK is synchronous, so we run it in a thread
        to avoid blocking the async event loop.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        import anyio
        
        def _generate():
            result = self.model.generate_content(prompt)
            if hasattr(result, 'text'):
                return result.text
            return str(result)
        
        return await anyio.to_thread.run_sync(_generate)
