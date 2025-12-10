# Nginx Configuration

This directory contains the Nginx reverse proxy configuration for the Querio API.

## Configuration File

### nginx-querio.conf
**Purpose**: Unified production configuration (HTTP + HTTPS ready)

**Features:**
- **HTTP Support**: Works out of the box with IP address (13.213.3.90)
- **HTTPS Ready**: Commented sections for SSL/HTTPS (enable when needed)
- **Reverse Proxy**: Forwards requests to FastAPI on port 8000
- **Large File Uploads**: Supports up to 50MB (configurable)
- **Health Check Endpoint**: Optimized `/api/health` endpoint
- **Long Timeouts**: 300s for LLM processing
- **WebSocket Support**: Ready for real-time features
- **Security Headers**: HSTS, X-Frame-Options, etc. (in HTTPS mode)
- **Let's Encrypt Ready**: ACME challenge support built-in

**Initial Setup (HTTP):**
```bash
# Copy to nginx sites-available
sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio

# Enable site
sudo ln -s /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

**Access:** http://13.213.3.90/

**Upgrade to HTTPS (with domain):**
```bash
# Option 1: Let Certbot auto-configure (Recommended)
sudo certbot --nginx -d your-domain.com

# Option 2: Manually uncomment HTTPS sections
sudo nano /etc/nginx/sites-available/querio
# Uncomment HTTPS server blocks and update domain
sudo nginx -t && sudo systemctl reload nginx
```

**Access:** https://your-domain.com/

---

## Configuration Details

### Server Name
Current configuration uses:
```nginx
server_name 13.213.3.90;
```

**To use a custom domain:**
1. Update `server_name` to your domain
2. Point DNS A record to 13.213.3.90
3. Run `./scripts/setup-https.sh` for SSL

### Upload Size
Maximum file size is set to 50MB:
```nginx
client_max_body_size 50M;
```

**To increase:**
```nginx
client_max_body_size 100M;  # For 100MB files
```

### Timeouts
Long timeouts for LLM processing:
```nginx
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

**Adjust based on your needs:**
- Shorter for faster responses
- Longer for heavy document processing

### Logging
Logs are written to:
- Access: `/var/log/nginx/querio_access.log`
- Errors: `/var/log/nginx/querio_error.log`

**View logs:**
```bash
# Access logs
sudo tail -f /var/log/nginx/querio_access.log

# Error logs
sudo tail -f /var/log/nginx/querio_error.log

# Combined
sudo tail -f /var/log/nginx/querio_*.log
```

---

## Common Nginx Commands

### Testing
```bash
# Test configuration
sudo nginx -t

# Test and show configuration file
sudo nginx -T
```

### Service Management
```bash
# Start
sudo systemctl start nginx

# Stop
sudo systemctl stop nginx

# Restart
sudo systemctl restart nginx

# Reload (no downtime)
sudo systemctl reload nginx

# Status
sudo systemctl status nginx
```

### Configuration
```bash
# Edit configuration
sudo nano /etc/nginx/sites-available/querio

# List enabled sites
ls -la /etc/nginx/sites-enabled/

# Show config
cat /etc/nginx/sites-available/querio
```

---

## Enabling HTTPS

The configuration file has both HTTP and HTTPS sections. HTTPS sections are commented out by default.

### Method 1: Automatic (Recommended)

Let Certbot automatically configure HTTPS:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate and auto-configure
sudo certbot --nginx -d your-domain.com

# Certbot will:
# - Obtain SSL certificate
# - Modify nginx config
# - Enable HTTPS
# - Setup auto-renewal
```

### Method 2: Manual

```bash
# 1. Update server_name to your domain
sudo nano /etc/nginx/sites-available/querio
# Change line 3: server_name your-domain.com;

# 2. Get certificate with Certbot
sudo certbot certonly --nginx -d your-domain.com

# 3. Uncomment HTTPS sections in config
# Find the "# HTTPS Server Block" section
# Remove # from all lines in that section

# 4. Update domain in HTTPS section
# Change: server_name your-domain.com;

# 5. Uncomment HTTP redirect section
# Remove # from "# HTTP to HTTPS Redirect" section

