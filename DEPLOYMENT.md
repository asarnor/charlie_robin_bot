# Deployment Guide

This guide covers deploying the trading bot across different environments (local, sandbox, production).

## Table of Contents

1. [Local Development](#local-development)
2. [Sandbox/Testing Environment](#sandboxtesting-environment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Process Management](#process-management)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Considerations](#security-considerations)

---

## Local Development

### Prerequisites
- Python 3.8+ or Node.js 14+
- Virtual environment (Python) or npm (Node.js)
- Broker API credentials

### Setup Steps

#### Python

1. **Clone and setup**:
```bash
git clone <your-repo-url>
cd charlie_robin_bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp env.local.example .env.local
# Edit .env.local with your credentials
```

3. **Test connection**:
```bash
ENVIRONMENT=local python test_connection.py
```

4. **Run the bot**:
```bash
ENVIRONMENT=local python trading_bot.py
```

#### JavaScript

1. **Setup**:
```bash
npm install
```

2. **Configure environment**:
```bash
cp env.local.example .env.local
# Edit .env.local with your credentials
```

3. **Test connection**:
```bash
ENVIRONMENT=local npm test
```

4. **Run the bot**:
```bash
ENVIRONMENT=local npm start
```

---

## Sandbox/Testing Environment

Use sandbox environments to test with real API connections but without risking real money.

### Setup

1. **Create sandbox configuration**:
```bash
cp env.sandbox.example .env.sandbox
# Edit .env.sandbox with sandbox/test account credentials
```

2. **Configure sandbox-specific settings**:
```env
ENVIRONMENT=sandbox
WATCHLIST=SPY,QQQ  # Smaller watchlist for testing
MAX_DRAWDOWN_PCT=0.05  # More conservative
CYCLE_INTERVAL_SECONDS=1800  # Longer intervals
LOG_FILE=bot_state_sandbox.json
```

3. **Test sandbox connection**:
```bash
ENVIRONMENT=sandbox python test_connection.py
```

4. **Run in sandbox mode**:
```bash
ENVIRONMENT=sandbox python trading_bot.py
```

### Best Practices for Sandbox

- Use separate test accounts
- Monitor closely for first few days
- Test all features before production
- Keep logs separate from production

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests pass (`test_connection.py`)
- [ ] Credentials configured securely
- [ ] Environment variables set correctly
- [ ] Logging and monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback plan prepared
- [ ] Security review completed

### Option 1: Direct Server Deployment

#### Using systemd (Linux)

1. **Create service file** `/etc/systemd/system/trading-bot.service`:
```ini
[Unit]
Description=Charlie Robin Trading Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/charlie_robin_bot
Environment="ENVIRONMENT=production"
EnvironmentFile=/path/to/charlie_robin_bot/.env.production
ExecStart=/path/to/venv/bin/python /path/to/charlie_robin_bot/trading_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

3. **View logs**:
```bash
sudo journalctl -u trading-bot -f
```

#### Using PM2 (Node.js)

1. **Install PM2**:
```bash
npm install -g pm2
```

2. **Create ecosystem file** `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'trading-bot',
    script: './trading_bot.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'production'
    },
    env_file: '.env.production',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

3. **Start with PM2**:
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Setup PM2 to start on boot
```

4. **Monitor**:
```bash
pm2 status
pm2 logs trading-bot
pm2 monit
```

### Option 2: Docker Deployment

#### Create Dockerfile

**Python Dockerfile** (`Dockerfile.python`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY trading_bot.py test_connection.py ./

# Create logs directory
RUN mkdir -p /app/logs

# Run as non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "trading_bot.py"]
```

**JavaScript Dockerfile** (`Dockerfile.js`):
```dockerfile
FROM node:18-slim

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Copy application
COPY trading_bot.js test_connection.js ./

# Create logs directory
RUN mkdir -p /app/logs

# Run as non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

CMD ["node", "trading_bot.js"]
```

#### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  trading-bot:
    build:
      context: .
      dockerfile: Dockerfile.python  # or Dockerfile.js
    container_name: trading-bot-prod
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    volumes:
      - ./bot_state_production.json:/app/bot_state_production.json
      - ./schwab_token_production.json:/app/schwab_token_production.json
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Deploy with Docker Compose**:
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Cloud Deployment

#### AWS EC2 / Lightsail

1. **Launch instance** (Ubuntu 22.04 LTS recommended)
2. **SSH into instance**:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install dependencies**:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
# or for Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

4. **Clone repository**:
```bash
git clone <your-repo-url>
cd charlie_robin_bot
```

5. **Setup environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure secrets** (use AWS Secrets Manager or Parameter Store):
```bash
# Install AWS CLI
sudo apt install awscli

# Retrieve secrets (example)
aws secretsmanager get-secret-value --secret-id trading-bot/production | jq -r .SecretString > .env.production
```

7. **Setup systemd service** (see Option 1 above)

#### AWS Lambda (Serverless)

**Note**: Lambda has execution time limits. Consider using Step Functions or EventBridge for scheduling.

1. **Create Lambda deployment package**:
```bash
mkdir lambda-package
cp trading_bot.py lambda-package/
pip install -r requirements.txt -t lambda-package/
cd lambda-package
zip -r ../trading-bot.zip .
```

2. **Create Lambda function** with:
   - Runtime: Python 3.11
   - Handler: `trading_bot.lambda_handler`
   - Environment variables from Secrets Manager
   - Timeout: 15 minutes (max)
   - EventBridge trigger for scheduling

3. **Lambda handler wrapper** (`lambda_handler.py`):
```python
import os
import json

def lambda_handler(event, context):
    # Set environment
    os.environ['ENVIRONMENT'] = 'production'
    
    # Import and run bot
    from trading_bot import TradingBot
    
    bot = TradingBot()
    bot.run_bot_cycle()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Bot cycle completed')
    }
```

#### Google Cloud Run

1. **Create Dockerfile** (see Docker section above)

2. **Build and deploy**:
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/trading-bot

# Deploy
gcloud run deploy trading-bot \
  --image gcr.io/PROJECT_ID/trading-bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets SCHWAB_API_KEY=schwab-api-key:latest \
  --memory 512Mi \
  --timeout 900 \
  --max-instances 1
```

#### Heroku

1. **Create `Procfile`**:
```
worker: python trading_bot.py
```

2. **Create `runtime.txt`**:
```
python-3.11.0
```

3. **Deploy**:
```bash
heroku create your-app-name
heroku config:set ENVIRONMENT=production
heroku config:set SCHWAB_API_KEY=your-key
# ... set other env vars
git push heroku main
heroku ps:scale worker=1
```

---

## Process Management

### Python: Using supervisor

1. **Install supervisor**:
```bash
sudo apt install supervisor
```

2. **Create config** `/etc/supervisor/conf.d/trading-bot.conf`:
```ini
[program:trading-bot]
command=/path/to/venv/bin/python /path/to/trading_bot.py
directory=/path/to/charlie_robin_bot
user=your-username
autostart=true
autorestart=true
stderr_logfile=/var/log/trading-bot.err.log
stdout_logfile=/var/log/trading-bot.out.log
environment=ENVIRONMENT="production"
```

3. **Reload and start**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start trading-bot
```

### Node.js: Using PM2

See PM2 section in Production Deployment above.

---

## Monitoring & Logging

### Logging Setup

1. **Create logs directory**:
```bash
mkdir -p logs
```

2. **Configure log rotation** (`/etc/logrotate.d/trading-bot`):
```
/path/to/charlie_robin_bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 your-username your-group
}
```

### Monitoring Options

#### Option 1: Simple Health Check Script

Create `health_check.py`:
```python
#!/usr/bin/env python3
import os
import json
from datetime import datetime, timedelta

LOG_FILE = os.getenv('LOG_FILE', 'bot_state.json')

def check_bot_health():
    """Check if bot is running and healthy"""
    try:
        # Check if state file exists and is recent
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                state = json.load(f)
            
            # Check if bot has run recently (within last hour)
            # This is a simple check - adjust based on your needs
            return True, "Bot state file exists"
        else:
            return False, "Bot state file not found"
    except Exception as e:
        return False, f"Error: {e}"

if __name__ == "__main__":
    healthy, message = check_bot_health()
    print(f"Health: {'OK' if healthy else 'FAIL'}")
    print(f"Message: {message}")
    exit(0 if healthy else 1)
```

#### Option 2: Prometheus Metrics

Add metrics endpoint to bot (for HTTP-based monitoring):
```python
from prometheus_client import Counter, Gauge, start_http_server

# Metrics
cycles_completed = Counter('bot_cycles_completed', 'Total bot cycles')
positions_monitored = Gauge('bot_positions_monitored', 'Current positions')
errors_total = Counter('bot_errors_total', 'Total errors')

# Start metrics server
start_http_server(8000)
```

#### Option 3: External Monitoring Services

- **UptimeRobot**: Monitor HTTP health endpoint
- **Datadog**: Application performance monitoring
- **Sentry**: Error tracking
- **PagerDuty**: Alerting

### Alerting

Create `send_alert.py`:
```python
#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
import os

def send_alert(subject, message):
    """Send email alert"""
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    email_from = os.getenv('ALERT_EMAIL_FROM')
    email_to = os.getenv('ALERT_EMAIL_TO')
    email_password = os.getenv('ALERT_EMAIL_PASSWORD')
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
```

---

## Security Considerations

### 1. Credential Management

**Never commit credentials!**

#### Option A: Environment Files (Local/Small Deployments)
- Use `.env.{environment}` files
- Set restrictive permissions: `chmod 600 .env.production`
- Keep in `.gitignore`

#### Option B: Secrets Management (Production)

**AWS Secrets Manager**:
```python
import boto3
import json

def get_secrets():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='trading-bot/production')
    return json.loads(response['SecretString'])
```

**HashiCorp Vault**:
```python
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')
secrets = client.secrets.kv.v2.read_secret_version(path='trading-bot/production')
```

**Azure Key Vault**:
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net", credential=credential)
secret = client.get_secret("SCHWAB-API-KEY")
```

### 2. Network Security

- Use VPN for production servers
- Restrict SSH access (key-based only)
- Use firewall rules (UFW/iptables)
- Consider private networks/VPCs

### 3. Access Control

- Use least privilege principle
- Separate production and development access
- Enable 2FA for all accounts
- Regular credential rotation

### 4. Audit Logging

Enable audit logs for:
- Bot executions
- Trade executions
- Configuration changes
- Access attempts

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] All tests passing
- [ ] Credentials configured securely
- [ ] Environment variables set
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup strategy in place

### Deployment
- [ ] Deploy to sandbox first
- [ ] Test in sandbox for 24-48 hours
- [ ] Monitor logs and metrics
- [ ] Deploy to production
- [ ] Verify production deployment
- [ ] Monitor closely for first week

### Post-Deployment
- [ ] Verify bot is running
- [ ] Check logs for errors
- [ ] Monitor performance
- [ ] Set up alerts
- [ ] Document any issues

---

## Troubleshooting Deployment

### Bot Not Starting

1. **Check logs**:
```bash
# systemd
sudo journalctl -u trading-bot -n 50

# PM2
pm2 logs trading-bot

# Docker
docker logs trading-bot-prod
```

2. **Verify environment variables**:
```bash
# Check if env vars are loaded
env | grep SCHWAB
env | grep ROBINHOOD
```

3. **Test connection**:
```bash
ENVIRONMENT=production python test_connection.py
```

### Bot Crashing

1. **Check error logs**
2. **Verify API credentials**
3. **Check network connectivity**
4. **Review rate limits**
5. **Check disk space**

### Performance Issues

1. **Monitor resource usage**:
```bash
# CPU/Memory
top
htop

# Disk
df -h
```

2. **Review cycle intervals**
3. **Optimize watchlist size**
4. **Check API rate limits**

---

## Rollback Procedure

1. **Stop current deployment**:
```bash
# systemd
sudo systemctl stop trading-bot

# PM2
pm2 stop trading-bot

# Docker
docker-compose down
```

2. **Revert to previous version**:
```bash
git checkout <previous-commit>
# or
git revert <commit-hash>
```

3. **Redeploy**:
```bash
# Follow deployment steps again
```

4. **Verify**:
```bash
python test_connection.py
# Monitor logs
```

---

## Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Test connection script
4. Check broker API status
5. Review error messages

