# Free & Low-Cost Deployment Platforms

This guide covers free and affordable platforms to deploy your trading bot, with specific recommendations and setup instructions.

## 🆓 Free Tier Options

### 1. **Oracle Cloud Infrastructure (OCI) - FREE TIER** ⭐ RECOMMENDED

**Why it's great:**
- **Always Free**: 2 AMD-based VMs (1/8 OCPU, 1GB RAM each) - PERMANENTLY FREE
- **No credit card required** for ARM instances
- **24/7 uptime** - perfect for trading bots
- **2 ARM-based VMs** (4 OCPU, 24GB RAM) - Always Free
- **10TB egress** per month free
- **No time limits** - truly always free

**Cost:** $0/month (forever)

**Setup:**
```bash
# 1. Sign up at cloud.oracle.com (free tier)
# 2. Create an Ubuntu 22.04 instance
# 3. SSH into instance
ssh opc@your-instance-ip

# 4. Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv git

# 5. Clone and setup
git clone <your-repo-url>
cd charlie_robin_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure
cp env.production.example .env.production
nano .env.production  # Add your credentials

# 7. Setup systemd service
sudo nano /etc/systemd/system/trading-bot.service
# (Use config from DEPLOYMENT.md)

# 8. Start
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

**Pros:**
- ✅ Truly free forever
- ✅ 24/7 uptime
- ✅ Good performance
- ✅ No credit card needed for ARM instances

**Cons:**
- ⚠️ Account approval can take time
- ⚠️ ARM instances may need some package adjustments

---

### 2. **Google Cloud Platform (GCP) - FREE TIER**

**Why it's great:**
- **$300 free credit** for 90 days
- **Always Free**: f1-micro instance (1 vCPU, 0.6GB RAM) in specific regions
- **e2-micro** instances eligible for always-free tier
- Good for low-resource bots

**Cost:** $0/month (after free credit expires, ~$5-10/month for e2-micro)

**Setup:**
```bash
# 1. Sign up at cloud.google.com (get $300 credit)
# 2. Create VM instance (e2-micro, Ubuntu 22.04)
# 3. Enable Always Free eligibility in us-west1, us-central1, us-east1

# 4. SSH via browser or gcloud CLI
gcloud compute ssh your-instance-name --zone=us-west1-a

# 5. Follow same setup as OCI above
```

**Pros:**
- ✅ $300 free credit to start
- ✅ Always-free tier available
- ✅ Easy to use
- ✅ Good documentation

**Cons:**
- ⚠️ Limited resources on free tier
- ⚠️ May need to pay after free credit expires

---

### 3. **AWS Free Tier**

**Why it's great:**
- **12 months free** for new accounts
- **t2.micro** or **t3.micro** instances free for 750 hours/month
- **t4g.micro** (ARM) - always free tier eligible
- Can run 24/7 if you use t4g.micro

**Cost:** $0/month (first year), then ~$7-10/month

**Setup:**
```bash
# 1. Sign up at aws.amazon.com
# 2. Launch EC2 instance (t4g.micro, Ubuntu 22.04)
# 3. Select "Always Free Tier Eligible"
# 4. Configure security group (SSH access)
# 5. Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-ip

# 6. Follow setup steps (same as OCI)
```

**Pros:**
- ✅ Well-documented
- ✅ Reliable infrastructure
- ✅ Good free tier

**Cons:**
- ⚠️ Only 12 months free (then pay)
- ⚠️ Can accidentally incur charges

---

### 4. **Railway.app** ⭐ EASIEST SETUP

**Why it's great:**
- **$5 free credit** per month (enough for small bots)
- **One-click deployment** from GitHub
- **Automatic HTTPS**
- **Built-in monitoring**
- **No server management**

**Cost:** $0-5/month (free credit covers most usage)

**Setup:**
```bash
# 1. Sign up at railway.app (GitHub login)
# 2. Click "New Project" → "Deploy from GitHub"
# 3. Select your repository
# 4. Add environment variables in Railway dashboard:
#    - ENVIRONMENT=production
#    - SCHWAB_API_KEY=...
#    - SCHWAB_APP_SECRET=...
#    - etc.

