#!/bin/bash

# Querio HTTPS Setup Script
# Automates SSL certificate installation with Let's Encrypt

set -e

echo "================================================"
echo "Querio API - HTTPS Setup with Let's Encrypt"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Please do not run this script as root"
    echo "Run without sudo: ./setup-https.sh"
    exit 1
fi

# Prompt for domain name
echo "Enter your domain name (e.g., api.yourdomain.com):"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "ERROR: Domain name cannot be empty"
    exit 1
fi

echo ""
echo "Domain: $DOMAIN"
echo ""

# Confirm DNS is pointing to this server
echo "Before proceeding, make sure:"
echo "1. Your domain DNS A record points to this server's IP"
echo "2. Port 80 and 443 are open in your EC2 Security Group"
echo ""
read -p "Have you done this? (yes/no): " -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Please configure DNS and security group first, then run this script again."
    exit 1
fi

# Test DNS resolution
echo ""
echo "Testing DNS resolution..."
if host "$DOMAIN" > /dev/null 2>&1; then
    RESOLVED_IP=$(host "$DOMAIN" | grep "has address" | awk '{print $4}' | head -1)
    echo "✓ Domain resolves to: $RESOLVED_IP"
else
    echo "✗ DNS resolution failed!"
    echo "Please wait for DNS propagation and try again."
    exit 1
fi

# Install Certbot if not already installed
echo ""
echo "Checking for Certbot..."
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    echo "✓ Certbot installed"
else
    echo "✓ Certbot is already installed"
fi

# Update nginx configuration with domain
echo ""
echo "Updating nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/querio"

if [ -f "$NGINX_CONF" ]; then
    # Backup current config
    sudo cp "$NGINX_CONF" "$NGINX_CONF.backup-$(date +%Y%m%d-%H%M%S)"

    # Update server_name
    sudo sed -i "s/server_name .*/server_name $DOMAIN;/" "$NGINX_CONF"

    echo "✓ Nginx configuration updated"
else
    echo "✗ Nginx configuration not found at $NGINX_CONF"
    exit 1
fi

# Test nginx configuration
echo ""
echo "Testing nginx configuration..."
if sudo nginx -t; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration test failed"
    exit 1
fi

# Reload nginx
echo ""
echo "Reloading nginx..."
sudo systemctl reload nginx
echo "✓ Nginx reloaded"

# Obtain SSL certificate
echo ""
echo "================================================"
echo "Obtaining SSL certificate from Let's Encrypt..."
echo "================================================"
echo ""
echo "You will be asked for:"
echo "1. Email address (for renewal notifications)"
echo "2. Agree to Terms of Service"
echo "3. Whether to redirect HTTP to HTTPS (choose Yes)"
echo ""
read -p "Press Enter to continue..."

sudo certbot --nginx -d "$DOMAIN"

# Check if certificate was obtained
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo ""
    echo "================================================"
    echo "✓ SSL Certificate Successfully Installed!"
    echo "================================================"
    echo ""
    echo "Your API is now accessible via HTTPS:"
    echo "  https://$DOMAIN/docs"
    echo "  https://$DOMAIN/api/health"
    echo ""
    echo "Certificate details:"
    sudo certbot certificates -d "$DOMAIN"
    echo ""
    echo "Auto-renewal is configured. Check status with:"
    echo "  sudo systemctl status certbot.timer"
    echo ""
    echo "Test renewal with:"
    echo "  sudo certbot renew --dry-run"
    echo ""
else
    echo ""
    echo "✗ Certificate installation failed"
    echo "Check the errors above and try again"
    exit 1
fi

# Test HTTPS
echo "Testing HTTPS connection..."
if curl -sSf "https://$DOMAIN/api/health" > /dev/null 2>&1; then
    echo "✓ HTTPS is working correctly!"
else
    echo "⚠ HTTPS test failed, but certificate may still be installed"
    echo "Try accessing https://$DOMAIN/docs in your browser"
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Visit https://$DOMAIN/docs to test your API"
echo "2. Update your frontend/apps to use HTTPS URLs"
echo "3. Monitor certificate renewal logs"
echo ""
echo "Certificate will auto-renew before expiration."
echo ""
