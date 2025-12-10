# Project Structure

Complete overview of the Querio API project organization.

## Directory Tree

```
querio/
├── src/                          # Application source code
│   ├── api/                      # FastAPI routes and models
│   │   ├── routes/
│   │   │   ├── query.py         # Query endpoints
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── documents.py     # Document management
│   │   │   ├── search.py        # Search endpoints
│   │   │   └── system.py        # Health & stats
│   │   ├── models.py            # Pydantic models
│   │   ├── services.py          # Business logic
│   │   └── dependencies.py      # Dependency injection
│   ├── app.py                   # FastAPI application
│   ├── config.py                # Configuration settings
│   ├── pdf_handler.py           # PDF processing
│   ├── text_splitter.py         # Text chunking
│   ├── vector_store.py          # Vector DB operations
│   └── rag_pipeline.py          # RAG logic
│
├── scripts/                      # Deployment & setup scripts
│   ├── setup-ec2.sh             # Install dependencies
│   ├── deploy.sh                # Full automated deployment
│   ├── quick-deploy.sh          # Quick deployment
│   ├── setup-https.sh           # HTTPS/SSL setup
│   └── README.md                # Scripts documentation
│
├── nginx/                        # Nginx configurations
│   ├── nginx-querio.conf        # Unified HTTP/HTTPS config
│   └── README.md                # Nginx documentation
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md     # API reference
│   └── STORAGE_RECOMMENDATIONS.md
│
├── data/                         # PDF storage (created at runtime)
├── chroma_db/                    # Vector database (created at runtime)
│
├── docker-compose.yml            # Docker Compose config
├── Dockerfile                    # Container definition
├── .dockerignore                 # Docker build exclusions
├── querio.service                # Systemd service file
├── requirements.txt              # Python dependencies
├── environment.yml               # Conda environment
├── .env                          # Environment variables (not in git)
│
└── Documentation Files
    ├── README.md                 # Project overview
    ├── QUICK_START.md           # Quick deployment guide
    ├── AWS_EC2_DEPLOYMENT.md    # Complete EC2 guide
    ├── HTTPS_SETUP.md           # SSL configuration guide
    ├── DEPLOYMENT_SUMMARY.md    # Deployment overview
    └── PROJECT_STRUCTURE.md     # This file
```

---

## Core Directories

### `/src` - Application Code
The main application source code.

**Key Files:**
- `app.py` - FastAPI application entry point
- `config.py` - Configuration management
- `rag_pipeline.py` - RAG implementation
- `vector_store.py` - ChromaDB operations

**API Structure:**
```
src/api/
├── routes/      # API endpoints organized by domain
├── models.py    # Request/response models
├── services.py  # Business logic layer
└── dependencies.py  # Dependency injection
```

### `/scripts` - Deployment Scripts
All automation scripts for deployment and setup.

**Usage:**
```bash
# Run from project root
./scripts/setup-ec2.sh
./scripts/deploy.sh
./scripts/setup-https.sh
```

**What each script does:**
- `setup-ec2.sh` - First-time server setup (Docker, Nginx, etc.)
- `deploy.sh` - Complete deployment with all options
- `quick-deploy.sh` - Fast deployment with minimal prompts
- `setup-https.sh` - SSL certificate setup

### `/nginx` - Web Server Config
Nginx reverse proxy configuration.

**Contains:**
- `nginx-querio.conf` - Single unified configuration
  - HTTP configuration (active by default)
  - HTTPS configuration (commented, ready to enable)

