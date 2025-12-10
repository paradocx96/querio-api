# Deployment Files Summary

All deployment files and scripts for AWS EC2 deployment.

## 📋 Files Created

### Deployment Scripts

1. **setup-ec2.sh**
   - Installs all dependencies (Docker, Docker Compose, Git, Nginx)
   - Run once on new EC2 instance
   - Usage: `./setup-ec2.sh`

2. **deploy.sh** ⭐ (Recommended)
   - Complete automated deployment
   - Interactive prompts for configuration
   - Includes nginx and HTTPS setup
   - Usage: `./deploy.sh`

3. **quick-deploy.sh**
   - Minimal deployment script
   - Quick setup with fewer prompts
   - Usage: `./quick-deploy.sh`

4. **setup-https.sh**
   - Automated HTTPS/SSL setup with Let's Encrypt
   - Requires domain name
   - Usage: `./setup-https.sh`

### Configuration Files

5. **docker-compose.yml**
   - Docker Compose configuration
   - Container orchestration
   - Volume management

6. **Dockerfile**
   - Container image definition
   - Application packaging

7. **.dockerignore**
   - Excludes unnecessary files from Docker build
   - Optimizes build size and speed

8. **nginx/nginx-querio.conf**
   - Unified Nginx reverse proxy configuration
   - HTTP configuration (active by default)
   - HTTPS configuration (commented, ready to enable)
   - Configured for IP: 3.0.98.108
   - Security headers included
   - Let's Encrypt ACME challenge support

9. **querio.service**
    - Systemd service file
    - Auto-start on reboot
    - Service management

### Documentation

10. **AWS_EC2_DEPLOYMENT.md**
    - Complete step-by-step deployment guide
    - Manual deployment instructions
    - Troubleshooting section

11. **HTTPS_SETUP.md**
    - SSL/HTTPS configuration guide
    - Let's Encrypt setup
    - Certificate management

12. **DEPLOYMENT.md**
    - Railway.app deployment guide
    - Alternative deployment option

13. **QUICK_START.md** ⭐
    - Quick reference guide
    - One-command deployment
    - Common commands

14. **DEPLOYMENT_SUMMARY.md** (this file)
    - Overview of all deployment files
    - Quick reference

---

## 🚀 Quick Deploy Guide

### Option 1: One-Command Deploy (Easiest)

SSH to your EC2 and run:

```bash
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Steps

```bash
# 1. Setup dependencies
./setup-ec2.sh
newgrp docker

# 2. Clone repository
git clone https://github.com/paradocx96/querio-api.git
cd querio-api

# 3. Configure
echo "GENAI_API_KEY=your_key" > .env
mkdir -p data chroma_db

# 4. Deploy
docker-compose up -d --build

# 5. Setup Nginx
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### Option 3: With HTTPS

After deploying:
```bash
./setup-https.sh
# Enter your domain when prompted
```

---

## 📊 File Usage Matrix

| File | Required | When to Use |
|------|----------|-------------|
| setup-ec2.sh | Yes | First time setup |
| deploy.sh | Recommended | Full deployment |
| docker-compose.yml | Yes | Container management |
| Dockerfile | Yes | Image building |
| nginx/nginx-querio.conf | Optional | Production setup |
| querio.service | Optional | Auto-start |
| setup-https.sh | Optional | When you have domain |

---

## 🌐 Your Current Configuration

### Server Details
- **IP Address**: 3.0.98.108
- **Region**: ap-southeast-1 (Singapore)
- **Instance**: t2.micro
- **OS**: Ubuntu 22.04 LTS

### Nginx Configuration
- **File**: nginx/nginx-querio.conf
- **Server Name**: 3.0.98.108
- **Type**: Unified HTTP/HTTPS (HTTPS commented out)
- **Configured**: ✅ Yes

### Current Access URLs
- **With Nginx**: http://3.0.98.108/docs
- **Direct**: http://3.0.98.108:8000/docs

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] EC2 instance launched (t2.micro)
- [ ] Security group configured (ports 22, 80, 443, 8000)
- [ ] SSH key downloaded
- [ ] Google AI API key obtained

### Initial Setup
- [ ] Connected to EC2 via SSH
- [ ] Run setup-ec2.sh
- [ ] Docker permissions applied (newgrp docker)

### Application Deployment
- [ ] Repository cloned
- [ ] .env file created with API key
- [ ] Directories created (data, chroma_db)
- [ ] Docker containers deployed
- [ ] Health check passed

### Nginx Setup (Optional)
- [ ] Nginx configured
- [ ] Configuration tested
- [ ] Nginx restarted
- [ ] Accessible on port 80

