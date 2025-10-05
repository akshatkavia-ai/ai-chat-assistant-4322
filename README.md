# AI Copilot - Full-Stack Chat Application

A modern full-stack AI Copilot web application that enables real-time chat with an AI assistant powered by Google Gemini API. Built with React and FastAPI with Ocean Professional theme styling.

## Architecture

- **Frontend**: React (JavaScript) with Axios for API communication
- **Backend**: FastAPI with Google Gemini API integration
- **Theme**: Ocean Professional with modern blue and amber accents
- **Ports**: Backend runs on port 3001, Frontend on port 3000

## Features

### Backend (FastAPI)
- RESTful API endpoints for chat functionality
- Google Gemini API integration for AI responses
- CORS configuration for frontend communication
- Environment-based configuration with .env support
- Graceful degradation when API key is not configured
- Comprehensive API documentation (Swagger/OpenAPI)

### Frontend (React)
- Modern, responsive chat interface
- Real-time message updates with auto-scroll
- Ocean Professional theme with smooth animations
- Error handling and loading states
- Environment variable configuration for API endpoint

## ⚠️ Important: Preview Environment URLs

**Note**: The preview environment URLs can change between sessions. The current running services are at:
- **Backend**: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001
- **Frontend**: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000

If you encounter connectivity issues, verify your actual preview URLs and update the `.env` files accordingly. See [CONNECTIVITY_FIX.md](CONNECTIVITY_FIX.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key (optional for testing, required for real AI responses)

### ✅ Connectivity Status
The frontend-backend connectivity has been verified and is working correctly. See [CONNECTIVITY_FIX.md](CONNECTIVITY_FIX.md) for details of recent fixes.

### Backend Setup

1. Navigate to the backend directory:
```bash
cd ai_copilot_backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Google Gemini API key:
```
GOOGLE_GEMINI_API_KEY=your_api_key_here
```
Get your API key from: https://makersuite.google.com/app/apikey

5. The backend is auto-started on port 3001 by the preview environment.

To run manually:
```bash
cd src/api
uvicorn main:app --host 0.0.0.0 --port 3001 --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ai-chat-assistant-4344/ai_copilot_frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. The frontend is auto-started on port 3000 by the preview environment.

To run manually:
```bash
npm start
```

## API Endpoints

### Backend API

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - Send message to AI assistant
  ```json
  Request: { "message": "Your question" }
  Response: { "reply": "AI response" }
  ```

### API Documentation

Once the backend is running, access:
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc
- OpenAPI JSON: http://localhost:3001/openapi.json

## Environment Variables

### Backend (.env)
```env
GOOGLE_GEMINI_API_KEY=     # Your Google Gemini API key
ALLOWED_ORIGINS=           # Comma-separated CORS origins
```

### Frontend (.env)
```env
REACT_APP_API_BASE_URL=    # Backend API URL (default: http://localhost:3001)
```

## Theme Customization

The application uses the **Ocean Professional** theme defined in `src/theme.js`:

```javascript
{
  colors: {
    primary: '#2563EB',      // Blue
    secondary: '#F59E0B',    // Amber
    background: '#f9fafb',   // Light gray
    surface: '#ffffff',      // White
    text: '#111827'          // Dark gray
  }
}
```

To customize, edit `ai_copilot_frontend/src/theme.js`.

## Project Structure

```
ai-chat-assistant-4322/
├── README.md
└── ai_copilot_backend/
    ├── requirements.txt
    ├── .env.example
    ├── .env
    ├── README.md
    └── src/
        └── api/
            ├── main.py              # FastAPI app with endpoints
            ├── gemini_service.py    # Gemini API integration
            └── generate_openapi.py  # OpenAPI schema generator

ai-chat-assistant-4344/
└── ai_copilot_frontend/
    ├── package.json
    ├── .env.example
    ├── .env
    ├── README.md
    └── src/
        ├── api/
        │   └── client.js         # Axios API client
        ├── components/
        │   └── Chat.js           # Main chat component
        ├── theme.js              # Theme configuration
        ├── App.js                # Root component
        └── index.js              # Entry point
```

## Usage

1. Ensure both backend and frontend are running
2. Open the frontend at http://localhost:3000
3. Start chatting with the AI assistant
4. If you haven't configured the Gemini API key, you'll receive stub responses with instructions

## Notes

- **Without API Key**: The application will work but return stub responses indicating that the API key needs to be configured
- **CORS**: The backend is configured to accept requests from `http://localhost:3000` by default
- **Port Configuration**: Backend uses port 3001, Frontend uses port 3000
- **Auto-reload**: Both services support hot-reloading during development

## Troubleshooting

### Cannot connect to backend
**Symptoms**: Frontend shows "Cannot connect to backend" error

**Quick Fix**:
1. Verify backend is running: `curl https://<your-host>:3001/api/health`
2. Check frontend `.env` has correct backend URL
3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed steps

### CORS Errors
**Symptoms**: Browser console shows CORS policy errors

**Quick Fix**:
1. Check backend `.env` ALLOWED_ORIGINS includes your frontend URL
2. Ensure URL matches exactly (protocol, host, port)
3. Restart backend after changes

### Backend not connecting
- Verify the backend is running on port 3001
- Check the `.env` file in the backend directory
- Ensure all Python dependencies are installed

### Frontend can't reach backend
- Check `REACT_APP_API_BASE_URL` in frontend `.env`
- Verify CORS settings in backend `.env`
- Ensure backend is running and accessible

### Stub responses instead of AI
- Add your Google Gemini API key to backend `.env`
- Restart the backend service after updating the `.env` file

### Preview Domain Changes
If your preview domain changes, update both `.env` files and restart services. See [CONNECTIVITY_FIX.md](CONNECTIVITY_FIX.md) for instructions.

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Development

Both services support hot-reloading:
- **Backend**: Changes to Python files will trigger auto-reload
- **Frontend**: Changes to React components will hot-reload in the browser

## Production Build

### Frontend
```bash
cd ai_copilot_frontend
npm run build
```

This creates an optimized production build in the `build/` directory.

## License

This project is part of the Kavia AI Copilot application suite.
