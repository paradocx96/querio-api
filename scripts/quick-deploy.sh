#!/bin/bash

# Querio API - Quick Deploy Script
# One-command deployment for AWS EC2

set -e

echo ""
echo "================================================"
echo "  Querio API - Quick Deploy"
echo "================================================"
echo ""

# Check if setup is done
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Installing dependencies..."
    curl -sO https://raw.githubusercontent.com/paradocx96/querio-api/main/scripts/setup-ec2.sh
    chmod +x setup-ec2.sh
    ./setup-ec2.sh
    echo ""
    echo "Please run 'newgrp docker' or log out and log back in"
    echo "Then run this script again: ./scripts/quick-deploy.sh"
    exit 0
fi

# Clone or update repository
if [ -d "$HOME/querio" ]; then
    echo "Updating existing installation..."
    cd "$HOME/querio"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/paradocx96/querio-api.git "$HOME/querio"
    cd "$HOME/querio"
fi

# Configure environment
if [ ! -f ".env" ]; then
    echo ""
    echo "Enter your Google AI API Key:"
    read -r -p "GENAI_API_KEY: " GENAI_KEY
    echo "GENAI_API_KEY=$GENAI_KEY" > .env
fi

# Deploy
echo ""
echo "Deploying application..."
docker-compose up -d --build

# Setup Nginx
if command -v nginx &> /dev/null; then
    echo ""
    read -p "Setup Nginx? (y/n): " -r SETUP
    if [ "$SETUP" = "y" ]; then
        sudo cp nginx/nginx-querio.conf /etc/nginx/sites-available/querio
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo ln -sf /etc/nginx/sites-available/querio /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl restart nginx
        echo "✓ Nginx configured"
    fi
fi

# Get IP
IP=$(curl -s http://checkip.amazonaws.com)

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "Access your API at:"
echo "  http://$IP/docs"
echo ""
