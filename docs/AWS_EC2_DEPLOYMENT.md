# AWS EC2 Deployment Guide

Complete guide to deploy Querio RAG API on AWS EC2 Free Tier (t2.micro).

## Cost Overview

- **Free Tier**: 750 hours/month for 12 months
- **Instance**: t2.micro (1 vCPU, 1GB RAM)
- **Storage**: 30GB EBS (free tier)
- **Data Transfer**: 15GB/month outbound (free tier)
- **After 12 months**: ~$8-10/month

---

## Prerequisites

- AWS Account (sign up at https://aws.amazon.com)
- Google AI API key (from https://makersuite.google.com/app/apikey)
- SSH client (Terminal on Mac/Linux, PuTTY on Windows)
- GitHub repository with your code

---

## Part 1: Launch EC2 Instance

### Step 1: Access EC2 Dashboard

1. Log in to AWS Console: https://console.aws.amazon.com
2. Search for "EC2" in the top search bar
3. Click on **EC2** service

### Step 2: Launch Instance

1. Click **"Launch Instance"** button
2. Configure the following:

**Name and Tags:**
```
Name: querio-api
```

**Application and OS Images (AMI):**
- Select: **Ubuntu Server 22.04 LTS**
- Architecture: **64-bit (x86)**
- Free tier eligible

**Instance Type:**
- Select: **t2.micro** (Free tier eligible)
- 1 vCPU, 1 GB RAM

**Key Pair (Login):**
- Click **"Create new key pair"**
- Key pair name: `querio-key`
- Key pair type: RSA
- Private key format: `.pem` (Mac/Linux) or `.ppk` (Windows/PuTTY)
- Click **"Create key pair"** and save the file securely

**Network Settings:**
- Click **"Edit"**
- Auto-assign public IP: **Enable**

**Configure Security Group:**
- Security group name: `querio-sg`
- Description: `Security group for Querio API`

**Add the following inbound rules:**

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | Anywhere (0.0.0.0/0) | HTTP access |
| HTTPS | TCP | 443 | Anywhere (0.0.0.0/0) | HTTPS access (future) |
| Custom TCP | TCP | 8000 | Anywhere (0.0.0.0/0) | API direct access |

**Configure Storage:**
- Size: **20 GB** (or up to 30GB, free tier includes 30GB)
- Volume type: **gp3** (General Purpose SSD)

3. Click **"Launch Instance"**

### Step 3: Wait for Instance to Start

- Go to **Instances** in the left sidebar
- Wait until **Instance State** shows "Running"
- Wait until **Status Checks** shows "2/2 checks passed"
- Note your **Public IPv4 address** (e.g., 54.123.45.67)

---

## Part 2: Connect to EC2 Instance

### For Mac/Linux Users:

```bash
# Set permissions for your key file
chmod 400 ~/Downloads/querio-key.pem

# Connect to EC2
ssh -i ~/Downloads/querio-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### For Windows Users:

**Option 1: Using PowerShell/Command Prompt**
```bash
ssh -i C:\path\to\querio-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**Option 2: Using PuTTY**
1. Convert `.pem` to `.ppk` using PuTTYgen
2. Open PuTTY
3. Host: `ubuntu@YOUR_EC2_PUBLIC_IP`
4. Connection > SSH > Auth: Browse and select `.ppk` file
5. Click **Open**

### First Connection

- Type `yes` when prompted about authenticity
- You should see the Ubuntu welcome message

---

## Part 3: Setup EC2 Instance

### Step 1: Run Setup Script

Once connected to your EC2 instance:

```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/paradocx96/querio/main/setup-ec2.sh

# Make it executable
chmod +x setup-ec2.sh

# Run the setup script
./setup-ec2.sh
```

The script will install:
- Docker
- Docker Compose
- Git
- Nginx
- Other utilities

**After installation, apply Docker permissions:**
```bash
newgrp docker
```

### Step 2: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/paradocx96/querio.git

# Navigate to project directory
cd querio
```

### Step 3: Create Environment File

```bash
# Create .env file
nano .env
```

Add the following content:
```bash
GENAI_API_KEY=your_google_api_key_here
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter`

### Step 4: Create Required Directories

```bash
# Create data and chroma_db directories
mkdir -p data chroma_db

# Set proper permissions
chmod 755 data chroma_db
```

---

## Part 4: Deploy with Docker

### Build and Start the Application

```bash
# Build and start containers
docker-compose up -d --build
```

This will:
- Build the Docker image
- Start the container in detached mode
- Map port 8000 to host

### Verify Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Check if API is running
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Test External Access

From your local machine:
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/api/health
```

Access in browser:
```
http://YOUR_EC2_PUBLIC_IP:8000/docs
```

---

## Part 5: Setup Nginx Reverse Proxy (Optional but Recommended)

### Why Use Nginx?

- Access API on port 80 (standard HTTP)
- Enable HTTPS with SSL certificates
- Better performance and caching
- Load balancing (for future scaling)

### Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx-querio.conf /etc/nginx/sites-available/querio

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Enable querio site
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Test Nginx

```bash
# Local test
curl http://localhost/api/health

# From your machine
curl http://YOUR_EC2_PUBLIC_IP/api/health
```

Now you can access:
```
http://YOUR_EC2_PUBLIC_IP/docs
http://YOUR_EC2_PUBLIC_IP/api/health
```

---

## Part 6: Setup Systemd Service (Auto-start on Reboot)

### Create Systemd Service

```bash
# Copy service file
sudo cp querio.service /etc/systemd/system/

# Edit the service file to match your username and path
sudo nano /etc/systemd/system/querio.service
```

Ensure paths are correct:
```ini
WorkingDirectory=/home/ubuntu/querio
User=ubuntu
Group=ubuntu
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable querio

# Start the service
sudo systemctl start querio

# Check status
sudo systemctl status querio
```

### Test Auto-restart

```bash
# Reboot EC2
sudo reboot

# After reboot, SSH back and check
docker-compose ps
curl http://localhost/api/health
```

---

## Part 7: Testing Your Deployment

### Test API Endpoints

**Upload a PDF:**
```bash
curl -X POST "http://YOUR_EC2_PUBLIC_IP/api/documents/upload" \
  -F "file=@/path/to/your/document.pdf"
```

**Process Documents:**
```bash
curl -X POST "http://YOUR_EC2_PUBLIC_IP/api/documents/process"
```

**Query:**
```bash
curl -X POST "http://YOUR_EC2_PUBLIC_IP/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "k": 3}'
```

**Chat:**
```bash
curl -X POST "http://YOUR_EC2_PUBLIC_IP/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the documents"}'
```

### Access Interactive Documentation

Visit in your browser:
- **Swagger UI**: `http://YOUR_EC2_PUBLIC_IP/docs`
- **ReDoc**: `http://YOUR_EC2_PUBLIC_IP/redoc`

---

## Part 8: Setup SSL with Let's Encrypt (Optional)

### Prerequisites

- Own a domain name
- Point domain A record to your EC2 public IP

### Install Certbot

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Follow prompts to configure SSL
```

### Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

### Update Nginx Configuration

Edit `/etc/nginx/sites-available/querio` and uncomment the HTTPS section, replacing `your-domain.com` with your actual domain.

---

## Part 9: Monitoring and Maintenance

### View Logs

```bash
# Docker logs
docker-compose logs -f

# Nginx access logs
sudo tail -f /var/log/nginx/querio_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/querio_error.log

# System logs
sudo journalctl -u querio -f
```

### Monitor Resources

```bash
# System resources
htop

# Docker container stats
docker stats

# Disk usage
df -h

# Check memory
free -h
```

### Common Commands

```bash
# Restart application
cd ~/querio
docker-compose restart

# Update application
git pull
docker-compose up -d --build

# Stop application
docker-compose down

# View all containers
docker ps -a

# Clean up unused images
docker image prune -a
```

---

## Part 10: Backup and Security

### Backup Data

```bash
# Backup PDFs and ChromaDB
cd ~/querio
tar -czf backup-$(date +%Y%m%d).tar.gz data/ chroma_db/

# Download to local machine (run from your computer)
scp -i ~/Downloads/querio-key.pem ubuntu@YOUR_EC2_PUBLIC_IP:~/querio/backup-*.tar.gz ./
```

### Security Best Practices

**1. Update Security Group:**
```bash
# Remove port 8000 from public access after setting up nginx
# Keep only ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

**2. Keep System Updated:**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**3. Setup Firewall (UFW):**
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

**4. Disable Root Login:**
```bash
sudo nano /etc/ssh/sshd_config
```
Set: `PermitRootLogin no`

Restart SSH:
```bash
sudo systemctl restart sshd
```

---

## Troubleshooting

### Issue 1: Cannot Connect to EC2

**Check:**
- Security group allows SSH (port 22) from your IP
- Instance is running
- Using correct key file and username (ubuntu)

**Solution:**
```bash
# Check security group in AWS Console
# Update your IP if it changed
```

### Issue 2: Docker Build Fails (Out of Memory)

**Problem:** t2.micro has only 1GB RAM

**Solution 1 - Add Swap:**
```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make it permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Solution 2 - Build without cache:**
```bash
docker-compose build --no-cache --memory=900m
```

### Issue 3: Application Crashes

**Check logs:**
```bash
docker-compose logs querio-api

# Check if out of memory
dmesg | grep -i "out of memory"
```

**Solution:**
- Add swap space (see above)
- Consider upgrading to t2.small ($0.023/hour)

### Issue 4: Nginx 502 Bad Gateway

**Check:**
```bash
# Is container running?
docker-compose ps

# Check container logs
docker-compose logs

# Test direct connection
curl http://localhost:8000/api/health
```

**Solution:**
```bash
# Restart containers
docker-compose restart

# Restart nginx
sudo systemctl restart nginx
```

### Issue 5: ChromaDB Persistence Issues

**Check permissions:**
```bash
ls -la chroma_db/
```

**Fix permissions:**
```bash
sudo chown -R ubuntu:ubuntu chroma_db/
chmod 755 chroma_db/
```

---

## Updating Your Application

### Pull Latest Changes

```bash
# SSH into EC2
ssh -i ~/Downloads/querio-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Navigate to project
cd ~/querio

# Pull changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

---

## Stopping and Cleaning Up

### Stop Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Terminate EC2 Instance

1. Go to EC2 Console
2. Select your instance
3. Instance State > Terminate Instance
4. Confirm

**Note:** This is permanent and will delete all data!

---

## Cost Optimization Tips

### 1. Use Free Tier Wisely

- Monitor usage in AWS Billing Dashboard
- Set up billing alerts
- Free tier: 750 hours/month (one t2.micro running 24/7)

### 2. Stop Instance When Not Needed

```bash
# Stop instance (preserves data, no charges except storage)
# From AWS Console: Instance State > Stop
```

**Restart later:**
```bash
# From AWS Console: Instance State > Start
# Note: Public IP may change
```

### 3. Monitor Costs

- AWS Billing Dashboard: https://console.aws.amazon.com/billing/
- Set up budget alerts
- Enable cost explorer

---

## Upgrading Instance (If Needed)

If t2.micro is too small:

### Option 1: Upgrade to t2.small
- 2GB RAM
- Cost: ~$0.023/hour (~$17/month)

### Option 2: Use t3.micro (Burstable)
- 2 vCPU, 1GB RAM (better performance)
- Cost: ~$0.0104/hour (~$7.50/month)

**How to upgrade:**
1. Stop instance
2. Instance Settings > Change Instance Type
3. Select new type
4. Start instance

---

## Quick Reference

### Essential Commands

```bash
# SSH to EC2
ssh -i ~/Downloads/querio-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Navigate to project
cd ~/querio

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Start
docker-compose up -d

# Rebuild
docker-compose up -d --build

# Check status
docker-compose ps
curl http://localhost/api/health
```

### AWS Console Quick Links

- EC2 Dashboard: https://console.aws.amazon.com/ec2/
- Billing: https://console.aws.amazon.com/billing/
- Security Groups: EC2 > Network & Security > Security Groups

---

## Support

### Resources

- AWS Free Tier: https://aws.amazon.com/free/
- Docker Documentation: https://docs.docker.com/
- Nginx Documentation: https://nginx.org/en/docs/

### Community

- GitHub Issues: https://github.com/paradocx96/querio/issues
- AWS Forums: https://forums.aws.amazon.com/

---

## Next Steps

After deployment:

1. **Test all endpoints** using the Swagger UI
2. **Upload test documents** and verify functionality
3. **Setup monitoring** (CloudWatch, logs)
4. **Configure domain** and SSL (if needed)
5. **Setup backups** (automated scripts)
6. **Monitor costs** in AWS Billing

---

**Congratulations! Your Querio API is now live on AWS EC2!**

Access your API at: `http://YOUR_EC2_PUBLIC_IP/docs`

For questions or issues, open a GitHub issue or contact support.
