# AI Copilot - Quick Reference Card

## 🔗 Essential URLs

### Current Preview Environment
- **Frontend**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
- **Backend API**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001
- **API Docs**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/docs
- **OpenAPI Spec**: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/openapi.json

### Local Development
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs

## ⚡ Quick Commands

### Health Checks
```bash
# Backend health
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health

# Test chat endpoint
curl -X POST https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### Service Status
```bash
# Check if services are running
lsof -i:3001  # Backend
lsof -i:3000  # Frontend
```

### Service Restart
```bash
# Backend
pkill -f "uvicorn.*ai_copilot_backend"
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

# Frontend
pkill -f "vite"
cd ai-chat-assistant-4344/ai_copilot_frontend
npm run dev
```

### CORS Verification
```bash
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat | grep access-control
```

## 📁 Configuration Files

### Backend (.env)
```
Location: ai-chat-assistant-4322/ai_copilot_backend/.env
```
**Key Variables**:
- `GOOGLE_GEMINI_API_KEY` - Your API key
- `ALLOWED_ORIGINS` - Must include frontend URL
- `GEMINI_MODEL` - AI model to use
- `ENV` - development or production

### Frontend (.env)
```
Location: ai-chat-assistant-4344/ai_copilot_frontend/.env
```
**Key Variables**:
- `VITE_API_BASE_URL` - Backend URL

## 🔧 Common Fixes

### "Cannot connect to backend"
```bash
# 1. Check backend is running
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health

# 2. Verify frontend .env
cat ai-chat-assistant-4344/ai_copilot_frontend/.env

# 3. Restart frontend if needed
pkill -f "vite" && cd ai-chat-assistant-4344/ai_copilot_frontend && npm run dev
```

### CORS Errors
```bash
# 1. Check backend CORS config
grep ALLOWED_ORIGINS ai-chat-assistant-4322/ai_copilot_backend/.env

# 2. Must include: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000

# 3. Restart backend after update
```

### Stub Responses Instead of AI
```bash
# 1. Add API key to backend .env
echo "GOOGLE_GEMINI_API_KEY=your_key_here" >> ai-chat-assistant-4322/ai_copilot_backend/.env

# 2. Restart backend
pkill -f "uvicorn.*ai_copilot_backend"
```

### Preview Domain Changed
```bash
# 1. Update backend ALLOWED_ORIGINS in .env
# 2. Update frontend VITE_API_BASE_URL in .env
# 3. Restart both services
```

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check |
| POST | `/api/chat` | Send message to AI |
| GET | `/docs` | API documentation |
| GET | `/openapi.json` | OpenAPI spec |

## 🔍 Browser DevTools Check

1. Open: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
2. Press **F12** (DevTools)
3. Check **Console** for: `[API] Base URL: ...`
4. Send message
5. Check **Network** tab for `/api/chat` request

## 📚 Documentation

- **Backend Container**: `ai-chat-assistant-4322/README.md`
- **Frontend Container**: `ai-chat-assistant-4344/README.md`
- **Integration Status**: `ai-chat-assistant-4322/INTEGRATION_COMPLETE.md`
- **Troubleshooting**: `ai-chat-assistant-4322/TROUBLESHOOTING.md`
- **Deployment**: `ai-chat-assistant-4322/DEPLOYMENT.md`

## 🎯 Environment Variables Cheatsheet

### Backend Required
- ✅ `GOOGLE_GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- ✅ `ALLOWED_ORIGINS` - Frontend URL with exact protocol/host/port

### Backend Optional
- `GEMINI_MODEL` (default: gemini-2.0-flash)
- `ENV` (default: development)

### Frontend Optional
- `VITE_API_BASE_URL` (auto-detected if not set)

## ⚠️ Remember

- **Restart required**: After .env changes
- **CORS must match**: Exact frontend URL in backend ALLOWED_ORIGINS
- **Protocol matters**: http vs https must match
- **Port matters**: Include :3000 and :3001 in URLs

## 🆘 Quick Help

**Issue**: Connection error  
**Fix**: Check backend running + verify URLs match

**Issue**: CORS error  
**Fix**: Update backend ALLOWED_ORIGINS + restart

**Issue**: Stub response  
**Fix**: Add API key to backend .env + restart

**Issue**: Port in use  
**Fix**: `lsof -ti:PORT | xargs kill -9`

---

**Keep this card handy for quick troubleshooting!**
