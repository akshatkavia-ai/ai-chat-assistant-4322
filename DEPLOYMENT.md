# AI Copilot Deployment Guide

This guide covers deploying your AI Copilot application to production.

## 🌍 Production Deployment Overview

The application consists of two services that need to be deployed:
1. **Backend (FastAPI)** - Python API service
2. **Frontend (React)** - Static web application

## Backend Deployment

### Option 1: Docker Deployment

Create a `Dockerfile` in `ai_copilot_backend/`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "3001"]
```

Build and run:
```bash
docker build -t ai-copilot-backend .
docker run -p 3001:3001 --env-file .env ai-copilot-backend
```

### Option 2: Platform as a Service (PaaS)

#### Deploy to Railway/Render/Fly.io

1. Connect your Git repository
2. Set environment variables:
   - `GOOGLE_GEMINI_API_KEY`
   - `ALLOWED_ORIGINS` (your frontend URL)
3. Set start command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

#### Deploy to AWS EC2/DigitalOcean/Linode

```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn for production
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
```

Set up as a systemd service:

```ini
[Unit]
Description=AI Copilot Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ai_copilot_backend
EnvironmentFile=/path/to/ai_copilot_backend/.env
ExecStart=/usr/local/bin/gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
Restart=always

[Install]
WantedBy=multi-user.target
```

## Frontend Deployment

### Build the Frontend

```bash
cd ai-chat-assistant-4344/ai_copilot_frontend
npm run build
```

This creates a `build/` directory with optimized static files.

### Option 1: Static Hosting

#### Vercel
```bash
npm install -g vercel
vercel --prod
```

Set environment variable:
- `REACT_APP_API_BASE_URL`: Your backend URL

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=build
```

Environment variables in Netlify dashboard:
- `REACT_APP_API_BASE_URL`: Your backend URL

#### AWS S3 + CloudFront
```bash
# Upload build folder to S3
aws s3 sync build/ s3://your-bucket-name --delete

# Configure CloudFront distribution to serve from S3
```

#### GitHub Pages
Add to `package.json`:
```json
{
  "homepage": "https://yourusername.github.io/ai-copilot"
}
```

Deploy:
```bash
npm install --save-dev gh-pages
npm run build
npx gh-pages -d build
```

### Option 2: Docker Deployment

Create `Dockerfile` in `ai_copilot_frontend/`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t ai-copilot-frontend .
docker run -p 80:80 ai-copilot-frontend
```

## Environment Configuration

### Backend Production Environment Variables

```env
GOOGLE_GEMINI_API_KEY=your_production_api_key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend Production Environment Variables

```env
REACT_APP_API_BASE_URL=https://api.yourdomain.com
```

## Security Considerations

### Backend Security

1. **API Key Protection**: Never commit `.env` files to Git
2. **CORS Configuration**: Set specific allowed origins, not `*`
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **HTTPS**: Always use HTTPS in production
5. **API Key Rotation**: Regularly rotate your Gemini API key

Example rate limiting with `slowapi`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest):
    # ... existing code
```

### Frontend Security

1. **Environment Variables**: Use build-time env vars, not runtime secrets
2. **Content Security Policy**: Configure CSP headers
3. **HTTPS Only**: Serve only over HTTPS
4. **API URL Validation**: Validate API base URL format

## Monitoring and Logging

### Backend Monitoring

Add logging middleware:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Health Checks

The `/api/health` endpoint is ready for load balancer health checks.

## Performance Optimization

### Backend
- Use connection pooling for databases
- Implement caching for frequent requests
- Use CDN for static assets
- Enable gzip compression

### Frontend
- Already optimized with production build
- Consider code splitting for larger apps
- Enable CDN caching
- Compress images and assets

## Scaling Considerations

### Horizontal Scaling
- Backend: Run multiple instances behind a load balancer
- Frontend: Use CDN for global distribution

### Database
- If you add a database later, use connection pooling
- Consider Redis for caching AI responses

## Cost Optimization

### Gemini API Costs
- Monitor API usage in Google Cloud Console
- Implement request caching to reduce API calls
- Set usage quotas and alerts

## Rollback Strategy

1. Keep previous deployments available
2. Use blue-green deployment for zero downtime
3. Maintain deployment logs and version tags

## Production Checklist

- [ ] Environment variables configured
- [ ] CORS properly restricted
- [ ] HTTPS enabled on both services
- [ ] Rate limiting implemented
- [ ] Monitoring and logging set up
- [ ] Error tracking (e.g., Sentry) configured
- [ ] Backup strategy in place
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated

## Support and Maintenance

- Regularly update dependencies
- Monitor API quotas and costs
- Review error logs weekly
- Keep Gemini API key secure
- Update CORS origins as needed

For questions or issues, refer to the main README.md or deployment platform documentation.
