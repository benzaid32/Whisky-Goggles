# Whisky Bottle Recognition API - AWS EC2 Deployment Guide

This guide provides step-by-step instructions for deploying the Whisky Bottle Recognition API to an AWS EC2 instance.

## 1. Setting Up an EC2 Instance

### 1.1 Launch an EC2 Instance

1. Log in to the AWS Management Console and navigate to EC2.
2. Click "Launch Instance" and select "Ubuntu Server 22.04 LTS" (or newer).
3. Choose an instance type:
   - For testing: t2.micro (free tier)
   - For production: t2.medium or better (consider GPU instances for faster inference)
4. Configure instance details (default settings are generally fine).
5. Add storage (at least 20GB recommended).
6. Configure security group:
   - SSH (Port 22) - Restrict to your IP
   - HTTP (Port 80)
   - HTTPS (Port 443)
   - Custom TCP (Port 8000) for direct API access
7. Review and launch the instance.
8. Create or select an existing key pair for SSH access.
9. Launch the instance.

### 1.2 Connect to Your Instance

```bash
ssh -i /path/to/your-key.pem ubuntu@your-instance-public-ip
```

## 2. Installing Dependencies

### 2.1 Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.2 Install Docker and Docker Compose

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install -y docker-compose
```

Log out and log back in to apply the docker group changes.

## 3. Deploying the API

### 3.1 Clone the Repository

```bash
mkdir -p ~/whisky-api
cd ~/whisky-api
```

### 3.2 Set Up the Application

Either clone your Git repository or upload the API files via SCP or SFTP.

To upload via SCP (from your local machine):
```bash
# From your local machine
scp -i /path/to/your-key.pem -r ./api ubuntu@your-instance-public-ip:~/whisky-api/
```

### 3.3 Configure Data Directories

```bash
cd ~/whisky-api
mkdir -p data/embeddings static/images
```

### 3.4 Process the Bottle Dataset

If using an existing dataset:
```bash
# Copy your bottle images to the server (from local machine)
scp -i /path/to/your-key.pem -r ./bottle-images ubuntu@your-instance-public-ip:~/whisky-api/bottle-images/

# Process the dataset
cd ~/whisky-api
docker-compose run api python process_dataset.py --input bottle-images --output data/embeddings --metadata data/metadata.json --copy-images
```

### 3.5 Run the API Server

```bash
cd ~/whisky-api
docker-compose up -d
```

The API should now be running at http://your-instance-public-ip:8000

## 4. Setting Up HTTPS with Nginx

### 4.1 Install Nginx and Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 4.2 Configure Nginx

Create a new Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/whisky-api
```

Add the following content:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/whisky-api /etc/nginx/sites-enabled/
sudo nginx -t  # Test the configuration
sudo systemctl reload nginx
```

### 4.3 Set Up SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts to complete the SSL setup. Certbot will automatically update your Nginx configuration to use HTTPS.

## 5. Setting Up Automatic Startup

To ensure the API starts automatically when the server reboots:

```bash
cd ~/whisky-api
echo "@reboot cd ~/whisky-api && docker-compose up -d" | crontab -
```

## 6. Monitoring and Maintenance

### 6.1 Check API Status

```bash
cd ~/whisky-api
docker-compose ps
```

### 6.2 View Logs

```bash
cd ~/whisky-api
docker-compose logs
```

For continuous log monitoring:
```bash
docker-compose logs -f
```

### 6.3 Restarting the API

```bash
cd ~/whisky-api
docker-compose restart
```

### 6.4 Updating the API

To update the API with new code:
```bash
cd ~/whisky-api
# Pull new code or update files
docker-compose build
docker-compose down
docker-compose up -d
```

## 7. Connect from React Native App

In your React Native app, use the following URL patterns:

- Development: `http://your-instance-public-ip:8000/api/identify`
- Production: `https://your-domain.com/api/identify`

Example API call from React Native:

```javascript
const uploadImage = async (imageUri) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'bottle.jpg',
  });

  try {
    const response = await fetch('https://your-domain.com/api/identify', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    });
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error identifying bottle:', error);
    throw error;
  }
};
```

## 8. Performance Optimization

For better performance:

1. **Consider using a GPU instance** if processing a large number of images or requiring faster inference times.
2. **Upgrade the instance type** if you experience slow response times.
3. **Implement caching** for frequently requested bottles.
4. **Scale horizontally** behind a load balancer if needed for high traffic. 