# 6. Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Disabling HTTPS (Reverting to HTTP)

```bash
# 1. Re-comment HTTPS sections
sudo nano /etc/nginx/sites-available/querio
# Add # back to HTTPS sections

# 2. Test and reload
sudo nginx -t
sudo systemctl reload nginx

# 3. Optionally revoke certificate
sudo certbot revoke --cert-path /etc/letsencrypt/live/your-domain.com/cert.pem
```

---

## Customization Examples

### Add Rate Limiting

```nginx
# At the top of nginx config
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# In location block
location /api/ {
    limit_req zone=api_limit burst=20;
    proxy_pass http://localhost:8000;
    # ... other proxy settings
}
```

### Add IP Whitelist

```nginx
# In server block
location / {
    allow 203.0.113.0/24;  # Your office IP range
    deny all;

    proxy_pass http://localhost:8000;
    # ... other proxy settings
}
```

### Add Basic Authentication

```bash
# Create password file
sudo apt-get install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin

# In nginx config
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://localhost:8000;
    # ... other proxy settings
}
```

### Custom Error Pages

```nginx
# In server block
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;

location = /404.html {
    root /usr/share/nginx/html;
}

location = /50x.html {
    root /usr/share/nginx/html;
}
```

---

## Security Hardening

### Recommended Headers (Already in HTTPS config)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Hide Nginx Version

```nginx
# In /etc/nginx/nginx.conf
http {
    server_tokens off;
    # ...
}
```

### SSL Best Practices

```nginx
# Strong SSL protocols
ssl_protocols TLSv1.2 TLSv1.3;

# Strong ciphers
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

# Perfect forward secrecy
ssl_prefer_server_ciphers off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
```

---

## Troubleshooting

### 502 Bad Gateway
**Cause:** FastAPI container not running or not accessible

**Fix:**
```bash
# Check if container is running
docker-compose ps

# Check if app responds
curl http://localhost:8000/api/health

# Restart container
cd ~/querio
docker-compose restart
```

### 413 Request Entity Too Large
**Cause:** File upload exceeds `client_max_body_size`

**Fix:**
```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/querio

# Increase size
client_max_body_size 100M;

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx
```

### Configuration Test Failed
**Cause:** Syntax error in nginx config

**Fix:**
```bash
# See detailed error
sudo nginx -t

# Common issues:
# - Missing semicolon
# - Mismatched braces {}
# - Invalid directive
```

### SSL Certificate Errors
**Cause:** Certificate not found or expired

**Fix:**
```bash
# Check certificates
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## Performance Tuning

### Enable Gzip Compression

```nginx
# In server block
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Enable Caching

```nginx
# Cache static files (if you serve any)
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Connection Pooling

```nginx
# In http block
keepalive_timeout 65;
keepalive_requests 100;
```

---

## Monitoring

### Real-time Log Monitoring

```bash
# Watch all requests
sudo tail -f /var/log/nginx/querio_access.log | grep -v "health"

# Watch errors only
sudo tail -f /var/log/nginx/querio_error.log

# Watch specific IP
sudo tail -f /var/log/nginx/querio_access.log | grep "203.0.113.1"
```

### Log Analysis

```bash
# Top 10 IPs
sudo awk '{print $1}' /var/log/nginx/querio_access.log | sort | uniq -c | sort -rn | head -10

# Status code distribution
sudo awk '{print $9}' /var/log/nginx/querio_access.log | sort | uniq -c | sort -rn

# Most accessed endpoints
sudo awk '{print $7}' /var/log/nginx/querio_access.log | sort | uniq -c | sort -rn | head -10
```

---

## Additional Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Best Practices](https://www.nginx.com/blog/nginx-best-practices-performance/)
- [SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Test](https://www.ssllabs.com/ssltest/)

---

**For deployment guides, see:**
- [../QUICK_START.md](../QUICK_START.md)
- [../AWS_EC2_DEPLOYMENT.md](../AWS_EC2_DEPLOYMENT.md)
- [../HTTPS_SETUP.md](../HTTPS_SETUP.md)
