# Charlie Robin Trading Bot

A trading bot for ETFs and options that supports both Charles Schwab and Robinhood brokers. The bot monitors your watchlist, analyzes positions, and executes trades based on capital erosion analysis while respecting IRS wash sale rules.

## Features

- **Multi-Broker Support**: Connect to both Charles Schwab and Robinhood
- **ETF Trading**: Monitor and trade ETFs
- **Options Trading**: Analyze and trade options chains
- **Wash Sale Protection**: Automatically tracks and prevents wash sale violations (IRS 30-day rule)
- **Capital Erosion Analysis**: Monitors positions and sells when losses exceed thresholds
- **State Persistence**: Maintains bot state across restarts
- **Dual Language Support**: Available in both Python and JavaScript

## Prerequisites

### Python Version
- Python 3.8 or higher
- pip package manager

### JavaScript Version
- Node.js 14.0 or higher
- npm package manager

## Installation

### Python Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd charlie_robin_bot
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### JavaScript Setup

1. Install dependencies:
```bash
npm install
```

## Configuration

The bot supports multiple environments (local, sandbox, production) with separate configuration files.

### Environment Setup

1. **Choose your environment** and copy the appropriate example file:
```bash
# For local development
cp env.local.example .env.local

# For sandbox/testing
cp env.sandbox.example .env.sandbox

# For production
cp env.production.example .env.production
```

2. **Set the ENVIRONMENT variable** when running the bot:
```bash
# Python
ENVIRONMENT=local python trading_bot.py
ENVIRONMENT=sandbox python trading_bot.py
ENVIRONMENT=production python trading_bot.py

# JavaScript
ENVIRONMENT=local npm start
ENVIRONMENT=sandbox npm start
ENVIRONMENT=production npm start
```

3. **Edit the appropriate `.env.{environment}` file** and configure your broker credentials:

### Environment Variables

All configuration is done through environment variables. The bot loads from `.env.{environment}` files based on the `ENVIRONMENT` variable.

**Available Configuration Variables:**

- `ENVIRONMENT`: Environment name (local, sandbox, production)
- `WATCHLIST`: Comma-separated list of tickers to monitor (e.g., "SPY,QQQ,TSLA")
- `OPTIONS_WATCHLIST`: Comma-separated list of tickers for options analysis
- `MAX_DRAWDOWN_PCT`: Maximum drawdown percentage before selling (default: 0.10)
- `WASH_SALE_DAYS`: Wash sale cooldown period in days (default: 31)
- `CYCLE_INTERVAL_SECONDS`: Bot cycle interval in seconds (default: 900)
- `LOG_FILE`: Path to bot state file

### Charles Schwab Setup

1. **Get API Credentials**:
   - Register for a Charles Schwab Developer Account
   - Visit: https://developer.schwab.com/
   - Create an app to get your API key and app secret

2. **Configure in your `.env.{environment}` file**:
```env
SCHWAB_ENABLED=true
SCHWAB_API_KEY=your_api_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:8182/
SCHWAB_TOKEN_PATH=./schwab_token.json
SCHWAB_ACCOUNT_ID=your_account_id  # Optional: specific account
SCHWAB_BASE_URL=https://api.schwabapi.com/v1  # Optional: API base URL
```

3. **First-time Authentication**:
   - When you first run the bot, it will open a browser for OAuth authentication
   - Complete the authentication flow
   - The token will be saved to `schwab_token.json`

### Robinhood Setup

**⚠️ Important Note**: Robinhood does not offer an official public API. The Python version uses the unofficial `robin-stocks` library. Using unofficial APIs may violate Robinhood's Terms of Service. Use at your own risk.

1. **Configure in your `.env.{environment}` file**:
```env
ROBINHOOD_ENABLED=true
ROBINHOOD_USERNAME=your_username
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_CODE=your_mfa_code_if_needed
ROBINHOOD_API_KEY=your_api_key  # Optional: if using API key
ROBINHOOD_DEVICE_TOKEN=your_device_token  # Optional: device token
```

## Usage

### Python Version

1. **Set up your environment file** (see Configuration section above)

2. **Configure your watchlist** in `.env.{environment}`:
```env
WATCHLIST=SPY,QQQ,TSLA,NVDA
OPTIONS_WATCHLIST=SPY,QQQ
```