### HTTPS Setup (Optional)
- [ ] Domain purchased
- [ ] DNS configured (A record)
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Auto-renewal configured

### Post-Deployment
- [ ] API tested
- [ ] Documentation accessible
- [ ] Test PDF uploaded
- [ ] Systemd service enabled (optional)
- [ ] Backup strategy planned

---

## 🔧 Common Commands Reference

### Docker Commands
```bash
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

# View stats
docker stats
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload (without downtime)
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# Status
sudo systemctl status nginx

# View access logs
sudo tail -f /var/log/nginx/querio_access.log

# View error logs
sudo tail -f /var/log/nginx/querio_error.log
```

### System Commands
```bash
# Check memory
free -h

# Check disk space
df -h

# Check processes
htop

# View systemd service
sudo systemctl status querio

# Check open ports
sudo netstat -tlnp

# Check system logs
sudo journalctl -xe
```

### Update Application
```bash
cd ~/querio
git pull
docker-compose up -d --build
```

---

## 🔒 Security Recommendations

### Immediate
1. ✅ Configure EC2 Security Group properly
2. ✅ Use strong API keys
3. ✅ Don't commit .env file

### After Deployment
4. [ ] Setup HTTPS with Let's Encrypt
5. [ ] Enable UFW firewall
6. [ ] Setup fail2ban for SSH protection
7. [ ] Configure automated backups

### Ongoing
8. [ ] Monitor logs regularly
9. [ ] Keep system updated
10. [ ] Review access logs
11. [ ] Rotate API keys periodically

---

## 💰 Cost Tracking

### AWS Free Tier (12 months)
- EC2 t2.micro: 750 hours/month (FREE)
- Storage: 30GB EBS (FREE)
- Data Transfer: 15GB/month (FREE)

### After Free Tier
- EC2 t2.micro: ~$8/month
- Storage (20GB): ~$2/month
- Data Transfer: First 1GB free, then $0.09/GB

### Optional Costs
- Domain name: $10-15/year (~$1/month)
- SSL certificate: FREE (Let's Encrypt)
- Elastic IP: FREE (while instance running)

**Total estimated cost after free tier: $8-10/month**

---

## 🆘 Troubleshooting Quick Reference

### Can't SSH to EC2
- Check security group allows port 22 from your IP
- Verify key permissions: `chmod 400 your-key.pem`
- Check instance is running

### Docker build fails
- Add swap space (see AWS_EC2_DEPLOYMENT.md)
- Check available memory: `free -h`
- Try: `docker-compose build --no-cache`

### API not responding
- Check container: `docker-compose ps`
- View logs: `docker-compose logs`
- Test locally: `curl http://localhost:8000/api/health`
- Check port: `sudo netstat -tlnp | grep 8000`

### Nginx errors
- Test config: `sudo nginx -t`
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Verify file: `ls -la /etc/nginx/sites-enabled/`

### HTTPS issues
- Verify DNS: `dig your-domain.com`
- Check certbot: `sudo certbot certificates`
- Test renewal: `sudo certbot renew --dry-run`

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) | Complete EC2 deployment guide |
| [HTTPS_SETUP.md](./HTTPS_SETUP.md) | SSL/HTTPS configuration |
| [QUICK_START.md](QUICK_START.md) | Quick deploy reference |
| [README.md](./README.md) | Project overview |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API endpoints |

---

## 🎯 Next Steps After Deployment

1. **Test Your API**
   - Visit http://3.0.98.108/docs
   - Upload a test PDF
   - Try the query endpoint

2. **Setup HTTPS** (if you have a domain)
   - Run `./setup-https.sh`
   - Follow the prompts

3. **Configure Monitoring**
   - Setup CloudWatch (AWS)
   - Configure log rotation
   - Setup alerting

4. **Backup Strategy**
   - Backup data and chroma_db directories
   - Setup automated backups
   - Test restore procedure

5. **Optimize**
   - Monitor memory usage
   - Adjust Docker limits if needed
   - Consider t2.small if t2.micro is insufficient

---

## 🔄 Update Process

When you make changes and need to redeploy:

```bash
# 1. Push changes to GitHub
git add .
git commit -m "Your changes"
git push

# 2. On EC2, pull and rebuild
ssh -i your-key.pem ubuntu@3.0.98.108
cd ~/querio
git pull
docker-compose up -d --build

# 3. Verify
curl http://localhost/api/health
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/paradocx96/querio-api/issues
- **Documentation**: Check the docs/ folder
- **API Docs**: http://your-ip/docs

---

**Ready to deploy?**

```bash
ssh -i your-key.pem ubuntu@3.0.98.108
curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

That's it! 🚀
