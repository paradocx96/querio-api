#!/bin/bash

# Querio API - Complete Deployment Script
# Automates deployment on AWS EC2 or any Ubuntu server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/paradocx96/querio-api.git"
PROJECT_DIR="$HOME/querio-api"
NGINX_CONF="/etc/nginx/sites-available/querio-api"

echo ""
echo "================================================"
echo "  Querio RAG API - Deployment Script"
echo "================================================"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    echo "Run without sudo: ./deploy.sh"
    exit 1
fi

# Step 1: Check Prerequisites
echo ""
echo "Step 1/6: Checking prerequisites..."
echo "-----------------------------------"

MISSING_DEPS=0

if command_exists docker; then
    print_success "Docker is installed"
else
    print_error "Docker is not installed"
    MISSING_DEPS=1
fi

if command_exists docker-compose; then
    print_success "Docker Compose is installed"
else
    print_error "Docker Compose is not installed"
    MISSING_DEPS=1
fi

if command_exists git; then
    print_success "Git is installed"
else
    print_error "Git is not installed"
    MISSING_DEPS=1
fi

if command_exists nginx; then
    print_success "Nginx is installed"
else
    print_warning "Nginx is not installed (optional)"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    print_error "Missing required dependencies!"
    echo ""
    echo "Please run the setup script first:"
    echo "  curl -O https://raw.githubusercontent.com/paradocx96/querio-api/main/setup-ec2.sh"
    echo "  chmod +x setup-ec2.sh"
    echo "  ./setup-ec2.sh"
    echo "  newgrp docker"
    exit 1
fi

# Step 2: Clone Repository
echo ""
echo "Step 2/6: Cloning repository..."
echo "-------------------------------"

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists"
    read -p "Do you want to remove it and clone fresh? (yes/no): " -r CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        echo "Backing up existing directory..."
        mv "$PROJECT_DIR" "${PROJECT_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
        print_success "Backup created"
    else
        print_info "Using existing directory"
        cd "$PROJECT_DIR"
        echo "Pulling latest changes..."
        git pull origin main || print_warning "Could not pull latest changes"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Cloning repository from $REPO_URL..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    print_success "Repository cloned"
fi

cd "$PROJECT_DIR"

# Step 3: Configure Environment
echo ""
echo "Step 3/6: Configuring environment..."
echo "------------------------------------"

if [ -f ".env" ]; then
    print_warning ".env file already exists"
    read -p "Do you want to update it? (yes/no): " -r UPDATE_ENV
    if [ "$UPDATE_ENV" != "yes" ]; then
        print_info "Keeping existing .env file"
    else
        mv .env .env.backup-$(date +%Y%m%d-%H%M%S)
        print_info "Backed up existing .env file"
        UPDATE_ENV="yes"
    fi
else
    UPDATE_ENV="yes"
fi

if [ "$UPDATE_ENV" = "yes" ]; then
    echo ""
    echo "Please enter your Google AI API key:"
    echo "(Get it from: https://makersuite.google.com/app/apikey)"
    read -r -p "GENAI_API_KEY: " GENAI_KEY

    if [ -z "$GENAI_KEY" ]; then
        print_error "API key cannot be empty"
        exit 1
    fi

    echo "GENAI_API_KEY=$GENAI_KEY" > .env
    print_success ".env file created"
fi

# Step 4: Deploy Application
echo ""
echo "Step 4/6: Deploying application..."
echo "----------------------------------"

echo "Building and starting Docker containers..."
echo "This may take several minutes on first run..."
echo ""

if docker-compose up -d --build; then
    print_success "Application deployed successfully"
else
    print_error "Deployment failed"
    echo ""
    echo "Troubleshooting tips:"
    echo "1. Check if you have enough memory (may need swap space)"
    echo "2. View logs: docker-compose logs"
    echo "3. Check Docker status: docker ps"
    exit 1
fi

# Wait for application to start
echo ""
echo "Waiting for application to start..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_success "Container is running"
else
    print_warning "Container may not be running properly"
    echo "Check status with: docker-compose ps"
    echo "View logs with: docker-compose logs -f"
