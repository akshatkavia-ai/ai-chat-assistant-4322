# Backend Connectivity Diagnostic Guide

## Quick Diagnostic Steps

Run these commands in order to diagnose connectivity issues:

### 1. Verify Backend is Running and Healthy

```bash
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health
```

**Expected Output:**
```json
{"status":"ok","gemini_configured":true,"model":"gemini-2.0-flash"}
```

**If this fails:**
- Backend is not running on port 3001
- Check if backend service is started
- Verify port 3001 is not blocked by firewall

### 2. Test CORS Configuration

```bash
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat | grep access-control
```

**Expected Output:**
```
access-control-allow-origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
access-control-allow-credentials: true
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

**If CORS headers are missing:**
- Check `ALLOWED_ORIGINS` in backend `.env` file
- Ensure frontend URL is exactly listed (protocol, host, port)
- Verify `ENV=development` is set for auto-pattern matching
- Restart backend after changing `.env`

### 3. Test Chat Endpoint

```bash
curl -X POST https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat \
     -H "Content-Type: application/json" \
     -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -d '{"message":"test"}'
```

**Expected Output:**
```json
{"reply":"<AI response>","model":"gemini-2.0-flash","latency_ms":500}
```

**If this fails:**
- Check if request is being rejected (4xx status)
- Verify API key is configured
- Check backend logs for errors

### 4. Verify Frontend Configuration

```bash
cat ai-chat-assistant-4344/ai_copilot_frontend/.env
```

**Expected Content:**
```
VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001
```

**Common Issues:**
- ❌ Using `REACT_APP_API_BASE_URL` (wrong - this is Vite, not Create React App)
- ❌ Wrong port number
- ❌ Wrong protocol (http vs https)
- ❌ Wrong hostname

### 5. Browser Console Check

1. Open frontend: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
2. Press **F12** to open DevTools
3. Look in Console tab

**Expected Output:**
```
[API] Base URL: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001
```

**If base URL is wrong:**
- Frontend `.env` is not using `VITE_API_BASE_URL`
- Restart frontend dev server after changing `.env`
- Clear browser cache

## Common Problems and Solutions

### Problem: "Cannot connect to backend"

**Symptoms:** Frontend shows connection error message

**Root Causes:**
1. Backend not running
2. Wrong backend URL in frontend `.env`
3. Network/firewall blocking connection

**Solution:**
```bash
# 1. Check backend is running
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health

# 2. Verify frontend .env has correct URL
cat ai-chat-assistant-4344/ai_copilot_frontend/.env
# Should show: VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001

# 3. If URL is wrong, fix it:
echo "VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001" > ai-chat-assistant-4344/ai_copilot_frontend/.env

# 4. Restart frontend (if running as dev server)
```

### Problem: CORS Policy Error

**Symptoms:** Browser console shows CORS error like:
```
Access to XMLHttpRequest at 'https://...3001/api/chat' from origin 'https://...3000' 
has been blocked by CORS policy
```

**Root Causes:**
1. Frontend origin not in backend `ALLOWED_ORIGINS`
2. Origin doesn't exactly match (protocol/port different)
3. Backend not configured for development mode

**Solution:**
```bash
# 1. Check backend CORS config
cat ai-chat-assistant-4322/ai_copilot_backend/.env | grep ALLOWED_ORIGINS

# 2. Should include: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000

# 3. If missing, update backend .env:
cat > ai-chat-assistant-4322/ai_copilot_backend/.env << 'EOF'
GOOGLE_GEMINI_API_KEY=<your_key>
ALLOWED_ORIGINS=http://localhost:3000,https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
GEMINI_MODEL=gemini-2.0-flash
ENV=development
EOF

# 4. Restart backend
pkill -f "uvicorn.*ai_copilot_backend"
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload &
```

### Problem: Wrong Environment Variable Name

**Symptoms:** Frontend not picking up backend URL from `.env`

**Root Cause:** Using `REACT_APP_*` prefix instead of `VITE_*`

**Solution:**
This is a **Vite** project, not Create React App. Environment variables must use `VITE_` prefix.

```bash
# Wrong (for Create React App):
REACT_APP_API_BASE_URL=...

# Correct (for Vite):
VITE_API_BASE_URL=...
```

Update frontend `.env`:
```bash
echo "VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001" > ai-chat-assistant-4344/ai_copilot_frontend/.env
```

Then restart frontend dev server.

### Problem: Preview Domain Changed

**Symptoms:** Everything was working, but now connection fails

**Root Cause:** Preview environment generated new domain/port

**Solution:**
When preview domain changes, you must update **both** .env files:

```bash
# 1. Update backend ALLOWED_ORIGINS
# Edit: ai-chat-assistant-4322/ai_copilot_backend/.env
# Change ALLOWED_ORIGINS to include new frontend URL

# 2. Update frontend API base URL
# Edit: ai-chat-assistant-4344/ai_copilot_frontend/.env
# Change VITE_API_BASE_URL to new backend URL

# 3. Restart both services
```

**Note:** In `ENV=development` mode, the backend auto-allows preview domain patterns, but it's still best practice to explicitly configure the exact origins.

## Configuration Checklist

Use this checklist to ensure correct configuration:

- [ ] Backend is responding: `curl <backend-url>/api/health` returns 200
- [ ] Backend `.env` has `GOOGLE_GEMINI_API_KEY` set
- [ ] Backend `.env` has `ALLOWED_ORIGINS` including frontend URL
- [ ] Backend `.env` has `ENV=development` for preview environments
- [ ] Frontend `.env` exists and has `VITE_API_BASE_URL` (not REACT_APP_*)
- [ ] Frontend `VITE_API_BASE_URL` points to correct backend (protocol, host, port)
- [ ] Both services restarted after `.env` changes
- [ ] CORS preflight returns correct `access-control-allow-origin` header
- [ ] Browser console shows correct base URL on page load

## Testing Connectivity End-to-End

Complete test sequence:

```bash
# Step 1: Backend health
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health
# Expected: {"status":"ok",...}

# Step 2: CORS preflight
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat | grep access-control-allow-origin
# Expected: access-control-allow-origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000

# Step 3: Chat endpoint
curl -X POST https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat \
     -H "Content-Type: application/json" \
     -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -d '{"message":"hello"}'
# Expected: {"reply":"<AI response>",...}

# Step 4: Frontend .env
cat ai-chat-assistant-4344/ai_copilot_frontend/.env
# Expected: VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001

# Step 5: Open browser
# Visit: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
# Check console for: [API] Base URL: https://...
# Send test message and verify AI response
```

If all steps pass, connectivity is fully functional.

## Quick Fix Script

Save this as `fix_connectivity.sh` and run when connectivity breaks:

```bash
#!/bin/bash

BACKEND_URL="https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001"
FRONTEND_URL="https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000"

echo "Testing backend health..."
curl -s "$BACKEND_URL/api/health"

echo -e "\n\nChecking backend .env..."
grep ALLOWED_ORIGINS ai-chat-assistant-4322/ai_copilot_backend/.env

echo -e "\n\nChecking frontend .env..."
cat ai-chat-assistant-4344/ai_copilot_frontend/.env

echo -e "\n\nTesting CORS..."
curl -i -H "Origin: $FRONTEND_URL" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     "$BACKEND_URL/api/chat" 2>/dev/null | grep access-control-allow-origin

echo -e "\n\nDone! Check output above for issues."
```

---

**Document Version:** 1.0  
**Last Updated:** Current Session  
**Preview Domain:** vscode-internal-34116-beta.beta01.cloud.kavia.ai
