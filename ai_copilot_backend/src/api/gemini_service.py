import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in backend root directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

class GeminiClient:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.model_name = model_name
        self._usable = GEMINI_AVAILABLE and bool(API_KEY)
        if self._usable:
            genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    @property
    def usable(self) -> bool:
        """Check if Gemini API is available and configured."""
        return self._usable

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
        # Simple non-streaming call
        try:
            resp = await self._generate_async(prompt)
            return resp
        except Exception as e:
            return f"[AI Error] {e}"

    async def _generate_async(self, prompt: str) -> str:
        """Generate content asynchronously using Gemini API."""
        # google-generativeai SDK is sync; run in thread to avoid blocking
        import anyio
        def _generate():
            result = self.model.generate_content(prompt)
            return result.text if hasattr(result, "text") else str(result)
        return await anyio.to_thread.run_sync(_generate)