fi

# Test API
echo ""
echo "Testing API endpoint..."
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "API is responding"
else
    print_warning "API is not responding yet (may need more time to start)"
fi

# Step 5: Setup Nginx
echo ""
echo "Step 5/6: Setting up Nginx..."
echo "------------------------------"

if command_exists nginx; then
    read -p "Do you want to setup Nginx reverse proxy? (yes/no): " -r SETUP_NGINX

    if [ "$SETUP_NGINX" = "yes" ]; then
        echo ""
        echo "Configuring Nginx..."

        # Check if nginx config file exists in project
        if [ -f "nginx/nginx-querio.conf" ]; then
            # Backup existing nginx config if exists
            if [ -f "$NGINX_CONF" ]; then
                sudo cp "$NGINX_CONF" "${NGINX_CONF}.backup-$(date +%Y%m%d-%H%M%S)"
                print_info "Backed up existing Nginx configuration"
            fi

            # Copy nginx configuration
            sudo cp nginx/nginx-querio.conf "$NGINX_CONF"
            print_success "Nginx configuration copied"

            # Remove default site if exists
            if [ -f "/etc/nginx/sites-enabled/default" ]; then
                sudo rm /etc/nginx/sites-enabled/default
                print_info "Removed default Nginx site"
            fi

            # Create symbolic link
            sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/querio-api
            print_success "Nginx site enabled"

            # Test nginx configuration
            echo ""
            echo "Testing Nginx configuration..."
            if sudo nginx -t; then
                print_success "Nginx configuration is valid"

                # Restart nginx
                echo ""
                echo "Restarting Nginx..."
                sudo systemctl restart nginx
                print_success "Nginx restarted"

                # Check nginx status
                if sudo systemctl is-active --quiet nginx; then
                    print_success "Nginx is running"
                else
                    print_error "Nginx failed to start"
                    echo "Check logs with: sudo journalctl -u nginx -n 50"
                fi
            else
                print_error "Nginx configuration test failed"
                echo "Please check the configuration manually"
            fi
        else
            print_error "nginx/nginx-querio.conf not found in project directory"
        fi
    else
        print_info "Skipping Nginx setup"
        echo "You can access the API directly on port 8000"
    fi
else
    print_info "Nginx is not installed, skipping this step"
    echo "You can access the API directly on port 8000"
fi

# Step 6: Setup HTTPS (Optional)
echo ""
echo "Step 6/6: HTTPS Setup (Optional)..."
echo "------------------------------------"

if command_exists nginx && [ "$SETUP_NGINX" = "yes" ]; then
    echo ""
    read -p "Do you want to setup HTTPS with Let's Encrypt? (yes/no): " -r SETUP_HTTPS

    if [ "$SETUP_HTTPS" = "yes" ]; then
        echo ""
        print_info "HTTPS setup requires a domain name"
        read -p "Do you have a domain pointing to this server? (yes/no): " -r HAS_DOMAIN

        if [ "$HAS_DOMAIN" = "yes" ]; then
            if [ -f "./scripts/setup-https.sh" ]; then
                chmod +x scripts/setup-https.sh
                echo ""
                print_info "Starting HTTPS setup..."
                echo ""
                ./scripts/setup-https.sh
            else
                print_warning "scripts/setup-https.sh not found"
                echo ""
                echo "Manual HTTPS setup:"
                echo "1. Install Certbot: sudo apt-get install certbot python3-certbot-nginx"
                echo "2. Run: sudo certbot --nginx -d your-domain.com"
            fi
        else
            print_info "Skipping HTTPS setup"
            echo ""
            echo "To setup HTTPS later:"
            echo "1. Point your domain to this server's IP"
            echo "2. Run: ./scripts/setup-https.sh"
        fi
    else
        print_info "Skipping HTTPS setup"
    fi
fi

# Setup Systemd Service
echo ""
echo "Setting up systemd service..."
echo "------------------------------"

