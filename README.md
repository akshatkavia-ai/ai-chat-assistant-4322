# AI Copilot Backend Container

## Project Overview

This is the backend container for the AI Copilot application - a FastAPI-based REST API service that handles chat requests and integrates with Google's Gemini AI to provide intelligent responses. The backend manages API authentication, CORS configuration, and provides comprehensive error handling.

## Architecture

- **Framework**: FastAPI (Python 3.11+)
- **AI Integration**: Google Gemini API
- **Server**: Uvicorn (ASGI)
- **API Documentation**: OpenAPI/Swagger
- **Port**: 3001

## Prerequisites

Before running this container, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Access to the preview environment or local development setup

## Quick Start

### 1. Install Dependencies

```bash
cd ai-chat-assistant-4322/ai_copilot_backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file should already exist. Verify it contains the required variables:

```bash
cat .env
```

If not present, create it with:

```bash
cp .env.example .env
```

### 3. Set Your API Key

Edit the `.env` file and add your Google Gemini API key:

```env
GOOGLE_GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run Preview

The backend service is automatically started in the preview environment. Access it at:

- **API Documentation**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/docs
- **Health Check**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health

### 5. Manual Start (If Needed)

```bash
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_GEMINI_API_KEY` | Yes* | (placeholder) | Your Google Gemini API key. Required for real AI responses. |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model to use. Options: `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-pro` |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins. Must match frontend URL exactly (protocol, host, port). |
| `ENV` | No | `development` | Environment mode. Use `development` for auto CORS pattern matching, `production` for strict enforcement. |

\* *Without API key, the service returns stub responses with configuration instructions.*

### Example .env File

```env
GOOGLE_GEMINI_API_KEY=AIzaSyABC123...xyz789
GEMINI_MODEL=gemini-2.0-flash
ALLOWED_ORIGINS=http://localhost:3000,https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
ENV=development
```

## API Endpoints

### GET / 
**Root endpoint** - Basic service information

**Response:**
```json
{
  "message": "AI Copilot Backend API",
  "version": "0.1.0",
  "status": "running"
}
```

### GET /api/health
**Health check endpoint** - Verify service status and configuration

**Response:**
```json
{
  "status": "ok",
  "gemini_configured": true,
  "model": "gemini-2.0-flash"
}
```

### POST /api/chat
**Chat endpoint** - Send messages to AI assistant

**Request Body:**
```json
{
  "message": "What is FastAPI?"
}
```

**Response:**
```json
{
  "reply": "FastAPI is a modern, fast web framework for building APIs with Python...",
  "model": "gemini-2.0-flash",
  "latency_ms": 1250
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or empty message
- `500 Internal Server Error` - AI generation failed

## Base URL Rules

The backend API base URL follows this pattern:

- **Local Development**: `http://localhost:3001`
- **Preview Environment**: `https://vscode-internal-{port}-beta.beta01.cloud.kavia.ai:3001`

When the preview domain changes, you must update:
1. Backend `.env` → `ALLOWED_ORIGINS` (include new frontend URL)
2. Frontend `.env` → `VITE_API_BASE_URL` (point to new backend URL)

## Interactive API Documentation

Once the service is running, visit these URLs for interactive API documentation:

- **Swagger UI**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/docs
- **ReDoc**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/redoc
- **OpenAPI JSON**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/openapi.json

## Troubleshooting

### Issue: Service won't start

**Symptoms**: Port 3001 already in use

**Solution**:
```bash
# Kill existing process
lsof -ti:3001 | xargs kill -9

# Restart service
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

### Issue: CORS errors from frontend

**Symptoms**: Browser console shows CORS policy errors

**Causes**:
- Frontend origin not in `ALLOWED_ORIGINS`
- Protocol/port mismatch
- Preview domain changed

**Solution**:
```bash
# Check current CORS configuration
grep ALLOWED_ORIGINS ai-chat-assistant-4322/ai_copilot_backend/.env