3. **Adjust trading parameters** in `.env.{environment}`:
```env
MAX_DRAWDOWN_PCT=0.10
WASH_SALE_DAYS=31
CYCLE_INTERVAL_SECONDS=900
```

4. **Run the bot** with your chosen environment:
```bash
# Local development
ENVIRONMENT=local python trading_bot.py

# Sandbox/testing
ENVIRONMENT=sandbox python trading_bot.py

# Production
ENVIRONMENT=production python trading_bot.py
```

### JavaScript Version

1. **Set up your environment file** (see Configuration section above)

2. **Configure your watchlist** in `.env.{environment}`:
```env
WATCHLIST=SPY,QQQ,TSLA,NVDA
OPTIONS_WATCHLIST=SPY,QQQ
```

3. **Run the bot** with your chosen environment:
```bash
# Local development
ENVIRONMENT=local npm start

# Sandbox/testing
ENVIRONMENT=sandbox npm start

# Production
ENVIRONMENT=production npm start
```

## How It Works

### Trading Cycle

1. **Watchlist Monitoring**: The bot iterates through your watchlist
2. **Wash Sale Check**: Verifies if a ticker is in wash sale cooldown period
3. **Market Data Retrieval**: Fetches current prices and technical indicators
4. **Position Analysis**: Analyzes existing positions for capital erosion
5. **Decision Making**: Determines whether to hold or sell based on:
   - Capital loss vs. dividend gains
   - Maximum drawdown threshold
   - Wash sale rules
6. **Order Execution**: Places trades when conditions are met
7. **State Logging**: Records wash sale dates for future reference

### Wash Sale Protection

The bot automatically tracks when you sell a position at a loss and prevents repurchasing within 31 days (IRS rule is 30 days, we use 31 for safety). This information is persisted in `bot_state.json`.

### Capital Erosion Analysis

For each position, the bot calculates:
- Capital loss/gain: `current_price - average_cost`
- Net position: `capital_loss + dividends`
- If net position is negative and loss exceeds threshold → **SELL**

## File Structure

```
charlie_robin_bot/
├── main.py                      # Original reference file
├── trading_bot.py               # Python trading bot
├── trading_bot.js               # JavaScript trading bot
├── test_connection.py           # Python connection test script
├── test_connection.js           # JavaScript connection test script
├── requirements.txt             # Python dependencies
├── package.json                # Node.js dependencies
├── env.local.example            # Local environment template
├── env.sandbox.example          # Sandbox environment template
├── env.production.example       # Production environment template
├── .env.example                 # Generic environment template
├── setup_env.sh                 # Environment setup script (bash)
├── setup_env.ps1                # Environment setup script (PowerShell)
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── ENV_SETUP.md                 # Environment configuration guide
├── bot_state.json               # Bot state (created at runtime)
├── bot_state_sandbox.json      # Sandbox bot state (created at runtime)
├── bot_state_production.json   # Production bot state (created at runtime)
└── schwab_token*.json          # Schwab OAuth tokens (created at runtime)
```

## Customization

### Adding Custom Strategies

You can extend the bot by modifying:

1. **`analyze_erosion()`**: Change the capital erosion logic
2. **`analyze_options_opportunity()`**: Implement your options trading strategy
3. **`get_market_data()`**: Add more technical indicators
4. **Order placement**: Modify order types, quantities, or conditions

### Broker-Specific Customization

Each broker implementation (`SchwabBroker`, `RobinhoodBroker`) can be customized independently. The broker interface ensures consistent behavior across implementations.

## Safety Features

- **Wash Sale Protection**: Prevents IRS violations
- **Error Handling**: Comprehensive error handling and logging
- **State Persistence**: Bot state survives restarts
- **API Rate Limiting**: Built-in delays to respect API limits
- **Dry Run Mode**: Consider adding a dry-run flag before going live

## Environment Management

### Environment Files

The bot supports three environments, each with its own configuration:

1. **Local** (`.env.local`): For local development and testing
2. **Sandbox** (`.env.sandbox`): For testing with sandbox/test accounts
3. **Production** (`.env.production`): For live trading (use with extreme caution!)

### Best Practices

