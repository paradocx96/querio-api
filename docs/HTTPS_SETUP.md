# HTTPS Setup Guide for EC2

Complete guide to enable HTTPS/SSL for your Querio API on AWS EC2.

## Prerequisites

- EC2 instance running with Querio deployed
- A domain name (or use EC2 public DNS)
- Nginx configured and running

---

## Option 1: Using Let's Encrypt with Custom Domain (Recommended)

### Requirements
- Own domain name (e.g., yourdomain.com)
- Domain DNS pointed to EC2 IP: 13.213.3.90

---

### Step 1: Point Your Domain to EC2

In your domain registrar's DNS settings, add an A record:

```
Type: A
Name: api (or @ for root domain)
Value: 13.213.3.90
TTL: 3600
```

Examples:
- `api.yourdomain.com` → Points to your API
- `yourdomain.com` → Root domain points to API

**Wait 5-30 minutes for DNS propagation**

Test DNS:
```bash
# From your computer
nslookup api.yourdomain.com
# Should return: 13.213.3.90
```

---

### Step 2: Update Nginx Configuration

SSH into your EC2:
```bash
ssh -i your-key.pem ubuntu@13.213.3.90
cd ~/querio
```

Edit nginx config:
```bash
sudo nano /etc/nginx/sites-available/querio
```

