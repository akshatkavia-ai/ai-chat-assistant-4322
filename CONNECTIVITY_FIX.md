# Frontend-Backend Connectivity Fix

## Issue Summary
The frontend was unable to connect to the backend due to mismatched preview domain URLs. The environment configuration files were pointing to an old preview host (`vscode-internal-23134`) while the actual running services were on a different host (`vscode-internal-20620`).

## Root Cause
1. **Frontend .env**: Configured with old backend URL `https://vscode-internal-23134-beta.beta01.cloud.kavia.ai:3001`
2. **Backend CORS**: Allowed origins included old frontend URL `https://vscode-internal-23134-beta.beta01.cloud.kavia.ai:3000`
3. **Actual running services**: Both services were running on `https://vscode-internal-20620-beta.beta01.cloud.kavia.ai`

## Changes Made

### 1. Backend Configuration (`ai_copilot_backend/.env`)
**Updated ALLOWED_ORIGINS to include the correct preview domain:**
```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000
```

### 2. Frontend Configuration (`ai_copilot_frontend/.env`)
**Updated REACT_APP_API_BASE_URL to point to correct backend:**
```env
REACT_APP_API_BASE_URL=https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001
```

### 3. Documentation Updates
Updated both `.env.example` files to include clear instructions about updating preview domain URLs.

## Verification Results

### ✅ Backend Health Check
```bash
curl https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001/api/health
# Response: {"status":"ok"}
```

### ✅ CORS Configuration
```bash
curl -i -H "Origin: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001/api/chat
     
# Response headers include:
# access-control-allow-origin: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000
# access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
# access-control-allow-credentials: true
```

### ✅ Chat Endpoint
```bash
curl -X POST https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001/api/chat \
     -H "Content-Type: application/json" \
     -H "Origin: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000" \
     -d '{"message":"test"}'
     
# Response: {"reply":"<AI response>"}
```

## Current Service Status

### Backend
- **URL**: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001
- **Status**: ✅ Running
- **CORS**: ✅ Configured for correct origin
- **API Key**: ✅ Configured (Gemini API active)

### Frontend
- **URL**: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000
- **Status**: ✅ Running
- **API Base URL**: ✅ Pointing to correct backend

## Testing the Application

1. **Open the frontend**: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000
2. **Open browser DevTools**: Press F12 or right-click → Inspect
3. **Check Console**: You should see: `[API] Base URL: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001`
4. **Send a message**: Type any message in the chat interface
5. **Verify response**: You should receive an AI-generated response from Gemini

## Browser Console Diagnostics

Expected console output when loading the frontend:
```
[API] Base URL: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001
```

Expected console output when sending a message (success):
```
(no errors)
```

## Network Tab Verification

When you send a message, check the Network tab in DevTools:
- **Request URL**: `https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3001/api/chat`
- **Status**: `200 OK`
- **Response Headers**:
  - `access-control-allow-origin: https://vscode-internal-20620-beta.beta01.cloud.kavia.ai:3000`
  - `content-type: application/json`

## Common Issues and Solutions

### Issue: "Cannot connect to backend"
**Solution**: Verify the frontend .env has the correct backend URL matching your preview domain.

### Issue: CORS errors
**Solution**: Ensure backend .env ALLOWED_ORIGINS includes the exact frontend URL (protocol, host, port).

### Issue: Different preview domain
**Solution**: If your preview domain changes:
1. Update `ai_copilot_backend/.env` → `ALLOWED_ORIGINS`
2. Update `ai_copilot_frontend/.env` → `REACT_APP_API_BASE_URL`
3. Restart both services

## Important Notes

- **Dynamic URLs**: Preview environment URLs can change. Always verify your actual running URLs from the work item or running containers info.
- **Environment Variables**: Changes to .env files require service restarts to take effect.
- **CORS**: The frontend origin must EXACTLY match an entry in the backend's ALLOWED_ORIGINS (including protocol and port).

## Summary

✅ **Fixed**: Updated both frontend and backend configurations to use the correct preview domain URLs  
✅ **Verified**: Backend health check, CORS headers, and chat endpoint all working correctly  
✅ **Tested**: Successfully sent test message and received AI response with proper CORS headers  

The connectivity issue is now resolved and the application is fully functional.
