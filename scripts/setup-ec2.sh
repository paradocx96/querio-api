#!/bin/bash

# Querio EC2 Setup Script
# This script sets up the EC2 instance with all required dependencies

set -e

echo "================================================"
echo "Querio RAG API - EC2 Setup Script"
echo "================================================"
echo ""

# Update system
echo "Step 1/6: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo ""
echo "Step 2/6: Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add current user to docker group
    sudo usermod -aG docker $USER

    echo "Docker installed successfully!"
else
    echo "Docker is already installed."
fi

# Install Docker Compose (standalone)
echo ""
echo "Step 3/6: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully!"
else
    echo "Docker Compose is already installed."
fi

# Install Git
echo ""
echo "Step 4/6: Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
    echo "Git installed successfully!"
else
    echo "Git is already installed."
fi

# Install other utilities
echo ""
echo "Step 5/6: Installing utilities (curl, htop, etc.)..."
sudo apt-get install -y curl htop vim nginx

# Setup project directory
echo ""
echo "Step 6/6: Setting up project directory..."
mkdir -p ~/querio
cd ~/querio

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone https://github.com/paradocx96/querio.git"
echo "2. Navigate to the directory: cd querio"
echo "3. Create .env file with your GENAI_API_KEY"
echo "4. Run: docker-compose up -d"
echo ""
echo "Note: You may need to log out and log back in for Docker permissions to take effect."
echo "Or run: newgrp docker"
echo ""
