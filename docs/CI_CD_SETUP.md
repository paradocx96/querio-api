# CI/CD Setup Guide - GitHub Actions + Docker Hub + EC2

Complete guide to set up automated deployment pipeline for Querio API.

## Overview

This CI/CD pipeline will:
1. ✅ Build Docker image on push to `deploy` branch
2. ✅ Push image to Docker Hub
3. ✅ SSH to EC2 and pull the latest image
4. ✅ Deploy with docker-compose
5. ✅ Update Nginx if configuration changed
6. ✅ Verify deployment health

---

## Architecture

```
┌─────────────────┐
│   Push to       │
│  Deploy Branch  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│  - Build Image  │
│  - Run Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Docker Hub    │
│ Store Image     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EC2 Server    │
│  - Pull Image   │
│  - Deploy       │
│  - Update Nginx │
└─────────────────┘
```

---

## Prerequisites

### 1. Docker Hub Account
- Sign up at: https://hub.docker.com
- Create repository: `paradocx96/querio-api`

### 2. GitHub Repository
- Repository: https://github.com/paradocx96/querio-api

### 3. EC2 Instance
- Running Ubuntu 22.04
- IP: 3.0.98.108
- Docker and Docker Compose installed
- Nginx configured

---

## Step-by-Step Setup

### Step 1: Configure GitHub Secrets

Go to your GitHub repository:
```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets:

1. **DOCKER_USERNAME**
   - Value: `paradocx96`
   - Description: Your Docker Hub username

2. **DOCKER_PASSWORD**
   - Value: `your_docker_hub_password_or_token`
   - Description: Docker Hub password or access token
   - ⚠️ Recommended: Use access token instead of password

3. **EC2_SSH_KEY**
   - Value: Your EC2 private key content
   - Description: The content of your `.pem` file
   ```bash
   # On your local machine
   cat your-ec2-key.pem
   # Copy the entire content including:
   # -----BEGIN RSA PRIVATE KEY-----
   # ...
   # -----END RSA PRIVATE KEY-----
   ```

---

### Step 2: Create Docker Hub Access Token (Recommended)

1. Log in to Docker Hub
2. Go to: Account Settings → Security → New Access Token
3. Name: `github-actions-querio`
4. Permissions: Read, Write, Delete
5. Copy the token and use it as `DOCKER_PASSWORD` secret

---

### Step 3: Create Deploy Branch

```bash
# On your local machine
cd C:\Projects\Python\querio

# Create and push deploy branch
git checkout -b deploy
git push -u origin deploy

# Switch back to main
git checkout main
```

---

### Step 4: Update EC2 Setup

SSH to your EC2 instance and prepare for automated deployments:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.0.98.108

# Navigate to project directory
cd ~/querio-api

# Switch to deploy branch
git checkout deploy

# Pull latest changes
git pull

# Make sure .env file exists
ls -la .env

# If .env doesn't exist, create it
nano .env
# Add: GENAI_API_KEY=your_api_key_here

# Create data directories if they don't exist
mkdir -p data chroma_db

# Setup nginx if not already done
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio-api
sudo ln -sf /etc/nginx/sites-available/querio-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

### Step 5: Test the Pipeline

#### Option 1: Push to Deploy Branch

```bash
# On your local machine
cd C:\Projects\Python\querio

# Make a change
echo "# Test CI/CD" >> README.md

# Commit and push to deploy branch
git checkout deploy
git add .
git commit -m "Test CI/CD pipeline"
git push origin deploy
```

#### Option 2: Manual Trigger

1. Go to GitHub: Actions → Build and Deploy to EC2
2. Click "Run workflow"
3. Select branch: `deploy`
4. Click "Run workflow"

---

### Step 6: Monitor Deployment

Watch the GitHub Actions workflow:
```
GitHub Repository → Actions → Build and Deploy to EC2
```

You'll see:
1. ✅ Build and Push job
   - Checkout code
   - Build Docker image
   - Push to Docker Hub

2. ✅ Deploy job
   - SSH to EC2
   - Pull latest code
   - Pull Docker image
   - Deploy containers
   - Update Nginx
   - Health check

---

## Workflow Explained

### Workflow File: `.github/workflows/deploy.yml`

**Triggers:**
- Push to `deploy` branch
- Manual trigger via GitHub UI

**Jobs:**

#### 1. Build and Push
```yaml
- Checkout code
- Setup Docker Buildx
- Login to Docker Hub
- Build Docker image
- Push to Docker Hub with tags:
  - latest
  - deploy
  - deploy-{commit-sha}
```

#### 2. Deploy
```yaml
- SSH to EC2
- Pull latest code from deploy branch
- Pull latest Docker image
- Stop old containers
- Start new containers
- Clean up old images
- Health check
- Update Nginx if config changed
```

---

## Deployment Workflow

### Development → Staging → Production

```bash
# 1. Develop on main branch
git checkout main
# ... make changes ...
git commit -m "Add new feature"
git push origin main

# 2. When ready to deploy, merge to deploy branch
git checkout deploy
git merge main
git push origin deploy

# 3. GitHub Actions automatically deploys to EC2
```

---

## Managing Deployments

### View Deployed Version

```bash
# On EC2
docker ps
docker images | grep querio-api

# Check running version
curl http://localhost:8000/api/health
```

### Rollback to Previous Version

```bash
# On EC2
cd ~/querio-api

# Pull specific image version
docker pull paradocx96/querio-api:deploy-abc1234

# Update docker-compose to use specific version
nano docker-compose.yml
# Change: image: paradocx96/querio-api:deploy-abc1234

