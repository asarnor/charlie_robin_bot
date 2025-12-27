# Environment Configuration Guide

This guide explains how to set up and use environment-specific configuration files for the trading bot.

## Quick Start

1. **Run the setup script** (choose one):
   ```bash
   # Linux/Mac
   ./setup_env.sh
   
   # Windows PowerShell
   .\setup_env.ps1
   ```

2. **Or manually copy example files**:
   ```bash
   cp env.local.example .env.local
   cp env.sandbox.example .env.sandbox
   cp env.production.example .env.production
   ```

3. **Edit the appropriate `.env.{environment}` file** with your credentials

4. **Run the bot with the desired environment**:
   ```bash
   ENVIRONMENT=local python trading_bot.py
   ENVIRONMENT=sandbox python trading_bot.py
   ENVIRONMENT=production python trading_bot.py
   ```

## Environment Files

### `.env.local`
- **Purpose**: Local development and testing
- **Use Case**: Testing on your local machine
- **Settings**: Lower risk thresholds, shorter intervals for faster testing

### `.env.sandbox`
- **Purpose**: Testing with sandbox/test broker accounts
- **Use Case**: Testing with real API connections but fake money
- **Settings**: Conservative settings, longer intervals

### `.env.production`
- **Purpose**: Live trading with real money
- **Use Case**: Production deployment
- **Settings**: Production-grade settings, real account credentials
- **⚠️ WARNING**: Use extreme caution! Never commit this file!

## Environment Variables Reference

### Bot Configuration
| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Environment name | `local` | `local`, `sandbox`, `production` |
| `WATCHLIST` | Comma-separated tickers | `SPY,QQQ,TSLA,NVDA` | `SPY,QQQ,AAPL` |
| `OPTIONS_WATCHLIST` | Tickers for options analysis | `SPY,QQQ` | `SPY,QQQ,TSLA` |
| `MAX_DRAWDOWN_PCT` | Max loss before selling | `0.10` | `0.05`, `0.15` |
| `WASH_SALE_DAYS` | Wash sale cooldown period | `31` | `30`, `31` |
| `CYCLE_INTERVAL_SECONDS` | Bot cycle interval | `900` | `600`, `1800` |
| `LOG_FILE` | Bot state file path | `bot_state.json` | `bot_state_prod.json` |

### Charles Schwab Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SCHWAB_ENABLED` | Enable Schwab broker | Yes | `true`, `false` |
| `SCHWAB_API_KEY` | API key from Schwab | Yes | `your_api_key` |
| `SCHWAB_APP_SECRET` | App secret from Schwab | Yes | `your_app_secret` |
| `SCHWAB_CALLBACK_URL` | OAuth callback URL | Yes | `https://127.0.0.1:8182/` |
| `SCHWAB_TOKEN_PATH` | Path to save OAuth token | No | `./schwab_token.json` |
| `SCHWAB_ACCOUNT_ID` | Specific account ID | No | `123456789` |
| `SCHWAB_BASE_URL` | API base URL | No | `https://api.schwabapi.com/v1` |

### Robinhood Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ROBINHOOD_ENABLED` | Enable Robinhood broker | Yes | `true`, `false` |
| `ROBINHOOD_USERNAME` | Robinhood username | Yes | `your_username` |
| `ROBINHOOD_PASSWORD` | Robinhood password | Yes | `your_password` |
| `ROBINHOOD_MFA_CODE` | MFA code if enabled | No | `123456` |
| `ROBINHOOD_API_KEY` | API key (if using) | No | `your_api_key` |
| `ROBINHOOD_DEVICE_TOKEN` | Device token | No | `your_device_token` |

## Environment-Specific Recommendations

### Local Development
```env
ENVIRONMENT=local
WATCHLIST=SPY,QQQ
MAX_DRAWDOWN_PCT=0.05
CYCLE_INTERVAL_SECONDS=300  # 5 minutes for faster testing
LOG_FILE=bot_state_local.json
```

### Sandbox Testing
```env
ENVIRONMENT=sandbox
WATCHLIST=SPY,QQQ
MAX_DRAWDOWN_PCT=0.05
CYCLE_INTERVAL_SECONDS=1800  # 30 minutes
LOG_FILE=bot_state_sandbox.json
```

### Production
```env
ENVIRONMENT=production
WATCHLIST=SPY,QQQ,TSLA,NVDA,AAPL,MSFT
MAX_DRAWDOWN_PCT=0.10
CYCLE_INTERVAL_SECONDS=900  # 15 minutes
LOG_FILE=bot_state_production.json
```

## Security Best Practices

1. **Never commit `.env.*` files** to version control
2. **Use different credentials** for each environment
3. **Rotate credentials** regularly in production
4. **Use secrets management** in production deployments (AWS Secrets Manager, Azure Key Vault, etc.)
5. **Restrict file permissions** on production `.env` files:
   ```bash
   chmod 600 .env.production
   ```
6. **Use environment variables** in CI/CD pipelines instead of files
7. **Monitor access** to production credentials

## Troubleshooting

### Bot not loading environment file
- Check that `ENVIRONMENT` variable is set correctly
- Verify the `.env.{environment}` file exists
- Check file permissions
- Ensure `python-dotenv` (Python) or `dotenv` (Node.js) is installed

### Wrong environment loaded
- Verify `ENVIRONMENT` variable matches your file name
- Check for typos in environment name
- Ensure no conflicting `.env` file exists

### Credentials not working
- Verify credentials are correct for the environment
- Check if sandbox credentials are being used in production (or vice versa)
- Ensure API keys haven't expired
- Verify broker account is active

## Examples

### Python
```bash
# Local development
export ENVIRONMENT=local
python trading_bot.py

# Sandbox testing
export ENVIRONMENT=sandbox
python trading_bot.py

# Production
export ENVIRONMENT=production
python trading_bot.py
```

### JavaScript/Node.js
```bash
# Local development
export ENVIRONMENT=local
node trading_bot.js

# Sandbox testing
export ENVIRONMENT=sandbox
node trading_bot.js

# Production
export ENVIRONMENT=production
node trading_bot.js
```

### Windows PowerShell
```powershell
# Local development
$env:ENVIRONMENT="local"
python trading_bot.py

# Sandbox testing
$env:ENVIRONMENT="sandbox"
python trading_bot.py

# Production
$env:ENVIRONMENT="production"
python trading_bot.py
```

