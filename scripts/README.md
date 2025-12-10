# Deployment Scripts

This directory contains all deployment and setup scripts for the Querio API.

## Scripts

### 1. setup-ec2.sh
**Purpose**: Initial server setup - installs all dependencies

**What it installs:**
- Docker and Docker Compose
- Git
- Nginx
- Essential utilities (curl, htop, vim)

**Usage:**
```bash
chmod +x setup-ec2.sh
./setup-ec2.sh
newgrp docker  # Activate Docker permissions
```

**When to use:** Run once on a new EC2 instance before deploying the application.

---

### 2. deploy.sh ⭐ (Recommended)
**Purpose**: Complete automated deployment with interactive prompts

**What it does:**
- Checks prerequisites
- Clones repository
- Configures environment (.env file)
- Deploys Docker containers
- Sets up Nginx (optional)
- Configures HTTPS (optional)
- Enables auto-start service (optional)

**Usage:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**When to use:** For full deployment with all options. Best for first-time deployment.

---

### 3. quick-deploy.sh
**Purpose**: Simplified quick deployment with minimal prompts

**What it does:**
- Checks and installs dependencies if missing
- Clones or updates repository
- Prompts for API key
- Deploys application
- Optional Nginx setup

**Usage:**
```bash
chmod +x quick-deploy.sh
./quick-deploy.sh
```

**When to use:** For fast deployment or updates with fewer configuration options.

---

### 4. setup-https.sh
**Purpose**: Automated HTTPS/SSL setup with Let's Encrypt

**What it does:**
- Installs Certbot
- Updates nginx configuration
- Obtains SSL certificate
- Configures auto-renewal

**Usage:**
```bash
chmod +x setup-https.sh
./setup-https.sh
```

**Requirements:**
- Domain name
- DNS pointing to server
- Nginx already configured
- Ports 80 and 443 open

**When to use:** After deploying the application when you want to enable HTTPS.

---

## Deployment Flow

### Option 1: Full Automated Deployment
```bash
# One command does everything
./scripts/deploy.sh
```

### Option 2: Step-by-Step Manual
```bash
# Step 1: Setup dependencies
./scripts/setup-ec2.sh
newgrp docker

# Step 2: Deploy application
cd ~/querio
echo "GENAI_API_KEY=your_key" > .env
mkdir -p data chroma_db
docker-compose up -d --build

# Step 3: Setup Nginx (optional)
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Step 4: Setup HTTPS (optional)
./scripts/setup-https.sh
```

### Option 3: Quick Deploy
```bash
# Minimal prompts, fast deployment
./scripts/quick-deploy.sh
```

---

## Script Features

### Color-Coded Output
All scripts use colored output for better visibility:
- 🟢 Green: Success messages
- 🔴 Red: Error messages
- 🟡 Yellow: Warning messages
- 🔵 Blue: Info messages

### Error Handling
- All scripts use `set -e` to exit on errors
- Validation checks before each step
- Clear error messages with troubleshooting hints

### Safety Features
- Backup existing configurations before overwriting
- Permission checks (won't run as root)
- Dry-run options where applicable
- Confirmation prompts for destructive actions

---

## GitHub URLs

When downloading scripts directly:

```bash
# setup-ec2.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/setup-ec2.sh

# deploy.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/deploy.sh

# quick-deploy.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/quick-deploy.sh

# setup-https.sh
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/setup-https.sh
```

---

## Troubleshooting

### Script won't execute
```bash
chmod +x scriptname.sh
```

### Permission denied for Docker
```bash
newgrp docker
# Or logout and login again
```

### Script fails partway through
- Check the error message for specific issues
- View full logs if available
- Retry the script (most are idempotent)

---

## Contributing

When modifying scripts:
1. Test on a clean EC2 instance
2. Update this README if functionality changes
3. Keep error messages clear and helpful
4. Maintain backward compatibility where possible

---

**For detailed documentation, see:**
- [QUICK_START.md](../QUICK_START.md) - Quick deployment guide
- [AWS_EC2_DEPLOYMENT.md](../AWS_EC2_DEPLOYMENT.md) - Full deployment documentation
- [HTTPS_SETUP.md](../HTTPS_SETUP.md) - SSL configuration guide
