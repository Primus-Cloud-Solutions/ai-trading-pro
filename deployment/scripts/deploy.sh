#!/bin/bash

# AI Trading SaaS Platform - EC2 Deployment Script
# This script deploys the complete SaaS platform on Ubuntu EC2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as ubuntu user with sudo privileges."
fi

# Check required environment variables
check_env_vars() {
    log "Checking environment variables..."
    
    required_vars=(
        "DOMAIN_NAME"
        "EMAIL"
        "SECRET_KEY"
        "DATABASE_URL"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error "Missing required environment variables: ${missing_vars[*]}"
    fi
    
    log "All required environment variables are set"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
    log "System packages updated"
}

# Install required packages
install_packages() {
    log "Installing required packages..."
    
    # Install Python and development tools
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        git \
        curl \
        wget \
        unzip \
        nginx \
        postgresql \
        postgresql-contrib \
        redis-server \
        supervisor \
        certbot \
        python3-certbot-nginx \
        ufw
    
    log "Required packages installed"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw --force enable
    
    log "Firewall configured"
}

# Setup PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE ai_trading_saas;"
    sudo -u postgres psql -c "CREATE USER ai_trading_user WITH PASSWORD 'secure_password_123';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_trading_saas TO ai_trading_user;"
    sudo -u postgres psql -c "ALTER USER ai_trading_user CREATEDB;"
    
    log "PostgreSQL database configured"
}

# Setup Redis
setup_redis() {
    log "Setting up Redis..."
    
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Configure Redis for production
    sudo sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    sudo systemctl restart redis-server
    
    log "Redis configured"
}

# Create application user and directories
setup_app_structure() {
    log "Setting up application structure..."
    
    # Create application directory
    sudo mkdir -p /opt/ai_trading_saas
    sudo chown ubuntu:ubuntu /opt/ai_trading_saas
    
    # Create log directories
    sudo mkdir -p /var/log/ai_trading_saas
    sudo chown ubuntu:ubuntu /var/log/ai_trading_saas
    
    # Create run directory for sockets
    sudo mkdir -p /run/ai_trading_saas
    sudo chown ubuntu:ubuntu /run/ai_trading_saas
    
    log "Application structure created"
}

