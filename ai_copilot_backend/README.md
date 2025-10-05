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
- `ALLOWED_ORIGINS` - (Optional) Comma-separated list of allowed CORS origins
  - Default: `http://localhost:3000`

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