Update the `server_name` line:
```nginx
server_name api.yourdomain.com;  # Replace with your actual domain
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### Step 3: Install Certbot

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

---

### Step 4: Obtain SSL Certificate

```bash
# Get certificate (replace with your domain)
sudo certbot --nginx -d api.yourdomain.com
```

You'll be asked:
1. **Email address**: Enter your email (for renewal notifications)
2. **Terms of Service**: Type 'Y' to agree
3. **Share email**: Type 'N' (optional)
4. **Redirect HTTP to HTTPS**: Type '2' (recommended)

Certbot will:
- Obtain SSL certificate
- Automatically configure nginx
- Set up auto-renewal

---

### Step 5: Verify HTTPS

Test your API:
```bash
# From your computer
curl https://api.yourdomain.com/api/health
```

Visit in browser:
```
https://api.yourdomain.com/docs
```

You should see a padlock icon 🔒 in the browser!

---

### Step 6: Test Auto-Renewal

Certbot automatically sets up renewal. Test it:
```bash
# Dry run renewal
sudo certbot renew --dry-run
```

If successful, your certificate will auto-renew every 90 days.

---

## Option 2: Using Let's Encrypt with EC2 Public DNS

**Note**: Let's Encrypt has limitations with EC2 DNS names. This may not work reliably.

### Try This:

```bash
sudo certbot --nginx -d ec2-13-213-3-90.ap-southeast-1.compute.amazonaws.com
```

**Issues**:
- EC2 DNS changes if you stop/start instance
- Let's Encrypt may have rate limits on AWS domains
- Not recommended for production

**Alternative**: Get an Elastic IP (free while instance is running) for a permanent IP.

---

## Option 3: Self-Signed Certificate (Development Only)

For testing without a domain. **Not recommended for production** (browsers show warnings).

### Generate Self-Signed Certificate

```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate certificate (valid for 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/querio.key \
  -out /etc/nginx/ssl/querio.crt
```

You'll be asked for:
- Country: SG
- State: Singapore
- City: Singapore
- Organization: Your Company
- Common Name: 13.213.3.90
- Email: your@email.com

### Update Nginx for Self-Signed Certificate

Edit nginx config:
```bash
sudo nano /etc/nginx/sites-available/querio
```

Add HTTPS server block:
```nginx
server {
    listen 443 ssl http2;
    server_name 13.213.3.90;

    ssl_certificate /etc/nginx/ssl/querio.crt;
    ssl_certificate_key /etc/nginx/ssl/querio.key;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    access_log /var/log/nginx/querio_access.log;
    error_log /var/log/nginx/querio_error.log;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name 13.213.3.90;
    return 301 https://$server_name$request_uri;
}
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Access:
```
https://13.213.3.90/docs
```

**Note**: Browser will show "Not Secure" warning. Click "Advanced" → "Proceed".

---

## Option 4: AWS Certificate Manager + Load Balancer

For production with high traffic. **Costs extra** (~$20-30/month for load balancer).

### Steps:
1. Request certificate in AWS Certificate Manager (ACM)
2. Create Application Load Balancer (ALB)
3. Configure ALB with ACM certificate
4. Point ALB to EC2 instance

**Not recommended for free tier** - use Option 1 instead.

---

## Recommended HTTPS Setup (Updated Nginx Config)

I'll create an optimized nginx configuration that works with Let's Encrypt:

```nginx
# HTTP server - redirects to HTTPS after SSL setup
server {
    listen 80;
    server_name api.yourdomain.com;  # Replace with your domain

    # Allow Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;  # Replace with your domain

    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase body size for PDF uploads
    client_max_body_size 50M;

    # API proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /api/health {
        proxy_pass http://localhost:8000/api/health;
        access_log off;
    }

    # Logs
    access_log /var/log/nginx/querio_access.log;
    error_log /var/log/nginx/querio_error.log;
}
```

**Note**: After running Certbot, it will automatically update these paths.

---

## SSL Configuration Files

### Current Setup (Before SSL)
Your current nginx config works with HTTP:
- http://13.213.3.90/docs

### After SSL Setup (With Domain)
Your API will be accessible via:
- https://api.yourdomain.com/docs
- http://api.yourdomain.com/docs (redirects to HTTPS)

---

## Testing Your SSL Setup

### 1. Check Certificate

```bash
# From EC2
sudo certbot certificates

# Check expiration
echo | openssl s_client -servername api.yourdomain.com -connect api.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 2. Test SSL Grade

Visit: https://www.ssllabs.com/ssltest/
Enter your domain: `api.yourdomain.com`

Should get A or A+ rating!

### 3. Test API Endpoints

```bash
# Health check
curl https://api.yourdomain.com/api/health

# Upload document
curl -X POST "https://api.yourdomain.com/api/documents/upload" \
  -F "file=@test.pdf"

# Query
curl -X POST "https://api.yourdomain.com/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 3}'
```

---

## Automatic Certificate Renewal

### How It Works

Certbot installs a cron job or systemd timer:
```bash
# Check renewal timer
sudo systemctl status certbot.timer

# View cron job (alternative)
sudo crontab -l
```

### Manual Renewal

```bash
# Renew all certificates
sudo certbot renew

# Renew specific domain
sudo certbot renew --cert-name api.yourdomain.com

# Renew and reload nginx
sudo certbot renew --deploy-hook "systemctl reload nginx"
```

### Renewal Logs

```bash
# View renewal logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## Troubleshooting

### Issue 1: Certbot Fails - Port 80 Not Accessible

**Error**: `Timeout during connect`

**Solution**: Check EC2 Security Group allows port 80 from 0.0.0.0/0

```bash
# Verify port 80 is open
sudo netstat -tlnp | grep :80
```

### Issue 2: DNS Not Resolving

**Error**: `DNS problem: NXDOMAIN`

**Solution**: Wait longer for DNS propagation (up to 48 hours)

```bash
# Test DNS
dig api.yourdomain.com
nslookup api.yourdomain.com
```

### Issue 3: Certificate Already Exists

**Error**: `Certificate already exists`

**Solution**: Use force renewal
```bash
sudo certbot --nginx -d api.yourdomain.com --force-renewal
```

### Issue 4: Nginx Config Test Fails

**Error**: `nginx: configuration file test failed`

**Solution**: Check syntax
```bash
sudo nginx -t
# Fix errors shown, usually missing semicolon or bracket
```

### Issue 5: Mixed Content Warnings

**Problem**: Some resources load over HTTP on HTTPS page

**Solution**: Update your application to use HTTPS URLs, or use relative URLs

---

## Security Best Practices

### 1. Update SSL Configuration Regularly

```bash
# Update Certbot
sudo apt-get update
sudo apt-get upgrade certbot python3-certbot-nginx
```

### 2. Enable HSTS

Already included in recommended config:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 3. Disable TLS 1.0 and 1.1

Already configured (Certbot defaults to TLS 1.2+)

### 4. Monitor Certificate Expiration

Set up monitoring:
```bash
# Create check script
cat > ~/check-ssl.sh << 'EOF'
#!/bin/bash
EXPIRY=$(echo | openssl s_client -servername api.yourdomain.com -connect api.yourdomain.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
echo "Certificate expires: $EXPIRY"
EOF

chmod +x ~/check-ssl.sh
```

### 5. Regular Security Audits

- Use SSL Labs: https://www.ssllabs.com/ssltest/
- Check for vulnerabilities: https://securityheaders.com/
- Update nginx regularly: `sudo apt-get update && sudo apt-get upgrade nginx`

---

## Cost Summary

| Option | Cost | Recommendation |
|--------|------|----------------|
| Let's Encrypt + Domain | $10-15/year (domain only) | ✅ Best |
| Let's Encrypt + EC2 DNS | Free (unreliable) | ⚠️ Not recommended |
| Self-Signed | Free | 🚫 Development only |
| AWS ACM + ALB | ~$20-30/month | 💰 Overkill for small projects |

---

## Quick Command Reference

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Renew certificates
sudo certbot renew

# Check certificates
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Revoke certificate
sudo certbot revoke --cert-path /etc/letsencrypt/live/api.yourdomain.com/cert.pem

# Delete certificate
sudo certbot delete --cert-name api.yourdomain.com
```

---

## My Recommendation for You

Since you have EC2 IP: **13.213.3.90**

### Best Option:
1. **Get a cheap domain** ($10-15/year from Namecheap)
2. Point it to your EC2 IP
3. Use Let's Encrypt (free SSL)
4. Total cost: ~$1/month

### Example Domains:
- api.yourname.com
- querio.yourname.com
- myapi.dev (trendy TLD)

### Quick Setup:
1. Buy domain on Namecheap
2. Add A record: `@` → `13.213.3.90`
3. Wait 5-30 minutes
4. Run: `sudo certbot --nginx -d yourdomain.com`
5. Done! 🔒

---

## Need Help?

- Let's Encrypt Docs: https://letsencrypt.org/docs/
- Certbot Docs: https://certbot.eff.org/
- Nginx SSL Guide: https://nginx.org/en/docs/http/configuring_https_servers.html

---

**Ready to enable HTTPS? Follow Option 1 with a domain for the best experience!**
