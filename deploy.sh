#!/bin/bash
# Deployment script for trading bot
# Usage: ./deploy.sh [local|sandbox|production]

set -e  # Exit on error

ENVIRONMENT=${1:-local}

echo "=========================================="
echo "Trading Bot Deployment Script"
echo "Environment: $ENVIRONMENT"
echo "=========================================="
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(local|sandbox|production)$ ]]; then
    echo "❌ Invalid environment: $ENVIRONMENT"
    echo "Usage: ./deploy.sh [local|sandbox|production]"
    exit 1
fi

# Check if .env file exists
ENV_FILE=".env.$ENVIRONMENT"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  $ENV_FILE not found!"
    echo "Creating from example..."
    if [ -f "env.$ENVIRONMENT.example" ]; then
        cp "env.$ENVIRONMENT.example" "$ENV_FILE"
        echo "✅ Created $ENV_FILE"
        echo "⚠️  Please edit $ENV_FILE with your credentials before continuing"
        exit 1
    else
        echo "❌ Example file env.$ENVIRONMENT.example not found"
        exit 1
    fi
fi

echo "📋 Pre-deployment checks..."
echo ""

# Test connection
echo "🔍 Testing broker connections..."
export ENVIRONMENT=$ENVIRONMENT
if python test_connection.py; then
    echo "✅ Connection test passed"
else
    echo "❌ Connection test failed!"
    echo "Please fix configuration issues before deploying"
    exit 1
fi

echo ""
echo "🚀 Starting deployment..."
echo ""

# Create logs directory
mkdir -p logs

# Check if using Docker
if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "🐳 Deploying with Docker..."
    export ENVIRONMENT=$ENVIRONMENT
    docker-compose down
    docker-compose build
    docker-compose up -d
    echo "✅ Docker deployment complete"
    echo ""
    echo "View logs with: docker-compose logs -f"
    
# Check if using PM2 (Node.js)
elif command -v pm2 &> /dev/null && [ -f "ecosystem.config.js" ]; then
    echo "📦 Deploying with PM2..."
    pm2 stop trading-bot || true
    pm2 delete trading-bot || true
    pm2 start ecosystem.config.js --env $ENVIRONMENT
    pm2 save
    echo "✅ PM2 deployment complete"
    echo ""
    echo "View logs with: pm2 logs trading-bot"
    
# Check if using systemd
elif systemctl list-unit-files | grep -q trading-bot; then
    echo "⚙️  Deploying with systemd..."
    sudo systemctl restart trading-bot
    sudo systemctl status trading-bot
    echo "✅ systemd deployment complete"
    echo ""
    echo "View logs with: sudo journalctl -u trading-bot -f"
    
# Direct Python execution
elif command -v python3 &> /dev/null; then
    echo "🐍 Running Python bot directly..."
    echo "⚠️  This will run in foreground. Use Ctrl+C to stop."
    echo "For production, consider using systemd, PM2, or Docker"
    echo ""
    export ENVIRONMENT=$ENVIRONMENT
    python3 trading_bot.py
    
# Direct Node.js execution
elif command -v node &> /dev/null; then
    echo "📦 Running Node.js bot directly..."
    echo "⚠️  This will run in foreground. Use Ctrl+C to stop."
    echo "For production, consider using PM2 or Docker"
    echo ""
    export ENVIRONMENT=$ENVIRONMENT
    node trading_bot.js
    
else
    echo "❌ No deployment method found"
    echo "Please install Docker, PM2, or configure systemd"
    exit 1
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Monitor logs for errors"
echo "2. Verify bot is running correctly"
echo "3. Check broker connections"
echo ""