# 5. Railway auto-detects Python/Node.js and deploys!
# 6. Bot runs automatically
```

**Pros:**
- ✅ Easiest deployment
- ✅ No server management
- ✅ Auto-scaling
- ✅ Built-in monitoring

**Cons:**
- ⚠️ Free tier limited ($5/month credit)
- ⚠️ May need to pay for 24/7 uptime

---

### 5. **Render.com**

**Why it's great:**
- **Free tier** for web services (sleeps after inactivity)
- **$7/month** for always-on workers
- **Easy GitHub integration**
- **Free SSL**

**Cost:** $0/month (sleeps) or $7/month (always-on)

**Setup:**
```bash
# 1. Sign up at render.com
# 2. New → Background Worker
# 3. Connect GitHub repo
# 4. Set:
#    - Build Command: pip install -r requirements.txt
#    - Start Command: python trading_bot.py
#    - Environment: production
# 5. Add environment variables
# 6. Deploy!
```

**Pros:**
- ✅ Easy setup
- ✅ Free tier available
- ✅ Good for testing

**Cons:**
- ⚠️ Free tier sleeps (not good for trading bots)
- ⚠️ Need paid plan for 24/7

---

## 💰 Low-Cost Paid Options

### 1. **DigitalOcean** - $4-6/month ⭐ BEST VALUE

**Why it's great:**
- **$4/month** for basic droplet (1GB RAM, 1 vCPU)
- **$6/month** for standard (1GB RAM, 1 vCPU, better performance)
- **Simple pricing** - no surprises
- **Great performance**
- **$200 free credit** for new users

**Cost:** $4-6/month

**Setup:**
```bash
# 1. Sign up at digitalocean.com (get $200 credit)
# 2. Create Droplet (Ubuntu 22.04, $4/month plan)
# 3. SSH into droplet
ssh root@your-droplet-ip

# 4. Follow standard setup
```

**Pros:**
- ✅ Predictable pricing
- ✅ Great performance
- ✅ Simple interface
- ✅ $200 free credit

**Cons:**
- ⚠️ Not free (but very cheap)

---

### 2. **Linode (Akamai)** - $5/month

**Why it's great:**
- **$5/month** for Nanode (1GB RAM, 1 vCPU)
- **$100 free credit** for new users
- **Good performance**
- **Simple pricing**

**Cost:** $5/month

**Setup:** Similar to DigitalOcean

**Pros:**
- ✅ Simple pricing
- ✅ Good performance
- ✅ $100 free credit

**Cons:**
- ⚠️ Not free

---

### 3. **Vultr** - $2.50-6/month

**Why it's great:**
- **$2.50/month** for basic (512MB RAM) - may be too small
- **$6/month** for standard (1GB RAM, 1 vCPU)
- **$100 free credit** for new users
- **Many locations**

**Cost:** $2.50-6/month

**Setup:** Similar to DigitalOcean

**Pros:**
- ✅ Very cheap
- ✅ Many locations
- ✅ $100 free credit

**Cons:**
- ⚠️ Cheapest plan may be too small

---

### 4. **Hetzner Cloud** - €4/month (~$4.50)

**Why it's great:**
- **€4/month** (~$4.50) for CX11 (2GB RAM, 2 vCPU)
- **Best performance/price ratio**
- **European company** (GDPR compliant)
- **€20 free credit**

**Cost:** €4/month (~$4.50)

**Setup:** Similar to DigitalOcean

**Pros:**
- ✅ Best value
- ✅ More RAM/CPU for price
- ✅ €20 free credit

**Cons:**
- ⚠️ European data centers (may have latency)

---

## 🎯 Recommendations by Use Case

### For Absolute Free (Forever)
1. **Oracle Cloud Infrastructure** - Best option, truly free forever
2. **AWS t4g.micro** - Free tier, but only 12 months

### For Easiest Setup
1. **Railway.app** - One-click deployment, $5/month credit
2. **Render.com** - Easy setup, but need paid for 24/7

### For Best Value (Low Cost)
1. **Hetzner Cloud** - €4/month, best performance/price
2. **DigitalOcean** - $4-6/month, simple and reliable
3. **Vultr** - $6/month, many locations

### For Testing/Development
1. **Railway.app** - Free tier good for testing
2. **Render.com** - Free tier for development
3. **Local machine** - Free, but not 24/7

---

## 📊 Comparison Table

| Platform | Cost/Month | RAM | CPU | Free Credit | Best For |
|----------|-----------|-----|-----|-------------|----------|
| **Oracle Cloud** | $0 | 1-24GB | 1-4 cores | N/A | **Best free option** |
| **AWS t4g.micro** | $0 (12mo) | 1GB | 1 core | $300 | Free tier |
| **GCP e2-micro** | $0-5 | 0.6-1GB | 1 core | $300 | Free tier |
| **Railway** | $0-5 | Variable | Variable | $5 | **Easiest setup** |
| **Render** | $0-7 | Variable | Variable | N/A | Easy setup |
| **DigitalOcean** | $4-6 | 1GB | 1 core | $200 | **Best value** |
| **Hetzner** | €4 (~$4.50) | 2GB | 2 cores | €20 | **Best performance** |
| **Vultr** | $6 | 1GB | 1 core | $100 | Many locations |
| **Linode** | $5 | 1GB | 1 core | $100 | Simple pricing |

---

## 🚀 Quick Start: Oracle Cloud (Free Forever)

Here's a complete setup guide for Oracle Cloud, the best free option:

### Step 1: Sign Up
1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Start for Free"
3. Create account (no credit card needed for ARM instances)

### Step 2: Create Instance
1. Navigate to "Compute" → "Instances"
2. Click "Create Instance"
3. Select:
   - **Shape**: VM.Standard.A1.Flex (ARM, Always Free)
   - **Image**: Ubuntu 22.04
   - **4 OCPUs, 24GB RAM** (Always Free)
   - **SSH Keys**: Upload your public key or generate new

### Step 3: Configure Security
1. Go to "Networking" → "Security Lists"
2. Add Ingress Rule:
   - Source: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port: 22 (SSH)

### Step 4: Deploy Bot
```bash
# SSH into instance
ssh opc@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone <your-repo-url>
cd charlie_robin_bot

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env.production.example .env.production
nano .env.production  # Add your credentials

