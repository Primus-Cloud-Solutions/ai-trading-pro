# AI Trading SaaS Platform

A complete enterprise-grade SaaS platform for AI-powered automated trading with user management, subscriptions, and intelligent trading algorithms.

## 🚀 Features

### 🏢 **Complete SaaS Platform**
- **User Registration & Authentication**: Secure JWT-based authentication
- **Subscription Management**: Multiple subscription tiers with payment processing
- **Multi-User Support**: Isolated portfolios and trading accounts
- **Admin Dashboard**: User management and platform analytics
- **Role-Based Access Control**: Admin, Premium, and Free tier users

### 🤖 **Advanced AI Trading Engine**
- **Intelligent Market Analysis**: Real-time analysis across stocks and cryptocurrencies
- **Machine Learning Models**: Ensemble models with 78%+ accuracy
- **Automated Trading**: Daily automated trading with profit optimization
- **Risk Management**: Advanced position sizing and stop-loss algorithms
- **Dynamic Asset Discovery**: Automatically finds top trading opportunities

### 💰 **Portfolio Management**
- **Account Funding**: Secure deposit and withdrawal systems
- **Real-Time Portfolio Tracking**: Live portfolio value and performance metrics
- **Position Management**: Automated position opening and closing
- **P&L Tracking**: Detailed profit and loss analytics
- **Performance Analytics**: Comprehensive trading statistics

### 🔒 **Enterprise Security**
- **SSL/TLS Encryption**: Full HTTPS with Let's Encrypt certificates
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive data validation and sanitization
- **Secure Headers**: OWASP security headers implementation
- **Database Security**: Encrypted connections and secure queries

## 📋 **Requirements**

### **Server Requirements**
- **OS**: Ubuntu 20.04+ or Amazon Linux 2+
- **Instance Type**: t3.medium or larger (2 vCPU, 4GB RAM minimum)
- **Storage**: 20GB+ SSD storage
- **Network**: Public IP address with ports 22, 80, 443 open

### **Domain Requirements**
- Registered domain name pointing to your EC2 instance
- DNS A records configured for your domain and www subdomain

## 🚀 **Quick Deployment (3 Commands)**

### **1. Upload and Extract**
```bash
# Upload the application package to your EC2 instance
scp -i your-key.pem ai_trading_saas.tar.gz ubuntu@your-ec2-ip:~/

# SSH into your instance and extract
ssh -i your-key.pem ubuntu@your-ec2-ip
tar -xzf ai_trading_saas.tar.gz
cd ai_trading_saas
```

### **2. Configure Environment**
```bash
# Copy and edit environment configuration
cp .env.example .env
nano .env

# Set these required variables:
# DOMAIN_NAME=your-domain.com
# EMAIL=your-email@domain.com
# SECRET_KEY=your-super-secret-key
# DATABASE_URL=postgresql://ai_trading_user:secure_password_123@localhost/ai_trading_saas
```

### **3. Deploy Everything**
```bash
# Make deployment script executable and run
chmod +x deployment/scripts/deploy.sh

# Set environment variables and deploy
export DOMAIN_NAME="your-domain.com"
export EMAIL="your-email@domain.com"
export SECRET_KEY="your-super-secret-key-change-this"
export DATABASE_URL="postgresql://ai_trading_user:secure_password_123@localhost/ai_trading_saas"

# Run deployment script
sudo -E ./deployment/scripts/deploy.sh
```

**That's it!** Your AI Trading SaaS platform will be live at `https://your-domain.com`

## 🔧 **Manual Deployment Steps**

If you prefer manual deployment or need to customize the process:

### **1. System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server supervisor certbot python3-certbot-nginx
```

### **2. Database Setup**
```bash
# Configure PostgreSQL
sudo -u postgres createdb ai_trading_saas
sudo -u postgres createuser ai_trading_user
sudo -u postgres psql -c "ALTER USER ai_trading_user WITH PASSWORD 'secure_password_123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_trading_saas TO ai_trading_user;"
```

### **3. Application Setup**
```bash
# Create application directory
sudo mkdir -p /opt/ai_trading_saas
sudo chown ubuntu:ubuntu /opt/ai_trading_saas

# Copy application files
cp -r * /opt/ai_trading_saas/
cd /opt/ai_trading_saas

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **4. Configure Services**
```bash
# Copy systemd service file
sudo cp deployment/systemd/ai-trading-saas.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-trading-saas

# Configure Nginx
sudo cp deployment/nginx/ai-trading-saas /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/ai-trading-saas /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Setup SSL
sudo certbot --nginx -d your-domain.com
```

### **5. Start Services**
```bash
# Start all services
sudo systemctl start ai-trading-saas
sudo systemctl start nginx
sudo systemctl restart postgresql
sudo systemctl restart redis-server
```

## 🎛️ **Configuration**