# Should include exact frontend URL, e.g.:
# ALLOWED_ORIGINS=http://localhost:3000,https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000

# Update if needed, then restart backend
```

**Verify CORS** with curl:
```bash
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat
```

Expected headers:
```
access-control-allow-origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
access-control-allow-credentials: true
```

### Issue: Stub responses instead of AI

**Symptoms**: API returns "[Stubbed AI Response]" messages

**Causes**:
- `GOOGLE_GEMINI_API_KEY` not set or invalid
- API key doesn't have proper permissions

**Solution**:
```bash
# 1. Get API key from https://makersuite.google.com/app/apikey
# 2. Add to .env file
echo "GOOGLE_GEMINI_API_KEY=your_key_here" >> ai-chat-assistant-4322/ai_copilot_backend/.env

# 3. Restart backend
pkill -f "uvicorn.*ai_copilot_backend"
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

### Issue: Model not found (404)

**Symptoms**: Error message about model not being available

**Cause**: Specified model not supported by your API version

**Solution**:
```bash
# Update GEMINI_MODEL in .env to a supported model
# Supported models: gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro

# The service includes automatic fallback logic
# Check logs to see which model is actually being used
```

### Issue: Network/Connection errors

**Symptoms**: "Cannot connect to backend" or timeout errors

**Checks**:
```bash
# 1. Verify backend is running
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health

# 2. Check if process is running
lsof -i:3001

# 3. Check logs for errors
# (If running in preview, check container logs)

# 4. Verify firewall/network settings
```

### Issue: 4xx/5xx Errors

**400 Bad Request**:
- Check message is not empty
- Ensure JSON format is correct
- Verify Content-Type header is `application/json`

**500 Internal Server Error**:
- Check backend logs for stack trace
- Verify API key is valid
- Check Gemini API status
- Ensure all dependencies are installed

## Health Check Steps

### Quick Health Check
```bash
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health
```

Expected: `{"status":"ok","gemini_configured":true,"model":"gemini-2.0-flash"}`

### Comprehensive Health Check

1. **Service Status**:
```bash
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health
```

2. **CORS Configuration**:
```bash
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat | grep access-control
```

3. **Chat Endpoint**:
```bash
curl -X POST https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat \
     -H "Content-Type: application/json" \
     -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -d '{"message":"test"}'
```

4. **API Documentation**:
Visit https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/docs in browser

## Important Notes

- **Service Restart Required**: After changing `.env` variables, you must restart the backend service for changes to take effect.
- **CORS Exact Match**: Frontend origin must exactly match an entry in `ALLOWED_ORIGINS` (including protocol, host, and port).
- **Development Mode**: When `ENV=development`, the service automatically allows preview domain patterns for easier development.
- **API Key Security**: Never commit `.env` files with real API keys to version control.

## Project Structure

```
ai-chat-assistant-4322/ai_copilot_backend/
├── .env                          # Environment configuration (git-ignored)
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── interfaces/
│   └── openapi.json             # OpenAPI specification
└── src/
    └── api/
        ├── __init__.py          # Package marker
        ├── main.py              # FastAPI application & routes
        ├── gemini_service.py    # Gemini AI integration
        └── generate_openapi.py  # OpenAPI generator script
```

## Development

### Enable Debug Logging
```python
# In main.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

### Hot Reload
The `--reload` flag enables automatic restart on code changes:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

### Run Tests
```bash
# Install test dependencies (if available)
pip install pytest httpx

# Run tests
pytest
```

## Production Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) in the project root.

Key considerations:
- Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
- Set `ENV=production` for strict CORS
- Configure specific `ALLOWED_ORIGINS` (no wildcards)
- Enable HTTPS
- Implement rate limiting
- Set up monitoring and logging

## Support

For additional help, refer to:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [CONNECTIVITY_FIX.md](CONNECTIVITY_FIX.md) - CORS and connectivity fixes
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Google Gemini API Docs: https://ai.google.dev/docs

## License

Part of the Kavia AI Copilot application suite.
