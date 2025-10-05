import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

try:
    import google.generativeai as genai
    
    API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not API_KEY:
        print("No API key found. Set GOOGLE_GEMINI_API_KEY in .env file.")
    else:
        genai.configure(api_key=API_KEY)
        
        print("Available models:")
        print("-" * 50)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"Name: {model.name}")
                print(f"  Display name: {model.display_name}")
                print(f"  Description: {model.description}")
                print(f"  Supported methods: {model.supported_generation_methods}")
                print()
        
except Exception as e:
    print(f"Error: {e}")
