# CI/CD Quick Start - 10 Minutes Setup

Quick guide to set up automated deployments with GitHub Actions.

## What You'll Get

✅ Push to `deploy` branch → Automatic deployment to EC2
✅ Docker image built and stored in Docker Hub
✅ Zero-downtime deployments
✅ Automatic nginx updates
✅ Health checks after deployment

---

## Setup Steps (10 minutes)

### 1. Docker Hub Setup (2 min)

```bash
# 1. Sign up at: https://hub.docker.com (if you don't have an account)
# 2. Create access token:
#    - Go to: Account Settings → Security → New Access Token
#    - Name: github-actions-querio
#    - Permissions: Read, Write, Delete
#    - SAVE THE TOKEN (you'll need it in step 2)
```

---

### 2. GitHub Secrets Setup (3 min)

Go to: `https://github.com/paradocx96/querio-api/settings/secrets/actions`

Add these 3 secrets:

**Secret 1: DOCKER_USERNAME**
```
Value: paradocx96
```

**Secret 2: DOCKER_PASSWORD**
```
Value: <paste your Docker Hub access token from step 1>
```

**Secret 3: EC2_SSH_KEY**
```bash
# On your local computer, copy your EC2 key content:
cat your-ec2-key.pem
# Copy EVERYTHING including:
# -----BEGIN RSA PRIVATE KEY-----
# ... (all the key content)
# -----END RSA PRIVATE KEY-----
# Paste as the secret value
```

---

### 3. Create Deploy Branch (1 min)

```bash
# On your local machine
cd C:\Projects\Python\querio

git checkout -b deploy
git push -u origin deploy
git checkout main
```

---

### 4. Prepare EC2 (4 min)

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.0.98.108

# Navigate and switch to deploy branch
cd ~/querio-api
git fetch
git checkout deploy
git pull

# Verify .env exists (should have GENAI_API_KEY)
cat .env

# If missing, create it:
nano .env
# Add: GENAI_API_KEY=your_google_api_key_here
# Save: Ctrl+X, Y, Enter

# Verify nginx is setup
ls /etc/nginx/sites-enabled/querio-api

# If nginx not setup, run:
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio-api
sudo ln -sf /etc/nginx/sites-available/querio-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Exit EC2
exit
```

---

## ✅ Test Your Pipeline

### Option 1: Push to Deploy (Recommended)

```bash
# On your local machine
cd C:\Projects\Python\querio

# Make a test change
echo "# CI/CD Pipeline Active" >> README.md

# Commit and push to deploy branch
git checkout deploy
git add .
git commit -m "Test: CI/CD pipeline"
git push origin deploy

# Watch the action: https://github.com/paradocx96/querio-api/actions
```

### Option 2: Manual Trigger

1. Go to: https://github.com/paradocx96/querio-api/actions
2. Click: "Build and Deploy to EC2"
3. Click: "Run workflow" button
4. Select branch: `deploy`
5. Click: "Run workflow"

---

## 🎯 What Happens Next

1. **GitHub Actions starts** (30 seconds)
   - Checks out your code
   - Logs into Docker Hub

2. **Builds Docker image** (3-5 minutes)
   - Builds your application
   - Pushes to Docker Hub

3. **Deploys to EC2** (1-2 minutes)
   - SSH to your EC2
   - Pulls latest code
   - Pulls Docker image
   - Restarts containers
   - Updates nginx if needed
   - Runs health check

4. **Done!** (Total: ~5-8 minutes)
   - Access: http://3.0.98.108/docs
   - Your app is live!

---

## 📊 Monitor Your Deployment

### Watch GitHub Actions
```
https://github.com/paradocx96/querio-api/actions
```

You'll see:
- ✅ Build and push Docker image
- ✅ Deploy to EC2
- ✅ Update Nginx
- ✅ Health check passed

### Check EC2
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.0.98.108

# Check running containers
docker ps

# View logs
cd ~/querio-api
docker-compose logs -f

# Test API
curl http://localhost/api/health
```

---

## 🚀 Daily Workflow

### Development
```bash
# Work on main branch
git checkout main
# ... make changes ...
git add .
git commit -m "Add new feature"
git push origin main
```

### Deploy to Production
```bash
# Merge to deploy branch
git checkout deploy
git merge main
git push origin deploy

# GitHub Actions automatically deploys!
# No manual SSH or docker commands needed!
```

---

## 🔥 Quick Troubleshooting

### Build fails?
**Check:** GitHub Actions logs
**Fix:** Look for error in "Build and push Docker image" step

### Deploy fails?
**Check:** EC2_SSH_KEY secret is correct
**Fix:** Copy your entire .pem file content as secret

### Health check fails?
**Check:** `.env` file exists on EC2
**Fix:** SSH to EC2, create `.env` with GENAI_API_KEY

### Container not starting?
**Check:** EC2 memory
**Fix:** Add swap space (see troubleshooting guide)

---

## 📚 Full Documentation

For detailed information:
- [CI/CD Setup Guide](CI_CD_SETUP.md) - Complete guide
- [GitHub Actions Workflow](../.github/workflows/deploy.yml) - Workflow file
- [Docker Compose](../docker-compose.yml) - Container config

---

## ✨ What's Different Now?

**Before (Manual):**
```bash
ssh ubuntu@3.0.98.108
cd ~/querio-api
git pull
docker-compose up -d --build
# Wait 5-10 minutes...
# Hope it works...
```

**After (Automated):**
```bash
git push origin deploy
# Done! GitHub Actions handles everything
# Get notified when deployment completes
# Automatic rollback if health check fails
```

---

## 🎉 You're All Set!

Your CI/CD pipeline is ready. From now on:

1. **Develop** on `main` branch
2. **Push** to `deploy` branch when ready
3. **Relax** - GitHub Actions handles the rest!

**Test it now:**
```bash
cd C:\Projects\Python\querio
echo "# Test" >> README.md
git checkout deploy
git add .
git commit -m "Test CI/CD"
git push origin deploy
```

Watch it deploy automatically at:
https://github.com/paradocx96/querio-api/actions

🚀 **Welcome to automated deployments!**
