# 🚀 Deployment Guide

## Zero-Dependency Deployment (No FFmpeg Required!)

This podcast generator uses **binary MP3 concatenation** instead of FFmpeg, making it perfect for cloud platforms without system dependencies.

---

## Deployment Platforms

### 1. **Railway** (Recommended)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Add to requirements.txt:
```
gunicorn==21.2.0
```

---

### 2. **Render**

1. Connect GitHub repo
2. Create Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. Add Environment Variable: `GEMINI_API_KEY`

**render.yaml:**
```yaml
services:
  - type: web
    name: podcast-generator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

### 3. **Heroku**

```bash
# Login
heroku login

# Create app
heroku create podcast-generator

# Deploy
git push heroku main
```

**Procfile:**
```
web: gunicorn app:app
```

**runtime.txt:**
```
python-3.11.6
```

---

### 4. **Google Cloud Run**

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/podcast-generator

# Deploy
gcloud run deploy podcast-generator \
  --image gcr.io/PROJECT_ID/podcast-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

---

### 5. **Fly.io**

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch
fly launch

# Deploy
fly deploy
```

**fly.toml:**
```toml
app = "podcast-generator"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

---

## Environment Variables

Set these on your platform:

```env
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=production
PORT=8080  # or platform default
```

---

## Production Optimizations

### 1. **Use Production WSGI Server**

Replace Flask dev server with Gunicorn:

```python
# Don't use app.run() in production
# Use: gunicorn app:app
```

### 2. **Set Worker Count**

```bash
# For Railway/Render (512MB RAM)
gunicorn --workers 1 --threads 4 app:app

# For larger instances (1GB+ RAM)
gunicorn --workers 2 --threads 8 app:app
```

### 3. **Configure Timeouts**

Edge TTS can be slow. Set appropriate timeouts:

```bash
gunicorn --timeout 120 --workers 1 app:app
```

### 4. **Enable Compression**

Flask-Compress for faster responses:

```python
from flask_compress import Compress
Compress(app)
```

---

## What Works Without FFmpeg

✅ **MP3 Generation** - Edge TTS creates MP3 directly  
✅ **Multi-segment Merging** - Binary concatenation  
✅ **Voice Selection** - All 250+ voices  
✅ **Language Support** - All 140+ languages  
✅ **Audio Effects** - Pedalboard (optional but works)  
✅ **Gemini AI** - Script generation  

❌ **Crossfade** - Disabled (not critical)  
❌ **Silence Pauses** - Disabled (Edge TTS has natural pauses)  
❌ **Background Music** - Disabled (optional feature)  

---

## Estimated Costs

| Platform | Free Tier | Paid (512MB) |
|----------|-----------|--------------|
| Railway | $5 credit | ~$5/month |
| Render | 750 hrs | $7/month |
| Heroku | No free tier | $7/month |
| Fly.io | 3 VMs free | $1.94/month |
| Google Cloud Run | 2M requests | Pay per use |

---

## Monitoring

### Health Check Endpoint

```bash
curl https://your-app.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Logs

```bash
# Railway
railway logs

# Render
# View in dashboard

# Heroku
heroku logs --tail

# Fly.io
fly logs
```

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Rebuild with fresh requirements.txt

### Issue: "Memory exceeded"
**Solution:** Reduce worker count or upgrade instance

### Issue: "Connection timeout"
**Solution:** Increase gunicorn timeout to 120s

### Issue: "Gemini API error"
**Solution:** Verify GEMINI_API_KEY is set correctly

---

## Performance Tips

1. **Enable Caching** - Cache voice lists
2. **Async Processing** - Use background tasks for long podcasts
3. **CDN** - Serve static files via CDN
4. **Database** - Store generated podcasts (optional)

---

## Support

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Pull Requests: Contribute improvements

Happy Deploying! 🚀
