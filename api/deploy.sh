#!/bin/bash
# Whisky Bottle Recognition API Deployment Script
# This script helps deploy the API to GitHub and AWS EC2

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration variables - edit these
GITHUB_REPO=""  # Example: https://github.com/yourusername/whisky-api.git
EC2_IP=""       # Example: 54.123.45.678
EC2_USER="ubuntu"
EC2_KEY_PATH="" # Example: ~/.ssh/whisky-api-key.pem

# Check if required variables are set
check_config() {
    if [ -z "$GITHUB_REPO" ]; then
        echo -e "${RED}Error: GITHUB_REPO is not set in the script.${NC}"
        echo "Please edit the script and set your GitHub repository URL."
        exit 1
    fi

    if [ -z "$EC2_IP" ]; then
        echo -e "${RED}Error: EC2_IP is not set in the script.${NC}"
        echo "Please edit the script and set your EC2 instance IP address."
        exit 1
    fi

    if [ -z "$EC2_KEY_PATH" ]; then
        echo -e "${RED}Error: EC2_KEY_PATH is not set in the script.${NC}"
        echo "Please edit the script and set the path to your EC2 key file."
        exit 1
    fi
}

# Push to GitHub
push_to_github() {
    echo -e "${YELLOW}Pushing code to GitHub...${NC}"
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git is not installed.${NC}"
        exit 1
    fi
    
    # Check if .git directory exists
    if [ ! -d ".git" ]; then
        echo "Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit"
        git branch -M main
        git remote add origin $GITHUB_REPO
    else
        echo "Adding and committing changes..."
        git add .
        git commit -m "Update API code - $(date)"
    fi
    
    echo "Pushing to GitHub..."
    git push -u origin main
    
    echo -e "${GREEN}Successfully pushed to GitHub!${NC}"
}

# Deploy to AWS EC2
deploy_to_ec2() {
    echo -e "${YELLOW}Deploying to AWS EC2...${NC}"
    
    # Check if SSH key exists
    if [ ! -f "$EC2_KEY_PATH" ]; then
        echo -e "${RED}Error: EC2 key file not found at $EC2_KEY_PATH${NC}"
        exit 1
    fi
    
    # Check if SSH key has correct permissions
    current_perms=$(stat -c %a "$EC2_KEY_PATH" 2>/dev/null || stat -f %Lp "$EC2_KEY_PATH" 2>/dev/null)
    if [ "$current_perms" != "400" ] && [ "$current_perms" != "600" ]; then
        echo "Setting correct permissions on SSH key..."
        chmod 400 "$EC2_KEY_PATH"
    fi
    
    # Create the remote directory structure
    echo "Creating remote directory structure..."
    ssh -i "$EC2_KEY_PATH" "$EC2_USER@$EC2_IP" "mkdir -p ~/whisky-api"
    
    # Copy files to EC2
    echo "Copying files to EC2..."
    scp -i "$EC2_KEY_PATH" -r ./* "$EC2_USER@$EC2_IP:~/whisky-api/"
    
    # Set up and run the API on EC2
    echo "Setting up the API on EC2..."
    ssh -i "$EC2_KEY_PATH" "$EC2_USER@$EC2_IP" "cd ~/whisky-api && \
        sudo apt update && \
        sudo apt install -y docker.io docker-compose && \
        sudo systemctl enable docker && \
        sudo systemctl start docker && \
        sudo usermod -aG docker ubuntu && \
        mkdir -p data/embeddings static/images && \
        sudo docker-compose up -d --build"
    
    echo -e "${GREEN}Deployment to EC2 completed!${NC}"
    echo "API is running at http://$EC2_IP:8000"
    echo "Note: You still need to process your dataset. Connect to the instance and run:"
    echo "cd ~/whisky-api && docker-compose exec api python process_dataset.py --input /path/to/images --output data/embeddings --metadata data/metadata.json --copy-images"
}

# Main execution
main() {
    echo "================================================"
    echo "    Whisky Bottle Recognition API Deployment"
    echo "================================================"
    
    # Check configuration
    check_config
    
    # Menu
    echo "Select an option:"
    echo "1) Push to GitHub"
    echo "2) Deploy to AWS EC2"
    echo "3) Do both"
    echo "4) Exit"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            push_to_github
            ;;
        2)
            deploy_to_ec2
            ;;
        3)
            push_to_github
            deploy_to_ec2
            ;;
        4)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting...${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}Deployment completed successfully!${NC}"
}

# Run the main function
main 