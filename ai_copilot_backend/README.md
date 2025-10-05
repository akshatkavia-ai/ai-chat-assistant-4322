# AI Copilot Backend (FastAPI)

FastAPI backend service for the AI Copilot chat application with Google Gemini API integration.

## Features

- REST API endpoints for chat functionality
- Google Gemini API integration for AI responses
- CORS configuration for frontend communication
- Environment-based configuration
- Graceful degradation when API key is not configured

## Endpoints

### GET /api/health
Health check endpoint to verify service status.

**Response:**
```json
{
  "status": "ok"
}
```

### POST /api/chat
Send a message to the AI assistant and receive a response.

**Request Body:**
```json
{
  "message": "Your question here"
}
```

**Response:**
```json
{
  "reply": "AI-generated response"
}
```

## Environment Variables

Create a `.env` file in the backend root directory with the following variables:

- `GOOGLE_GEMINI_API_KEY` - (Required for real AI responses) Your Google Gemini API key
  - Get your key from: https://makersuite.google.com/app/apikey
- `GEMINI_MODEL` - (Optional) Specific Gemini model to use
  - Default: `gemini-pro`
  - Supported models: `gemini-pro`, `gemini-1.5-flash`, `gemini-1.5-pro`
  - If the specified model is not found (404), the service will automatically fall back to `gemini-pro` or `gemini-1.5-flash`
- `ALLOWED_ORIGINS` - (Optional) Comma-separated list of allowed CORS origins
  - Default includes: `http://localhost:3000`, `http://127.0.0.1:3000`, and common preview domains.
  - For your environment, set this explicitly to your frontend URL(s), e.g.:
    `ALLOWED_ORIGINS=https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000`

### Supported Models

The service supports the following Gemini models (compatible with google-generativeai SDK 0.7.2):

1. **gemini-2.0-flash** (default) - Fast and versatile multimodal model, stable release
2. **gemini-2.5-flash** - Mid-size multimodal model with up to 1 million tokens
3. **gemini-2.5-pro** - Advanced stable model with enhanced capabilities

The service includes automatic fallback logic: if the configured model returns a 404 error, it will automatically try fallback models in sequence until one succeeds.

**Note**: Older model names like `gemini-pro` and `gemini-1.5-pro` are not supported in the current API version. Use `gemini-2.0-flash` or newer models instead.
=======

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Add your Google Gemini API key to the `.env` file

## Running the Application

The application is auto-started by the preview environment on port 3001.

To run manually:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc
- OpenAPI JSON: http://localhost:3001/openapi.json

## Note

If `GOOGLE_GEMINI_API_KEY` is not set, the service will return stub responses with a message indicating that the API key needs to be configured.