# Redeploy
docker-compose down
docker-compose up -d
```

### Manual Deployment

```bash
# On EC2
cd ~/querio-api
git pull origin deploy
docker-compose pull
docker-compose up -d
```

---

## Environment Variables

### EC2 Environment Variables

The `.env` file on EC2 must contain:

```bash
GENAI_API_KEY=your_google_api_key_here
```

**Important:**
- .env file is NOT in git (it's in .gitignore)
- Must be manually created on EC2
- Persists across deployments
- Never commit to repository

### Adding New Environment Variables

1. **Add to `.env` on EC2:**
   ```bash
   ssh ubuntu@3.0.98.108
   cd ~/querio-api
   nano .env
   # Add: NEW_VARIABLE=value
   ```

2. **Update docker-compose.yml:**
   ```yaml
   environment:
     - GENAI_API_KEY=${GENAI_API_KEY}
     - NEW_VARIABLE=${NEW_VARIABLE}
   ```

3. **Commit and push to trigger deployment:**
   ```bash
   git add docker-compose.yml
   git commit -m "Add new environment variable"
   git push origin deploy
   ```

---

## Nginx Configuration Updates

### Automatic Nginx Updates

The workflow automatically detects nginx config changes:

```bash
# If nginx/nginx-querio.conf changed:
- Copies new config to /etc/nginx/sites-available/
- Tests configuration
- Reloads nginx
```

### Manual Nginx Update

```bash
# On EC2
cd ~/querio-api
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio-api
sudo nginx -t
sudo systemctl reload nginx
```

---

## Troubleshooting

### Build Fails on GitHub Actions

**Check:**
- Docker Hub credentials in GitHub Secrets
- Dockerfile syntax
- Build logs in GitHub Actions

**Solution:**
```bash
# Test build locally
docker build -t querio-api .
```

### Deployment Fails

**Check:**
- EC2_SSH_KEY secret is correct
- EC2 instance is running
- Port 22 is open in security group

**Solution:**
```bash
# Test SSH connection
ssh -i your-key.pem ubuntu@3.0.98.108
```

### Container Doesn't Start

**Check logs on EC2:**
```bash
cd ~/querio-api
docker-compose logs
```

**Common issues:**
- Missing .env file
- Wrong API key
- Out of memory

### Health Check Fails

**Check application:**
```bash
# On EC2
curl http://localhost:8000/api/health

# Check logs
docker-compose logs querio-api
```

---

## Advanced Configuration

### Multi-Environment Setup

Create separate branches:
- `develop` → Dev environment
- `staging` → Staging environment
- `production` → Production environment

### Add Tests to Pipeline

Edit `.github/workflows/deploy.yml`:

```yaml
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/
```

### Slack Notifications

Add to workflow:

```yaml
  - name: Slack Notification
    uses: 8398a7/action-slack@v3
    with:
      status: ${{ job.status }}
      text: 'Deployment to EC2 completed!'
      webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    if: always()
```

---

## Security Best Practices

### 1. Use Access Tokens
- ✅ Use Docker Hub access tokens instead of passwords
- ✅ Use GitHub deploy keys for EC2

### 2. Limit SSH Access
```bash
# On EC2 - Only allow GitHub Actions IP ranges
sudo ufw allow from 192.30.252.0/22 to any port 22
```

### 3. Rotate Secrets Regularly
- Change Docker Hub tokens every 90 days
- Rotate SSH keys periodically

### 4. Use Environment-Specific Secrets
- Different API keys for dev/staging/prod
- Separate Docker Hub repositories

---

## Monitoring & Alerts

### GitHub Actions Notifications

Enable in GitHub:
```
Settings → Notifications → Actions
✅ Only notify for failed workflows
```

### EC2 Monitoring

**CloudWatch alarms:**
- High CPU usage
- Low disk space
- Application downtime

**Simple uptime monitoring:**
```bash
# Add to crontab on separate monitoring server
*/5 * * * * curl -f http://3.0.98.108/api/health || mail -s "API Down" your@email.com
```

---

## Cost Optimization

### Docker Hub
- Free tier: Unlimited public repositories
- Image pulls: 200/6 hours (free tier)
- Consider caching to reduce pulls

### GitHub Actions
- Free tier: 2,000 minutes/month
- Optimize workflow to reduce run time
- Cache Docker layers

### EC2
- Use t2.micro (free tier eligible)
- Stop instance when not needed
- Consider reserved instances for production

---

## Deployment Checklist

### Before First Deployment
- [ ] GitHub secrets configured
- [ ] Docker Hub repository created
- [ ] EC2 instance prepared
- [ ] .env file created on EC2
- [ ] Nginx configured
- [ ] Deploy branch created

### Every Deployment
- [ ] Changes committed to main
- [ ] Merged to deploy branch
- [ ] GitHub Actions completed successfully
- [ ] Health check passed
- [ ] Application accessible

---

## Quick Commands Reference

### Local Development
```bash
# Build locally
docker-compose up --build

# Test build
docker build -t querio-api .
```

### EC2 Management
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.0.98.108

# View logs
cd ~/querio-api
docker-compose logs -f

# Restart
docker-compose restart

# Update manually
git pull origin deploy
docker-compose pull
docker-compose up -d
```

### GitHub Actions
```bash
# View workflow runs
gh run list --workflow=deploy.yml

# Watch live
gh run watch

# Trigger manually
gh workflow run deploy.yml --ref deploy
```

---

## Support

**Documentation:**
- GitHub Actions: https://docs.github.com/actions
- Docker Hub: https://docs.docker.com/docker-hub/
- Docker Compose: https://docs.docker.com/compose/

**Issues:**
- GitHub: https://github.com/paradocx96/querio-api/issues

---

**Your CI/CD pipeline is now ready!** 🚀

Push to the `deploy` branch and watch your application automatically deploy to EC2!