**Usage:**
```bash
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### `/docs` - Documentation
API and technical documentation.

### `/data` - PDF Storage
Runtime directory for uploaded PDF files.
- Created automatically on deployment
- Persistent across container restarts
- Backed by Docker volume

### `/chroma_db` - Vector Database
ChromaDB persistent storage.
- Created automatically on first use
- Contains embeddings and metadata
- Backed by Docker volume

---

## Configuration Files

### Docker
- **Dockerfile** - Container image definition
- **docker-compose.yml** - Service orchestration
- **.dockerignore** - Build optimization

### Python
- **requirements.txt** - Python dependencies (pip)
- **environment.yml** - Conda environment spec
- **.env** - Environment variables (API keys)

### System
- **querio.service** - Systemd service for auto-start

---

## Documentation Files

### Quick Reference
- **QUICK_START.md** - Fastest way to deploy (5 minutes)
- **PROJECT_STRUCTURE.md** - This file

### Complete Guides
- **AWS_EC2_DEPLOYMENT.md** - Step-by-step EC2 deployment
- **HTTPS_SETUP.md** - SSL/HTTPS configuration
- **DEPLOYMENT_SUMMARY.md** - Overview of all deployment files

### Project Info
- **README.md** - Project overview and features
- **API_DOCUMENTATION.md** - Complete API reference

---

## File Locations Reference

### Old Structure → New Structure

| Old Location | New Location | Type |
|--------------|--------------|------|
| `/setup-ec2.sh` | `/scripts/setup-ec2.sh` | Script |
| `/deploy.sh` | `/scripts/deploy.sh` | Script |
| `/quick-deploy.sh` | `/scripts/quick-deploy.sh` | Script |
| `/setup-https.sh` | `/scripts/setup-https.sh` | Script |
| `/nginx-querio.conf` | `/nginx/nginx-querio.conf` | Config |
| `/nginx-querio-https.conf` | ❌ Removed (merged) | Config |

### Important Notes
- **Single nginx config**: HTTP and HTTPS in one file
- **Scripts organized**: All deployment scripts in `/scripts`
- **Documentation updated**: All guides reference new paths

---

## Quick Commands

### Deployment
```bash
# Clone repository
git clone https://github.com/paradocx96/querio-api.git
cd querio-api

# Full automated deployment
./scripts/deploy.sh

# Quick deployment
./scripts/quick-deploy.sh

# Setup HTTPS
./scripts/setup-https.sh
```

### Docker
```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Nginx
```bash
# Install config
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/querio_access.log
```

---

## Development Workflow

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/paradocx96/querio-api.git
cd querio-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "GENAI_API_KEY=your_key" > .env

# 5. Run application
cd src
python app.py
```

### Production Deployment
```bash
# 1. SSH to server
ssh -i your-key.pem ubuntu@3.0.98.108

# 2. Run deployment script
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

---

## Environment Variables

### Required
- `GENAI_API_KEY` - Google AI API key (required)

### Optional
- `PORT` - Server port (default: 8000)
- `PDF_FOLDER` - PDF storage path (default: data/)
- `CHROMA_DB` - Vector DB path (default: chroma_db/)

### Setting Environment Variables

**Local (.env file):**
```bash
GENAI_API_KEY=your_google_api_key_here
```

**Docker Compose:**
Already configured to read from `.env` file

**Systemd Service:**
Add to `/etc/systemd/system/querio.service`:
```ini
[Service]
Environment="GENAI_API_KEY=your_key"
```

---

## Port Configuration

### Application Ports
- **8000** - FastAPI application (direct access)
- **80** - HTTP (via Nginx)
- **443** - HTTPS (via Nginx, when configured)

### AWS Security Group Requirements
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP | SSH access |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |
| 8000 | TCP | 0.0.0.0/0 | Direct API (optional) |

---

## Data Persistence

### Docker Volumes
Defined in `docker-compose.yml`:
```yaml
volumes:
  - ./data:/app/data           # PDF files
  - ./chroma_db:/app/chroma_db # Vector database
```

### Backup Strategy
```bash
# Backup data
cd ~/querio
tar -czf backup-$(date +%Y%m%d).tar.gz data/ chroma_db/

# Restore data
tar -xzf backup-20250101.tar.gz
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: 3.0.98.108
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd ~/querio
            git pull
            docker-compose up -d --build
```

---

## Troubleshooting

### Common Issues

**Scripts not executable:**
```bash
chmod +x scripts/*.sh
```

**Wrong working directory:**
```bash
# Always run from project root
cd ~/querio
./scripts/deploy.sh
```

**Nginx config not found:**
```bash
# Use correct path
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
```

**Docker permission denied:**
```bash
newgrp docker
# or logout and login again
```

---

## Contributing

When adding new files:

1. **Scripts** → Add to `/scripts` directory
2. **Nginx configs** → Add to `/nginx` directory
3. **Documentation** → Add to `/docs` or root (if major)
4. **Update this file** - Keep PROJECT_STRUCTURE.md current

---

## Additional Resources

- [QUICK_START.md](./QUICK_START.md) - 5-minute deployment
- [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) - Complete guide
- [scripts/README.md](../scripts/README.md) - Script documentation
- [nginx/README.md](../nginx/README.md) - Nginx documentation

---

**Last Updated:** 2025-12-10
**Project:** Querio RAG API
**Repository:** https://github.com/paradocx96/querio-api
