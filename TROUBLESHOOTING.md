# AI Copilot Troubleshooting Guide

## Quick Diagnostics

### 1. Check Backend Status
```bash
curl https://<your-preview-host>:3001/api/health
```
**Expected**: `{"status":"ok"}`  
**If fails**: Backend is not running or URL is incorrect

### 2. Check Frontend Base URL
1. Open frontend in browser
2. Press F12 (DevTools)
3. Look for: `[API] Base URL: <url>`

**Expected**: URL should match your preview domain with port 3001  
**If wrong**: Update `ai_copilot_frontend/.env`

### 3. Test CORS
```bash
curl -i -H "Origin: https://<your-preview-host>:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://<your-preview-host>:3001/api/chat | grep access-control
```
**Expected**: Should show `access-control-allow-origin` header  
**If missing**: Update backend ALLOWED_ORIGINS

## Common Errors

### Error: "Cannot connect to backend"

**Symptoms**: Frontend shows connection error message

**Causes**:
1. Backend not running
2. Wrong backend URL in frontend .env
3. Network/firewall issue

**Solutions**:
```bash
# Check if backend is running
curl https://<your-preview-host>:3001/api/health

# Verify frontend .env
cat ai-chat-assistant-4344/ai_copilot_frontend/.env

# Should show: REACT_APP_API_BASE_URL=https://<your-preview-host>:3001
```

### Error: CORS Policy Error

**Symptoms**: Browser console shows CORS error

**Causes**:
1. Frontend origin not in ALLOWED_ORIGINS
2. Protocol mismatch (http vs https)
3. Port mismatch

**Solutions**:
```bash
# Check backend .env
cat ai-chat-assistant-4322/ai_copilot_backend/.env

# ALLOWED_ORIGINS must include exact frontend URL:
# https://<your-preview-host>:3000

# Update if needed and restart backend
```

### Error: "[Stubbed AI Response]"

**Symptoms**: AI returns stub message instead of real responses

**Cause**: Google Gemini API key not configured

**Solution**:
```bash
# Add API key to backend .env
echo "GOOGLE_GEMINI_API_KEY=your_key_here" >> ai-chat-assistant-4322/ai_copilot_backend/.env

# Restart backend
```

### Error: Port Already in Use

**Symptoms**: "Address already in use" when starting services

**Solutions**:
```bash
# For backend (port 3001)
lsof -ti:3001 | xargs kill -9

# For frontend (port 3000)
lsof -ti:3000 | xargs kill -9

# Then restart the service
```

## Service Restart Commands

### Restart Backend
```bash
cd ai-chat-assistant-4322/ai_copilot_backend

# Stop existing process
pkill -f "uvicorn.*ai_copilot_backend"

# Start backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

### Restart Frontend
```bash
cd ai-chat-assistant-4344/ai_copilot_frontend

# Stop existing process
pkill -f "react-scripts start"

# Start frontend
BROWSER=none PORT=3000 npm start
```

## Environment Configuration

### Backend .env Template
```env
GOOGLE_GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
ALLOWED_ORIGINS=http://localhost:3000,https://<your-preview-host>:3000
```

### Frontend .env Template
```env
REACT_APP_API_BASE_URL=https://<your-preview-host>:3001
```

## Preview Domain Changes

If your preview domain changes (e.g., port number changes):

1. **Update backend .env**:
   ```bash
   # Edit ai-chat-assistant-4322/ai_copilot_backend/.env
   # Update ALLOWED_ORIGINS with new frontend URL
   ```

2. **Update frontend .env**:
   ```bash
   # Edit ai-chat-assistant-4344/ai_copilot_frontend/.env
   # Update REACT_APP_API_BASE_URL with new backend URL
   ```

3. **Restart both services** (see commands above)

## Verification Checklist

- [ ] Backend responds to `/api/health`
- [ ] Frontend console shows correct base URL
- [ ] CORS headers present in OPTIONS response
- [ ] POST to `/api/chat` returns AI response
- [ ] No CORS errors in browser console
- [ ] Frontend can send and receive messages

## Getting Help

If issues persist:
1. Check browser console for detailed error messages
2. Check backend logs for server errors
3. Verify all environment variables are set correctly
4. Ensure no firewall/proxy is blocking requests
5. Try accessing backend URL directly in browser

## Useful Commands

```bash
# Check what's running on ports
lsof -i:3000  # Frontend
lsof -i:3001  # Backend

# View backend logs (if running as service)
tail -f /path/to/backend/logs

# Test chat endpoint directly
curl -X POST https://<host>:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'

# Check environment variables
env | grep REACT_APP
env | grep GOOGLE_GEMINI
```
