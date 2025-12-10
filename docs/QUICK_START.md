# Quick Start Guide - Deploy in 5 Minutes

The fastest way to deploy Querio API on AWS EC2.

## One-Command Deployment

SSH into your EC2 instance and run:

```bash
curl -sL https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh | bash
```

That's it! The script will:
- ✅ Check prerequisites
- ✅ Clone repository
- ✅ Prompt for API key
- ✅ Deploy with Docker
- ✅ Setup Nginx (optional)
- ✅ Setup HTTPS (optional)

---

## Method 1: Automated Deployment (Recommended)

### Step 1: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@13.213.3.90
```

### Step 2: Download and Run Deploy Script

```bash
# Download the deployment script
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run it
./deploy.sh
```

The script will guide you through:
1. Prerequisites check
2. Repository cloning
3. Environment configuration
4. Docker deployment
5. Nginx setup (optional)
6. HTTPS setup (optional)
7. Systemd service (auto-start)

### Step 3: Access Your API

Visit in your browser:
```
http://13.213.3.90/docs
```

---

## Method 2: Manual Deployment

### Prerequisites

First, run the setup script:

```bash
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
newgrp docker
```

### Deploy Application

```bash
# Clone repository
git clone https://github.com/paradocx96/querio-api.git
cd querio-api

# Create .env file
echo "GENAI_API_KEY=your_google_api_key_here" > .env

# Create directories
mkdir -p data chroma_db

# Deploy
docker-compose up -d --build
```

### Setup Nginx (Optional)

```bash
# Copy nginx config
sudo cp nginx-querio.conf /etc/nginx/sites-available/querio

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Enable querio site
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### Setup HTTPS (Optional)

If you have a domain:

```bash
chmod +x setup-https.sh
./setup-https.sh
```

---

## Method 3: Super Quick Deploy

For those who want the absolute minimum:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@13.213.3.90

# Run quick deploy
bash <(curl -s https://raw.githubusercontent.com/paradocx96/querio-api/main/quick-deploy.sh)
```

---

## Verify Deployment

### Test Health Endpoint

```bash
curl http://13.213.3.90/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Access API Documentation

Open in browser:
- **Swagger UI**: http://13.213.3.90/docs
- **ReDoc**: http://13.213.3.90/redoc

---

## Common Commands

### View Logs
```bash
cd ~/querio
docker-compose logs -f
```

### Restart Application
```bash
cd ~/querio
docker-compose restart
```

### Stop Application
```bash
cd ~/querio
docker-compose down
```

### Update Application
```bash
cd ~/querio
git pull
docker-compose up -d --build
```

### Check Status
```bash
cd ~/querio
docker-compose ps
docker stats
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check memory
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Can't Connect to API

```bash
# Check if container is running
docker-compose ps

# Check if port is open
sudo netstat -tlnp | grep 8000

# Check EC2 Security Group
# Make sure port 8000 or 80 is open
```

### Nginx Issues

```bash
# Check nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View nginx logs
sudo tail -f /var/log/nginx/querio_error.log
```

---

## Script Reference

### Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup-ec2.sh` | Install dependencies | `./setup-ec2.sh` |
| `deploy.sh` | Full deployment | `./deploy.sh` |
| `quick-deploy.sh` | Quick deployment | `./quick-deploy.sh` |
| `setup-https.sh` | Enable HTTPS | `./setup-https.sh` |

### Script Locations

All scripts are in the repository:
```
https://github.com/paradocx96/querio-api/
```

Download individual scripts:
```bash
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/setup-ec2.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/setup-https.sh
```

---

## What Gets Deployed

### Directory Structure
```
~/querio/
├── src/              # Application code
├── data/             # PDF uploads
├── chroma_db/        # Vector database
├── .env              # API keys
├── docker-compose.yml
└── nginx-querio.conf
```

### Services
- **Docker Container**: Runs the FastAPI application
- **Nginx** (optional): Reverse proxy on port 80
- **Systemd Service** (optional): Auto-start on reboot

### Ports
- `8000`: FastAPI direct access
- `80`: Nginx (if configured)
- `443`: HTTPS (if configured)

---

## Cost Estimate

| Component | Cost |
|-----------|------|
| EC2 t2.micro | Free (12 months) then ~$8/month |
| Storage (20GB) | Free (30GB included) |
| Data Transfer | Free (15GB/month) |
| Domain (optional) | $10-15/year |
| **Total** | **Free for 12 months** |

After free tier: ~$8-10/month (without domain)

---

## Security Checklist

After deployment:

- [ ] Change EC2 Security Group to allow only necessary ports
- [ ] Setup HTTPS with Let's Encrypt (if using domain)
- [ ] Enable UFW firewall
- [ ] Setup automated backups
- [ ] Monitor logs regularly
- [ ] Keep system updated

---

## Next Steps

1. **Test the API** - Upload a test PDF
2. **Setup HTTPS** - If you have a domain
3. **Configure monitoring** - Setup CloudWatch or similar
4. **Setup backups** - Automate data backups
5. **Optimize** - Tune for your workload

---

## Getting Help

- **Documentation**: See `AWS_EC2_DEPLOYMENT.md` for detailed guide
- **HTTPS Setup**: See `HTTPS_SETUP.md` for SSL configuration
- **Issues**: https://github.com/paradocx96/querio-api/issues
- **API Docs**: http://your-ip/docs

---

## Example: Complete Deployment

Here's a complete example from start to finish:

```bash
# 1. SSH to EC2
ssh -i my-key.pem ubuntu@13.213.3.90

# 2. Download and run deploy script
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh
chmod +x deploy.sh
./deploy.sh

# 3. Follow prompts:
#    - Enter Google AI API key
#    - Choose to setup Nginx (yes)
#    - Choose to setup HTTPS (if you have domain)
#    - Choose auto-start service (yes)

# 4. Wait for deployment (2-5 minutes)

# 5. Test
curl http://13.213.3.90/api/health

# 6. Open browser
#    http://13.213.3.90/docs

# Done! 🎉
```

---

**That's it! Your Querio API is now live and ready to use.**

For detailed configuration and advanced options, see the full documentation:
- `AWS_EC2_DEPLOYMENT.md` - Complete deployment guide
- `HTTPS_SETUP.md` - SSL/HTTPS configuration
- `README.md` - Project overview and features
