# Deployment Guide - Railway.app

This guide will help you deploy Querio RAG API to Railway.app with minimal cost.

## Prerequisites

- GitHub account
- Railway.app account (sign up at https://railway.app)
- Google AI API key (from https://makersuite.google.com/app/apikey)

## Cost Overview

- **Free Tier**: $5 credit per month (enough for light usage)
- **Usage-based pricing**: ~$0.000231/min for 512MB RAM
- **Estimated cost**: $0-5/month for small projects

---

## Deployment Steps

### 1. Prepare Your Repository

Push your code to GitHub:

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/querio.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway

#### Option A: Using Railway Dashboard (Recommended)

1. Go to https://railway.app and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `querio` repository
5. Railway will auto-detect the Dockerfile and start building

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link to your project
railway link

# Deploy
railway up
```

### 3. Configure Environment Variables

In Railway dashboard:

1. Go to your project
2. Click on **"Variables"** tab
3. Add the following environment variable:

```
GENAI_API_KEY=your_google_api_key_here
```

4. Click **"Add Variable"** or **"Deploy"** to restart with new config

### 4. Add Persistent Storage (Important!)

Railway provides volumes for persistent data:

1. In your service, click **"Settings"**
2. Scroll to **"Volumes"**
3. Click **"Add Volume"**
4. Create two volumes:

**Volume 1 - PDF Storage:**
- **Mount Path**: `/app/data`
- Click **"Add"**

**Volume 2 - ChromaDB:**
- **Mount Path**: `/app/chroma_db`
- Click **"Add"**

5. Redeploy your service

### 5. Get Your Public URL

1. Go to **"Settings"** in your Railway service
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Your app will be available at: `https://your-app.up.railway.app`

---

## Testing Your Deployment

### Check Health Status

```bash
curl https://your-app.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Access API Documentation

Visit in your browser:
- **Swagger UI**: `https://your-app.up.railway.app/docs`
- **ReDoc**: `https://your-app.up.railway.app/redoc`

### Upload and Test

```bash
# Upload a PDF
curl -X POST "https://your-app.up.railway.app/api/documents/upload" \
  -F "file=@your_document.pdf"

# Process documents
curl -X POST "https://your-app.up.railway.app/api/documents/process"

# Ask a question
curl -X POST "https://your-app.up.railway.app/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "k": 3}'
```

---

## Monitoring and Logs

### View Logs

**In Railway Dashboard:**
1. Click on your service
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. View real-time logs

**Using CLI:**
```bash
railway logs
```

### Monitor Usage

1. Go to your project dashboard
2. Check **"Usage"** tab to monitor:
   - CPU usage
   - Memory usage
   - Network traffic
   - Monthly cost

---

## Custom Domain (Optional)

### Add Your Own Domain

1. Go to **"Settings"** > **"Networking"**
2. Click **"Custom Domain"**
3. Enter your domain: `api.yourdomain.com`
4. Add the CNAME record to your DNS:
   ```
   CNAME api.yourdomain.com -> your-app.up.railway.app
   ```
5. Wait for DNS propagation (5-30 minutes)

---

## Optimization Tips

### 1. Reduce Memory Usage

Edit `Dockerfile` to use lighter models if needed:

```python
# In your code, use a lighter embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Smaller, faster
)
```

### 2. Monitor Costs

- Check **Usage** tab daily during initial testing
- Set up alerts in Railway for budget limits
- Consider the Hobby plan ($5/month) for predictable costs

### 3. Enable Auto-scaling

Railway auto-scales by default, but you can configure limits:

1. Go to **"Settings"**
2. Set **"Resource Limits"**:
   - Memory: 512MB-1GB (depending on usage)
   - CPU: 1 vCPU

### 4. Optimize Build Time

Use Railway's build cache effectively:
- Dependencies are cached between builds
- Only changes trigger rebuilds

---

## Troubleshooting

### Build Fails

**Error: "Out of memory during build"**

Solution: Add this to `Dockerfile` before pip install:
```dockerfile
ENV PIP_NO_CACHE_DIR=1
```

### App Crashes After Deploy

**Check logs:**
```bash
railway logs
```

**Common issues:**
1. Missing `GENAI_API_KEY` environment variable
2. Volumes not mounted correctly
3. Port configuration (Railway uses `$PORT` env variable)

### ChromaDB Errors

If you see persistence errors:
1. Ensure volumes are correctly mounted to `/app/data` and `/app/chroma_db`
2. Redeploy after adding volumes

### API Returns 503

The app is still starting up. Wait 30-60 seconds after deployment.

---

## Updating Your Deployment

### Automatic Deployments

Railway automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will:
1. Detect the push
2. Build the new image
3. Deploy automatically
4. Keep your data (volumes persist)

### Manual Deployments

In Railway dashboard:
1. Go to **"Deployments"**
2. Click **"Deploy"** on the deployment you want to redeploy

---

## Scaling and Costs

### Free Tier Limits

- $5 credit per month
- ~21,600 minutes of runtime (512MB instance)
- Enough for development and small projects

### When You Need to Upgrade

If you exceed free tier:
- **Hobby Plan**: $5/month base + usage
- **Pro Plan**: $20/month base + usage (for teams)

### Cost Estimation

| Usage Pattern | Estimated Monthly Cost |
|---------------|------------------------|
| Development/Testing | $0 (within free tier) |
| Light production (few users) | $2-5/month |
| Medium production | $10-20/month |
| Heavy production | $30-50/month |

---

## Security Best Practices

### 1. Environment Variables

Never commit `.env` file:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. CORS Configuration

Update `src/app.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. API Rate Limiting

Consider adding rate limiting for production use (Railway provides this in Pro plan).

---

## Backup and Data Management

### Export Your Data

```bash
# SSH into Railway container (if needed)
railway run bash

# Download ChromaDB data
railway volume:get chroma_db ./chroma_db_backup

# Download PDFs
railway volume:get data ./data_backup
```

### Restore Data

```bash
# Upload data to Railway
railway volume:set data ./data_backup
railway volume:set chroma_db ./chroma_db_backup
```

---

## Alternative Deployment Options

If Railway doesn't meet your needs, consider:

### AWS EC2 (Free Tier)
- Free for 12 months
- More control, requires setup
- See `docs/AWS_DEPLOYMENT.md`

### AWS Lightsail
- $5/month for 1GB instance
- Simple interface
- Predictable pricing

### Render.com
- Free tier available
- Similar to Railway
- Persistent disk costs extra

---

## Support and Resources

### Railway Documentation
- https://docs.railway.app

### Querio Documentation
- API Docs: `https://your-app.up.railway.app/docs`
- GitHub: https://github.com/paradocx96/querio

### Community
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/paradocx96/querio/issues

---

## Quick Reference

### Useful Railway CLI Commands

```bash
# View logs
railway logs

# Run commands in Railway environment
railway run python src/app.py

# Open project in browser
railway open

# Check status
railway status

# Link to different project
railway link

# Environment variables
railway variables
```

### API Endpoints

```
Health Check:    GET  /api/health
Upload PDF:      POST /api/documents/upload
Process Docs:    POST /api/documents/process
Query:           POST /api/query
Chat:            POST /api/chat
Search:          POST /api/search
Stats:           GET  /api/stats
```

---

**Deployed successfully? Star the repo and share your experience!**

For issues or questions, open an issue at: https://github.com/paradocx96/querio/issues
