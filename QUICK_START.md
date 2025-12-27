# Quick Start Deployment Guide

## 🚀 Quick Deploy (One Command)

```bash
./deploy.sh [local|sandbox|production]
```

This script will:
1. ✅ Validate environment
2. ✅ Test broker connections
3. ✅ Deploy using available method (Docker/PM2/systemd)
4. ✅ Start the bot

## 📋 Step-by-Step Deployment

### 1. Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp env.local.example .env.local
# Edit .env.local with your credentials

# Test
ENVIRONMENT=local python test_connection.py

# Run
ENVIRONMENT=local python trading_bot.py
```

### 2. Sandbox/Testing

```bash
# Configure
cp env.sandbox.example .env.sandbox
# Edit .env.sandbox with sandbox credentials

# Test
ENVIRONMENT=sandbox python test_connection.py

# Deploy
ENVIRONMENT=sandbox ./deploy.sh sandbox
```

### 3. Production

#### Option A: Docker (Recommended)

```bash
# Configure
cp env.production.example .env.production
# Edit .env.production with production credentials

# Test
ENVIRONMENT=production python test_connection.py

# Deploy
ENVIRONMENT=production docker-compose up -d

# Monitor
docker-compose logs -f
```

#### Option B: systemd (Linux)

```bash
# Create service file (see DEPLOYMENT.md)
sudo nano /etc/systemd/system/trading-bot.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Monitor
sudo journalctl -u trading-bot -f
```

#### Option C: PM2 (Node.js)

```bash
# Install PM2
npm install -g pm2

# Start
ENVIRONMENT=production pm2 start ecosystem.config.js --env production

# Monitor
pm2 logs trading-bot
pm2 monit
```

## 🔍 Verification

After deployment, verify the bot is running:

```bash
# Test connection
ENVIRONMENT=production python test_connection.py

# Check logs
# Docker: docker-compose logs -f
# systemd: sudo journalctl -u trading-bot -f
# PM2: pm2 logs trading-bot
```

## 🛠️ Common Commands

### Docker
```bash
docker-compose up -d          # Start
docker-compose down            # Stop
docker-compose logs -f         # View logs
docker-compose restart         # Restart
docker-compose ps              # Status
```

### systemd
```bash
sudo systemctl start trading-bot    # Start
sudo systemctl stop trading-bot     # Stop
sudo systemctl restart trading-bot   # Restart
sudo systemctl status trading-bot    # Status
sudo journalctl -u trading-bot -f   # Logs
```

### PM2
```bash
pm2 start trading-bot          # Start
pm2 stop trading-bot           # Stop
pm2 restart trading-bot        # Restart
pm2 status                     # Status
pm2 logs trading-bot           # Logs
pm2 monit                      # Monitor
```

## 📝 Environment Checklist

Before deploying to production:

- [ ] Credentials configured in `.env.production`
- [ ] Connection test passes (`test_connection.py`)
- [ ] Logs directory exists and is writable
- [ ] State file directory exists
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Rollback plan prepared

## 🆘 Troubleshooting

### Bot won't start
```bash
# Check logs
docker-compose logs
# or
sudo journalctl -u trading-bot -n 50

# Test connection
ENVIRONMENT=production python test_connection.py

# Verify environment variables
env | grep SCHWAB
env | grep ROBINHOOD
```

### Connection issues
```bash
# Run connection test
python test_connection.py

# Check credentials
cat .env.production | grep -E "(SCHWAB|ROBINHOOD)"

# Verify network connectivity
ping api.schwabapi.com
```

### Performance issues
```bash
# Check resource usage
top
htop
df -h

# Review cycle intervals in .env file
grep CYCLE_INTERVAL .env.production
```

## 💰 Free & Low-Cost Hosting

Looking for free or cheap platforms to deploy? See [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) for:
- **Oracle Cloud** - Free forever (recommended)
- **Railway.app** - Easiest setup ($5/month credit)
- **DigitalOcean** - Best value ($4-6/month)
- **Hetzner** - Best performance/price (€4/month)
- And more options with free credits!

## 📚 More Information

- **Free/Cheap Hosting**: See [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md)
- **Full Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Environment Setup**: See [ENV_SETUP.md](ENV_SETUP.md)
- **Configuration**: See [README.md](README.md)