# Test connection
ENVIRONMENT=production python test_connection.py

# Create systemd service
sudo nano /etc/systemd/system/trading-bot.service
```

**Service file content:**
```ini
[Unit]
Description=Charlie Robin Trading Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/charlie_robin_bot
Environment="ENVIRONMENT=production"
EnvironmentFile=/home/opc/charlie_robin_bot/.env.production
ExecStart=/home/opc/charlie_robin_bot/venv/bin/python /home/opc/charlie_robin_bot/trading_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

---

## 🎯 Quick Start: Railway.app (Easiest)

### Step 1: Sign Up
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub

### Step 2: Deploy
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python/Node.js

### Step 3: Configure
1. Go to "Variables" tab
2. Add all environment variables:
   ```
   ENVIRONMENT=production
   SCHWAB_API_KEY=your_key
   SCHWAB_APP_SECRET=your_secret
   ROBINHOOD_USERNAME=your_username
   ROBINHOOD_PASSWORD=your_password
   WATCHLIST=SPY,QQQ,TSLA
   OPTIONS_WATCHLIST=SPY,QQQ
   MAX_DRAWDOWN_PCT=0.10
   WASH_SALE_DAYS=31
   CYCLE_INTERVAL_SECONDS=900
   LOG_FILE=bot_state_production.json
   ```

### Step 4: Deploy
1. Railway automatically builds and deploys
2. Check "Deployments" tab for logs
3. Bot runs automatically!

---

## 💡 Cost Optimization Tips

1. **Use Free Tiers First**
   - Start with Oracle Cloud (free forever)
   - Test thoroughly before paying

2. **Monitor Usage**
   - Set up billing alerts
   - Monitor resource usage
   - Use free monitoring tools

3. **Optimize Bot**
   - Increase `CYCLE_INTERVAL_SECONDS` to reduce API calls
   - Reduce watchlist size if needed
   - Use efficient logging

4. **Combine Free Credits**
   - Use multiple platforms' free credits
   - Rotate if needed (not recommended for production)

5. **Start Small**
   - Begin with free tier
   - Upgrade only if needed
   - Monitor costs closely

---

## ⚠️ Important Considerations

### For Trading Bots Specifically:

1. **24/7 Uptime Required**
   - Free tiers that "sleep" won't work
   - Need always-on instances
   - Oracle Cloud, AWS t4g.micro, or paid plans

2. **Reliability**
   - Trading bots need high uptime
   - Free tiers may have limitations
   - Consider paid options for production

3. **Security**
   - Use environment variables (never commit secrets)
   - Enable firewall rules
   - Use SSH keys (not passwords)
   - Regular security updates

4. **Monitoring**
   - Set up alerts for bot failures
   - Monitor API rate limits
   - Track costs

---

## 🎓 Learning Resources

- **Oracle Cloud**: [docs.oracle.com](https://docs.oracle.com)
- **Railway**: [docs.railway.app](https://docs.railway.app)
- **DigitalOcean**: [docs.digitalocean.com](https://docs.digitalocean.com)
- **AWS Free Tier**: [aws.amazon.com/free](https://aws.amazon.com/free)

---

## 📝 Summary

**Best Free Option:** Oracle Cloud Infrastructure (free forever, 24/7)

**Easiest Setup:** Railway.app (one-click deployment)

**Best Value:** Hetzner Cloud (€4/month, best performance)

**Recommended Path:**
1. Start with **Oracle Cloud** (free forever)
2. Test thoroughly
3. If needed, upgrade to **Hetzner** or **DigitalOcean** ($4-6/month)

All platforms support the deployment methods outlined in [DEPLOYMENT.md](DEPLOYMENT.md).

