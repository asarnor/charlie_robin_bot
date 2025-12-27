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

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your broker credentials:

### Charles Schwab Setup

1. **Get API Credentials**:
   - Register for a Charles Schwab Developer Account
   - Visit: https://developer.schwab.com/
   - Create an app to get your API key and app secret

2. **Configure in `.env`**:
```env
SCHWAB_ENABLED=true
SCHWAB_API_KEY=your_api_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:8182/
SCHWAB_TOKEN_PATH=./schwab_token.json
```

3. **First-time Authentication**:
   - When you first run the bot, it will open a browser for OAuth authentication
   - Complete the authentication flow
   - The token will be saved to `schwab_token.json`

### Robinhood Setup

**⚠️ Important Note**: Robinhood does not offer an official public API. The Python version uses the unofficial `robin-stocks` library. Using unofficial APIs may violate Robinhood's Terms of Service. Use at your own risk.

1. **Configure in `.env`**:
```env
ROBINHOOD_ENABLED=true
ROBINHOOD_USERNAME=your_username
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_CODE=your_mfa_code_if_needed
```

## Usage

### Python Version

1. Configure your watchlist in `trading_bot.py`:
```python
WATCHLIST = ['SPY', 'QQQ', 'TSLA', 'NVDA']  # ETFs and stocks
OPTIONS_WATCHLIST = ['SPY', 'QQQ']  # Tickers to monitor for options
```

2. Adjust trading parameters:
```python
MAX_DRAWDOWN_PCT = 0.10  # Sell if loss > 10%
WASH_SALE_DAYS = 31  # IRS wash sale cooldown period
```

3. Run the bot:
```bash
python trading_bot.py
```

### JavaScript Version

1. Configure your watchlist in `trading_bot.js`:
```javascript
const WATCHLIST = ['SPY', 'QQQ', 'TSLA', 'NVDA'];
const OPTIONS_WATCHLIST = ['SPY', 'QQQ'];
```

2. Run the bot:
```bash
npm start
# or
node trading_bot.js
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
├── main.py                 # Original reference file
├── trading_bot.py          # Python trading bot
├── trading_bot.js          # JavaScript trading bot
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── bot_state.json          # Bot state (created at runtime)
└── schwab_token.json       # Schwab OAuth token (created at runtime)
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

## Important Disclaimers

⚠️ **USE AT YOUR OWN RISK**

- This bot is for educational purposes
- Trading involves risk of financial loss
- Always test thoroughly before using real money
- Review and understand all code before deployment
- Ensure compliance with broker Terms of Service
- Consider tax implications of automated trading
- Robinhood integration uses unofficial APIs (may violate ToS)

## Troubleshooting

### Python Issues

**Import Errors**:
```bash
pip install --upgrade -r requirements.txt
```

**Schwab Authentication**:
- Ensure callback URL matches your app configuration
- Delete `schwab_token.json` and re-authenticate if needed

**Robinhood Login**:
- Check if 2FA is enabled and provide MFA code
- Ensure credentials are correct

### JavaScript Issues

**Module Not Found**:
```bash
npm install
```

**Schwab API**:
- Ensure `@allensarkisyan/schwab-td-ameritrade-api` is installed
- Check token path permissions

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License - See LICENSE file for details

## Support

For issues related to:
- **Schwab API**: Check [Schwab Developer Documentation](https://developer.schwab.com/)
- **Robinhood**: Note that there's no official API support
- **Bot Logic**: Review the code comments and adjust as needed

## Future Enhancements

- [ ] Add more technical indicators
- [ ] Implement backtesting
- [ ] Add web dashboard
- [ ] Support for more brokers
- [ ] Advanced options strategies
- [ ] Paper trading mode
- [ ] Email/SMS notifications
- [ ] Performance analytics