- **Never commit `.env.*` files** to version control (they're in `.gitignore`)
- Use **example files** (`env.*.example`) as templates
- Keep **separate credentials** for each environment
- Use **sandbox accounts** for testing before production
- **Rotate credentials** regularly in production
- Use **environment variables** or secrets management in production deployments

### Running in Different Environments

```bash
# Local development
export ENVIRONMENT=local
python trading_bot.py

# Sandbox testing
export ENVIRONMENT=sandbox
python trading_bot.py

# Production (be very careful!)
export ENVIRONMENT=production
python trading_bot.py
```

## Important Disclaimers

⚠️ **USE AT YOUR OWN RISK**

- This bot is for educational purposes
- Trading involves risk of financial loss
- Always test thoroughly before using real money
- Review and understand all code before deployment
- Ensure compliance with broker Terms of Service
- Consider tax implications of automated trading
- Robinhood integration uses unofficial APIs (may violate ToS)
- **Never commit production credentials** to version control
- Use **sandbox environments** for testing before production

## Testing Connections

Before running the bot, test your broker connections to ensure credentials are configured correctly:

### Python
```bash
# Test with default environment (local)
python test_connection.py

# Test with specific environment
ENVIRONMENT=sandbox python test_connection.py
ENVIRONMENT=production python test_connection.py
```

### JavaScript
```bash
# Test with default environment (local)
node test_connection.js
# or using npm
npm test

# Test with specific environment
ENVIRONMENT=sandbox node test_connection.js
ENVIRONMENT=production node test_connection.js
```

The test script will:
- ✓ Verify broker credentials are configured
- ✓ Test API connection and authentication
- ✓ Retrieve account information
- ✓ Test market data retrieval
- ✓ Display connection status and details

**Example Output**:
```
============================================================
Trading Bot Connection Test
============================================================

ℹ Environment: local
ℹ Testing brokers based on configuration...

============================================================
Testing Charles Schwab Connection
============================================================

✓ Successfully connected to Charles Schwab API
✓ Successfully retrieved account information
  Account ID: 123456789
✓ Successfully retrieved 5 positions
✓ Successfully retrieved market data for SPY: $450.23
```

## Troubleshooting

### Python Issues

**Import Errors**:
```bash
pip install --upgrade -r requirements.txt
```

**Schwab Authentication**:
- Ensure callback URL matches your app configuration
- Delete `schwab_token.json` and re-authenticate if needed
- Run `python test_connection.py` to verify credentials

**Robinhood Login**:
- Check if 2FA is enabled and provide MFA code
- Ensure credentials are correct
- Run `python test_connection.py` to verify credentials

### JavaScript Issues

**Module Not Found**:
```bash
npm install
```

**Schwab API**:
- Ensure `@allensarkisyan/schwab-td-ameritrade-api` is installed
- Check token path permissions
- Run `node test_connection.js` to verify credentials

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License - See LICENSE file for details

## Support

For issues related to:
- **Schwab API**: Check [Schwab Developer Documentation](https://developer.schwab.com/)
- **Robinhood**: Note that there's no official API support
- **Bot Logic**: Review the code comments and adjust as needed

## Deployment

### Quick Start

For a quick deployment guide, see [QUICK_START.md](QUICK_START.md).

### Quick Deploy

```bash
# Using the deployment script
./deploy.sh local      # Local development
./deploy.sh sandbox    # Sandbox/testing
./deploy.sh production # Production (be careful!)
```

### Deployment Options

1. **Docker** - Containerized deployment (recommended)
2. **systemd** - Linux service management
3. **PM2** - Node.js process manager
4. **Cloud** - AWS, GCP, Azure, Heroku

For detailed deployment instructions across different environments (local, sandbox, production), see [DEPLOYMENT.md](DEPLOYMENT.md).

**Looking for free/cheap hosting?** See [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) for recommendations including Oracle Cloud (free forever), Railway, and other affordable options.

## Future Enhancements

- [ ] Add more technical indicators
- [ ] Implement backtesting
- [ ] Add web dashboard
- [ ] Support for more brokers
- [ ] Advanced options strategies
- [ ] Paper trading mode
- [ ] Email/SMS notifications
- [ ] Performance analytics

