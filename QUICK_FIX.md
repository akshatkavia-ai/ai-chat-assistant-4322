# Quick Connectivity Fix Reference

## 🚨 Quick Diagnostics (30 seconds)

```bash
# Is backend healthy?
curl https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/health
# Expected: {"status":"ok",...}

# Is CORS working?
curl -i -H "Origin: https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000" \
     -X OPTIONS \
     https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/api/chat | grep access-control
# Expected: access-control-allow-origin: https://...3000

# Is frontend .env correct?
cat ai-chat-assistant-4344/ai_copilot_frontend/.env
# Expected: VITE_API_BASE_URL=https://...3001
```

---

## ⚡ Common Fixes

### Fix 1: "Cannot connect to backend"

```bash
# Check and fix frontend .env
echo "VITE_API_BASE_URL=https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001" > ai-chat-assistant-4344/ai_copilot_frontend/.env

# Restart frontend
cd ai-chat-assistant-4344/ai_copilot_frontend
npm run dev
```

### Fix 2: CORS Error

```bash
# Fix backend .env
cat > ai-chat-assistant-4322/ai_copilot_backend/.env << 'EOF'
GOOGLE_GEMINI_API_KEY=AIzaSyD798R-xKZTDjgsmNjvFr-IDRxfcwS1rEk
ALLOWED_ORIGINS=http://localhost:3000,https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
GEMINI_MODEL=gemini-2.0-flash
ENV=development
EOF

# Restart backend
pkill -f "uvicorn.*ai_copilot_backend"
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload &
```

### Fix 3: Wrong Variable Name

**Problem:** Using `REACT_APP_*` instead of `VITE_*`

**This is a VITE project!** Use `VITE_` prefix:

```bash
# Wrong ❌
REACT_APP_API_BASE_URL=...

# Correct ✅
VITE_API_BASE_URL=...
```

---

## 🎯 Current URLs

- **Frontend:** https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000
- **Backend:** https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001
- **API Docs:** https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3001/docs

---

## 📋 Configuration Checklist

- [ ] Backend returns 200 on `/api/health`
- [ ] Frontend `.env` has `VITE_API_BASE_URL` (not `REACT_APP_*`)
- [ ] Backend `.env` has `ALLOWED_ORIGINS` with frontend URL
- [ ] Backend `.env` has `ENV=development`
- [ ] Services restarted after `.env` changes
- [ ] Browser console shows correct base URL

---

## 📚 Full Documentation

For detailed troubleshooting, see:
- `CONNECTIVITY_DIAGNOSTIC.md` - Complete diagnostic guide
- `CONNECTIVITY_FIX_STATUS.md` - What was fixed and why
- `README.md` - Full container documentation

---

**Quick Test:** Open https://vscode-internal-34116-beta.beta01.cloud.kavia.ai:3000 → Press F12 → Check console for correct base URL → Send test message
