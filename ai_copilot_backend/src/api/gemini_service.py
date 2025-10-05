import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

class GeminiClient:
    """Service for interacting with Google Gemini API.
    
    Supported models (in order of preference):
    - gemini-2.0-flash: Fast and versatile multimodal model (default)
    - gemini-2.5-flash: Mid-size multimodal model
    - gemini-2.5-pro: Advanced stable model
    
    Set GEMINI_MODEL environment variable to override default model.
    """
    
    # Fallback model sequence if primary model fails
    # Using models that are confirmed available in the current API version
    FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
    
    def __init__(self, model_name: str = None):
        # Use environment variable if set, otherwise default to gemini-2.0-flash
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        self.model_name = model_name
        self._usable = GEMINI_AVAILABLE and bool(API_KEY)
        self.model = None
        self._actual_model_used = None
        
        if self._usable:
            genai.configure(api_key=API_KEY)
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
        """Try to initialize a specific model.
        
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
        """Check if Gemini API is available and configured."""
        return self._usable

    @property
    def actual_model(self) -> str:
        """Get the actual model being used (may differ from requested due to fallback)."""
        return self._actual_model_used or "none"

    async def chat(self, prompt: str) -> str:
        """
        Send a chat message to Gemini and get a response.
        
        Args:
            prompt: User's message
            
        Returns:
            AI-generated response or stub message if API not available
        """
        if not self._usable:
            return (
                "[Stubbed AI Response] Set GOOGLE_GEMINI_API_KEY in backend .env to get real AI answers.\n"
                f"You asked: {prompt}"
            )
        
        # Try to generate with current model
        try:
            resp = await self._generate_async(prompt)
            logger.info(f"Successfully generated response using model: {self._actual_model_used}")
            return resp
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
                            resp = await self._generate_async(prompt)
                            logger.info(f"Successfully generated response with fallback model: {fallback_model}")
                            return resp
                        except Exception as fallback_error:
                            logger.warning(f"Fallback model '{fallback_model}' also failed: {fallback_error}")
                            continue
                
                # All fallbacks failed
                return f"[AI Error] Model '{self.model_name}' not found (404) and all fallback models failed. Please check supported models for your API version."
            
            # Other errors
            return f"[AI Error] {error_msg}"

    async def _generate_async(self, prompt: str) -> str:
        """Generate content asynchronously using Gemini API."""
        # google-generativeai SDK is sync; run in thread to avoid blocking
        import anyio
        def _generate():
            result = self.model.generate_content(prompt)
            return result.text if hasattr(result, "text") else str(result)
        return await anyio.to_thread.run_sync(_generate)