read -p "Do you want to enable auto-start on reboot? (yes/no): " -r SETUP_SYSTEMD

if [ "$SETUP_SYSTEMD" = "yes" ]; then
    if [ -f "querio.service" ]; then
        # Update service file with correct paths
        sed "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" querio.service > /tmp/querio.service
        sed -i "s|User=.*|User=$USER|g" /tmp/querio.service
        sed -i "s|Group=.*|Group=$USER|g" /tmp/querio.service

        sudo cp /tmp/querio.service /etc/systemd/system/querio.service
        sudo systemctl daemon-reload
        sudo systemctl enable querio
        print_success "Systemd service enabled (auto-start on reboot)"

        echo ""
        echo "Service commands:"
        echo "  Start:   sudo systemctl start querio"
        echo "  Stop:    sudo systemctl stop querio"
        echo "  Restart: sudo systemctl restart querio"
        echo "  Status:  sudo systemctl status querio"
    else
        print_warning "querio.service file not found"
    fi
else
    print_info "Skipping systemd service setup"
fi

# Final Summary
echo ""
echo "================================================"
echo "  Deployment Complete! 🎉"
echo "================================================"
echo ""

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com || echo "YOUR_SERVER_IP")

echo "Your Querio API is now running!"
echo ""
echo "Access URLs:"
echo "-----------------------------------"

if [ "$SETUP_NGINX" = "yes" ]; then
    echo "  API Documentation: http://$SERVER_IP/docs"
    echo "  Health Check:      http://$SERVER_IP/api/health"
    echo "  ReDoc:             http://$SERVER_IP/redoc"
else
    echo "  API Documentation: http://$SERVER_IP:8000/docs"
    echo "  Health Check:      http://$SERVER_IP:8000/api/health"
    echo "  ReDoc:             http://$SERVER_IP:8000/redoc"
fi

echo ""
echo "Useful Commands:"
echo "-----------------------------------"
echo "  View logs:         cd $PROJECT_DIR && docker-compose logs -f"
echo "  Restart:           cd $PROJECT_DIR && docker-compose restart"
echo "  Stop:              cd $PROJECT_DIR && docker-compose down"
echo "  Start:             cd $PROJECT_DIR && docker-compose up -d"
echo "  Update:            cd $PROJECT_DIR && git pull && docker-compose up -d --build"
echo ""

if [ "$SETUP_NGINX" = "yes" ]; then
    echo "Nginx Commands:"
    echo "-----------------------------------"
    echo "  Test config:       sudo nginx -t"
    echo "  Reload:            sudo systemctl reload nginx"
    echo "  Restart:           sudo systemctl restart nginx"
    echo "  View logs:         sudo tail -f /var/log/nginx/querio_access.log"
    echo ""
fi

echo "Next Steps:"
echo "-----------------------------------"
echo "1. Test the API: curl http://$SERVER_IP/api/health"
echo "2. Visit the docs in your browser"
echo "3. Upload a PDF document"
echo "4. Start querying your documents!"
echo ""

if [ "$SETUP_HTTPS" != "yes" ]; then
    echo "Optional:"
    echo "- Setup HTTPS: ./scripts/setup-https.sh (requires domain)"
    echo ""
fi

echo "For detailed documentation, see:"
echo "  - AWS_EC2_DEPLOYMENT.md"
echo "  - HTTPS_SETUP.md"
echo "  - README.md"
echo ""
echo "================================================"
echo ""

# Test the deployment
echo "Running final health check..."
sleep 3

if [ "$SETUP_NGINX" = "yes" ]; then
    TEST_URL="http://localhost/api/health"
else
    TEST_URL="http://localhost:8000/api/health"
fi

if curl -sf "$TEST_URL" > /dev/null 2>&1; then
    print_success "Health check passed - API is ready!"
else
    print_warning "Health check failed - API may still be starting"
    echo "Wait a minute and try: curl $TEST_URL"
fi

echo ""
print_success "Deployment script completed!"
echo ""
