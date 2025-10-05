# AI Copilot Quick Start Guide

Get your AI Copilot chat application up and running in minutes!

## 🚀 Quick Setup

### Step 1: Get Your Google Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key for the next step

### Step 2: Configure Backend

Add your API key to the backend `.env` file:

```bash
cd ai-chat-assistant-4322/ai_copilot_backend
```

Edit the `.env` file and add your key:
```env
GOOGLE_GEMINI_API_KEY=your_actual_api_key_here
```

**Important:** Replace `your_actual_api_key_here` with your actual API key from Step 1.

### Step 3: Access Your Application

The preview environment has already started both services for you:

- **Frontend**: https://vscode-internal-23134-beta.beta01.cloud.kavia.ai:3000
- **Backend API**: https://vscode-internal-23134-beta.beta01.cloud.kavia.ai:3001/docs

### Step 4: Start Chatting!

1. Open the frontend URL in your browser
2. Type a message in the chat input
3. Click "Send" or press Enter
4. Watch the AI respond in real-time! 🎉

## 🧪 Testing Without API Key

You can test the application without configuring the Gemini API key:

1. The app will work but return stub responses
2. Each stub response will remind you to configure the API key
3. This is perfect for testing the UI and basic functionality

## 📝 What You Get

- ✅ Modern chat interface with Ocean Professional theme
- ✅ Real-time AI responses powered by Google Gemini
- ✅ Auto-scrolling chat history
- ✅ Loading states and error handling
- ✅ Responsive design that works on all devices
- ✅ Clean, modern UI with smooth animations

## 🔧 Manual Start (Optional)

If you need to manually start the services:

### Backend
```bash
cd ai-chat-assistant-4322/ai_copilot_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

### Frontend
```bash
cd ai-chat-assistant-4344/ai_copilot_frontend
npm start
```

## 💡 Tips

1. **Stub Responses**: If you see stub responses, add your API key to `.env`
2. **CORS Errors**: The backend is already configured for the preview URLs
3. **Hot Reload**: Both services auto-reload when you make code changes
4. **API Docs**: Visit `/docs` on the backend URL for interactive API documentation

## 🆘 Troubleshooting

### "Cannot connect to backend server"
- Check that the backend is running on port 3001
- Verify the `REACT_APP_API_BASE_URL` in frontend `.env`

### "Stub responses instead of AI"
- Add your Gemini API key to backend `.env`
- Restart the backend service

### Dependencies Issues
```bash
# Backend
cd ai_copilot_backend
pip install -r requirements.txt

# Frontend  
cd ai_copilot_frontend
npm install
```

## 📚 Next Steps

- Customize the theme in `src/theme.js`
- Add more features to the chat interface
- Deploy to production
- Check out the full README.md for detailed documentation

Enjoy your AI Copilot! 🤖✨