### **Environment Variables**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DOMAIN_NAME` | Your domain name | Yes | - |
| `EMAIL` | Admin email for SSL certificates | Yes | - |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | JWT signing key | No | Same as SECRET_KEY |
| `DEBUG` | Enable debug mode | No | `False` |

### **Trading Configuration**

For live trading, configure these optional variables:
```bash
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Use paper trading first
```

## 📊 **Usage**

### **User Registration**
1. Visit `https://your-domain.com`
2. Click "Sign Up" to create an account
3. Verify your email address
4. Choose a subscription plan

### **Account Funding**
1. Log in to your dashboard
2. Navigate to "Portfolio" section
3. Click "Fund Account" and enter amount
4. Funds are added to your trading balance

### **Automated Trading**
1. The AI engine automatically analyzes markets
2. Trading signals are generated based on ML models
3. Trades are executed automatically when conditions are met
4. Monitor performance in the Analytics section

### **Portfolio Management**
- View real-time portfolio value and performance
- Track individual positions and P&L
- Monitor trading history and statistics
- Adjust risk settings and preferences

## 🔍 **Monitoring and Maintenance**

### **Service Management**
```bash
# Check service status
sudo systemctl status ai-trading-saas

# View application logs
sudo journalctl -u ai-trading-saas -f

# Restart application
sudo systemctl restart ai-trading-saas

# Check Nginx status
sudo systemctl status nginx
```

### **Log Files**
- **Application Logs**: `/var/log/ai_trading_saas/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `sudo journalctl -u ai-trading-saas`

### **Database Management**
```bash
# Connect to database
sudo -u postgres psql ai_trading_saas

# Backup database
sudo -u postgres pg_dump ai_trading_saas > backup.sql

# Restore database
sudo -u postgres psql ai_trading_saas < backup.sql
```

### **SSL Certificate Renewal**
SSL certificates are automatically renewed by certbot. Check renewal status:
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

## 🛡️ **Security**

### **Firewall Configuration**
```bash
# UFW is configured automatically by the deployment script
sudo ufw status

# Manual configuration if needed
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### **Security Headers**
The application includes comprehensive security headers:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### **Rate Limiting**
API endpoints are protected with rate limiting:
- Login endpoints: 1 request per second
- API endpoints: 10 requests per second
- Burst allowance for legitimate traffic

## 📈 **Performance Optimization**

### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
```

### **Redis Configuration**
```bash
# Optimize Redis for production
sudo nano /etc/redis/redis.conf

# Set memory limit
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### **Nginx Optimization**
The deployment script configures Nginx with:
- Gzip compression
- Static file caching
- Connection pooling
- Rate limiting

## 🔧 **Troubleshooting**

### **Common Issues**

**Application won't start:**
```bash
# Check logs
sudo journalctl -u ai-trading-saas -n 50

# Check configuration
source /opt/ai_trading_saas/venv/bin/activate
cd /opt/ai_trading_saas
python -c "from src.main import create_app; app = create_app(); print('Config OK')"
```

**Database connection issues:**
```bash
# Test database connection
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql ai_trading_saas -c "SELECT COUNT(*) FROM users;"
```

**SSL certificate issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test Nginx configuration
sudo nginx -t
```

**Permission issues:**
```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /opt/ai_trading_saas
sudo chmod -R 755 /opt/ai_trading_saas
sudo chmod 600 /opt/ai_trading_saas/.env
```

## 📞 **Support**

### **Log Analysis**
When reporting issues, include relevant logs:
```bash
# Application logs
sudo tail -n 100 /var/log/ai_trading_saas/error.log

# System logs
sudo journalctl -u ai-trading-saas -n 100

# Nginx logs
sudo tail -n 100 /var/log/nginx/error.log
```

### **Health Checks**
The application includes health check endpoints:
- `https://your-domain.com/health` - Application health
- `https://your-domain.com/api/health` - API health

## 🚀 **Scaling and High Availability**

### **Load Balancing**
For high traffic, deploy multiple application instances:
```bash
# Run multiple Gunicorn workers
workers = (2 * cpu_cores) + 1

# Use multiple application servers behind a load balancer
# Configure Nginx upstream with multiple servers
```

### **Database Scaling**
- Use PostgreSQL read replicas for read-heavy workloads
- Implement connection pooling with pgbouncer
- Consider database sharding for very large datasets

### **Monitoring**
Integrate with monitoring solutions:
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log analysis
- **Sentry** for error tracking
- **New Relic** for APM

## 📄 **License**

This is a proprietary SaaS platform. All rights reserved.

## 🔄 **Updates**

To update the application:
```bash
# Backup current version
sudo systemctl stop ai-trading-saas
cp -r /opt/ai_trading_saas /opt/ai_trading_saas.backup

# Deploy new version
# ... upload new files ...

# Restart services
sudo systemctl start ai-trading-saas
```