# Deploy application code
deploy_application() {
    log "Deploying application code..."
    
    # Copy application files
    cp -r /home/ubuntu/ai_trading_saas/* /opt/ai_trading_saas/
    cd /opt/ai_trading_saas
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create environment file
    cat > .env << EOF
FLASK_APP=src/main.py
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=${DATABASE_URL:-postgresql://ai_trading_user:secure_password_123@localhost/ai_trading_saas}
REDIS_URL=redis://localhost:6379/0
DOMAIN_NAME=${DOMAIN_NAME}
EMAIL=${EMAIL}
DEBUG=False
TESTING=False
EOF
    
    # Set proper permissions
    chmod 600 .env
    
    # Initialize database
    source venv/bin/activate
    python -c "
from src.main import create_app
app = create_app()
with app.app_context():
    from src.models.user import db
    db.create_all()
    print('Database initialized successfully')
"
    
    log "Application deployed"
}

# Configure Gunicorn
setup_gunicorn() {
    log "Setting up Gunicorn..."
    
    # Create Gunicorn configuration
    cat > /opt/ai_trading_saas/gunicorn.conf.py << 'EOF'
import multiprocessing

# Server socket
bind = "unix:/run/ai_trading_saas/gunicorn.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/ai_trading_saas/access.log"
errorlog = "/var/log/ai_trading_saas/error.log"
loglevel = "info"

# Process naming
proc_name = "ai_trading_saas"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/run/ai_trading_saas/gunicorn.pid"
user = "ubuntu"
group = "ubuntu"
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
EOF
    
    log "Gunicorn configured"
}

# Setup systemd service
setup_systemd() {
    log "Setting up systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/ai-trading-saas.service > /dev/null << EOF
[Unit]
Description=AI Trading SaaS Platform
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/ai_trading_saas
Environment=PATH=/opt/ai_trading_saas/venv/bin
EnvironmentFile=/opt/ai_trading_saas/.env
ExecStart=/opt/ai_trading_saas/venv/bin/gunicorn --config gunicorn.conf.py src.main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable ai-trading-saas
    
    log "Systemd service configured"
}

# Configure Nginx
setup_nginx() {
    log "Setting up Nginx..."
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/ai-trading-saas > /dev/null << EOF
upstream ai_trading_saas {
    server unix:/run/ai_trading_saas/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;
    
    # Client max body size
    client_max_body_size 10M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Static files
    location /static/ {
        alias /opt/ai_trading_saas/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API endpoints with rate limiting
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://ai_trading_saas;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://ai_trading_saas;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Main application
    location / {
        proxy_pass http://ai_trading_saas;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://ai_trading_saas;
        proxy_set_header Host \$host;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/ai-trading-saas /etc/nginx/sites-enabled/
    
    # Test Nginx configuration
    sudo nginx -t
    
    log "Nginx configured"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificate..."
    
    # Start Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Obtain SSL certificate
    sudo certbot --nginx -d ${DOMAIN_NAME} -d www.${DOMAIN_NAME} --non-interactive --agree-tos --email ${EMAIL}
    
    # Setup auto-renewal
    sudo systemctl enable certbot.timer
    
    log "SSL certificate configured"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Configure log rotation
    sudo tee /etc/logrotate.d/ai-trading-saas > /dev/null << EOF
/var/log/ai_trading_saas/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload ai-trading-saas
    endscript
}
EOF
    
    # Create monitoring script
    cat > /opt/ai_trading_saas/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script

# Check if application is running
if ! systemctl is-active --quiet ai-trading-saas; then
    echo "$(date): AI Trading SaaS service is down, restarting..." >> /var/log/ai_trading_saas/monitor.log
    systemctl restart ai-trading-saas
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is ${DISK_USAGE}%" >> /var/log/ai_trading_saas/monitor.log
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "$(date): Memory usage is ${MEM_USAGE}%" >> /var/log/ai_trading_saas/monitor.log
fi
EOF
    
    chmod +x /opt/ai_trading_saas/monitor.sh
    
    # Add monitoring to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/ai_trading_saas/monitor.sh") | crontab -
    
    log "Monitoring configured"
}

# Start all services
start_services() {
    log "Starting all services..."
    
    # Start application
    sudo systemctl start ai-trading-saas
    
    # Restart Nginx to apply SSL configuration
    sudo systemctl restart nginx
    
    # Check service status
    if systemctl is-active --quiet ai-trading-saas; then
        log "AI Trading SaaS service is running"
    else
        error "Failed to start AI Trading SaaS service"
    fi
    
    if systemctl is-active --quiet nginx; then
        log "Nginx service is running"
    else
        error "Failed to start Nginx service"
    fi
    
    log "All services started successfully"
}

# Display deployment information
show_deployment_info() {
    log "Deployment completed successfully!"
    echo
    echo -e "${BLUE}=== AI Trading SaaS Platform Deployment Information ===${NC}"
    echo -e "${GREEN}Application URL:${NC} https://${DOMAIN_NAME}"
    echo -e "${GREEN}Admin Panel:${NC} https://${DOMAIN_NAME}/admin"
    echo -e "${GREEN}API Documentation:${NC} https://${DOMAIN_NAME}/api/docs"
    echo
    echo -e "${BLUE}=== Service Management Commands ===${NC}"
    echo -e "${GREEN}Check status:${NC} sudo systemctl status ai-trading-saas"
    echo -e "${GREEN}View logs:${NC} sudo journalctl -u ai-trading-saas -f"
    echo -e "${GREEN}Restart service:${NC} sudo systemctl restart ai-trading-saas"
    echo
    echo -e "${BLUE}=== Important Files ===${NC}"
    echo -e "${GREEN}Application:${NC} /opt/ai_trading_saas"
    echo -e "${GREEN}Configuration:${NC} /opt/ai_trading_saas/.env"
    echo -e "${GREEN}Logs:${NC} /var/log/ai_trading_saas/"
    echo -e "${GREEN}Nginx config:${NC} /etc/nginx/sites-available/ai-trading-saas"
    echo
    echo -e "${YELLOW}Please save these details for future reference!${NC}"
}

# Main deployment function
main() {
    log "Starting AI Trading SaaS Platform deployment..."
    
    check_env_vars
    update_system
    install_packages
    configure_firewall
    setup_database
    setup_redis
    setup_app_structure
    deploy_application
    setup_gunicorn
    setup_systemd
    setup_nginx
    setup_ssl
    setup_monitoring
    start_services
    show_deployment_info
    
    log "Deployment completed successfully!"
}

# Run main function
main "$@"

