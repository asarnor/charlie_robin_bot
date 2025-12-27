/**
 * Trading Bot for ETFs and Options
 * Supports Charles Schwab and Robinhood
 */

// Load environment variables from .env file
const fs = require('fs');
const path = require('path');

// Determine environment (defaults to 'local')
const env = (process.env.ENVIRONMENT || 'local').toLowerCase();
const envFile = `.env.${env}`;

// Load environment-specific .env file
if (fs.existsSync(envFile)) {
    require('dotenv').config({ path: envFile });
    console.log(`Loaded environment from ${envFile}`);
} else {
    // Fallback to .env if environment-specific file doesn't exist
    require('dotenv').config();
    console.log('Loaded environment from .env');
}

// --- CONFIGURATION ---
const WATCHLIST = process.env.WATCHLIST 
    ? process.env.WATCHLIST.split(',').map(s => s.trim())
    : ['SPY', 'QQQ', 'TSLA', 'NVDA']; // ETFs and stocks
const OPTIONS_WATCHLIST = process.env.OPTIONS_WATCHLIST
    ? process.env.OPTIONS_WATCHLIST.split(',').map(s => s.trim())
    : ['SPY', 'QQQ']; // Tickers to monitor for options
const MAX_DRAWDOWN_PCT = parseFloat(process.env.MAX_DRAWDOWN_PCT || '0.10'); // Sell if loss > 10%
const WASH_SALE_DAYS = parseInt(process.env.WASH_SALE_DAYS || '31'); // IRS rule is 30 days; we use 31 to be safe
const LOG_FILE = process.env.LOG_FILE || 'bot_state.json';
const CYCLE_INTERVAL_SECONDS = parseInt(process.env.CYCLE_INTERVAL_SECONDS || '900'); // 15 minutes default
const ENVIRONMENT = (process.env.ENVIRONMENT || 'local').toLowerCase();

// Broker configuration (from environment variables)
const BROKERS = {
    schwab: {
        enabled: process.env.SCHWAB_ENABLED === 'true',
        apiKey: process.env.SCHWAB_API_KEY || '',
        appSecret: process.env.SCHWAB_APP_SECRET || '',
        callbackUrl: process.env.SCHWAB_CALLBACK_URL || 'https://127.0.0.1:8182/',
        tokenPath: process.env.SCHWAB_TOKEN_PATH || './schwab_token.json',
        accountId: process.env.SCHWAB_ACCOUNT_ID || '', // Optional: specific account ID
        baseUrl: process.env.SCHWAB_BASE_URL || '' // Optional: for sandbox/production URLs
    },
    robinhood: {
        enabled: process.env.ROBINHOOD_ENABLED === 'true',
        username: process.env.ROBINHOOD_USERNAME || '',
        password: process.env.ROBINHOOD_PASSWORD || '',
        mfaCode: process.env.ROBINHOOD_MFA_CODE || '',
        apiKey: process.env.ROBINHOOD_API_KEY || '', // If using API key instead of username/password
        deviceToken: process.env.ROBINHOOD_DEVICE_TOKEN || '' // Device token for authentication
    }
};

// --- STATE MANAGEMENT ---
function loadState() {
    try {
        if (fs.existsSync(LOG_FILE)) {
            const data = fs.readFileSync(LOG_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading state:', error);
    }
    return { wash_sale_log: {}, positions: {} };
}

function saveState(state) {
    try {
        fs.writeFileSync(LOG_FILE, JSON.stringify(state, null, 4));
    } catch (error) {
        console.error('Error saving state:', error);
    }
}

// --- BROKER INTERFACE ---
class BrokerInterface {
    /**
     * Connect to broker API
     * @returns {Promise<boolean>}
     */
    async connect() {
        throw new Error('connect() must be implemented');
    }

    /**
     * Get account information
     * @returns {Promise<Object>}
     */
    async getAccountInfo() {
        throw new Error('getAccountInfo() must be implemented');
    }

    /**
     * Get current positions
     * @returns {Promise<Array>}
     */
    async getPositions() {
        throw new Error('getPositions() must be implemented');
    }

    /**
     * Get current price and technical indicators
     * @param {string} ticker
     * @returns {Promise<{price: number, indicators: Object}>}
     */
    async getMarketData(ticker) {
        throw new Error('getMarketData() must be implemented');
    }

    /**
     * Get options chain for a ticker
     * @param {string} ticker
     * @param {string|null} expirationDate
     * @returns {Promise<Array>}
     */
    async getOptionsChain(ticker, expirationDate = null) {
        throw new Error('getOptionsChain() must be implemented');
    }

    /**
     * Place a trade order
     * @param {string} ticker
     * @param {string} action - 'BUY' or 'SELL'
     * @param {number} quantity
     * @param {string} orderType - 'MARKET' or 'LIMIT'
     * @param {number|null} price
     * @param {string|null} optionType - 'CALL' or 'PUT'
     * @param {number|null} strike
     * @param {string|null} expiration
     * @returns {Promise<boolean>}
     */
    async placeOrder(ticker, action, quantity, orderType = 'MARKET', price = null,
                     optionType = null, strike = null, expiration = null) {
        throw new Error('placeOrder() must be implemented');
    }

    /**
     * Check if ticker is an ETF
     * @param {string} ticker
     * @returns {Promise<boolean>}
     */
    async isETF(ticker) {
        throw new Error('isETF() must be implemented');
    }
}

class SchwabBroker extends BrokerInterface {
    constructor(config) {
        super();
        this.config = config;
        this.client = null;
        this.connected = false;
    }

    async connect() {
        try {
            // Try to import schwab-td-ameritrade-api library
            let SchwabClient;
            try {
                SchwabClient = require('@allensarkisyan/schwab-td-ameritrade-api');
            } catch (error) {
                console.error('schwab-td-ameritrade-api library not installed. Install with: npm install @allensarkisyan/schwab-td-ameritrade-api');
                return false;
            }

            if (!this.config.apiKey || !this.config.appSecret) {
                console.error('Schwab API credentials not configured');
                return false;
            }

            this.client = new SchwabClient({
                apiKey: this.config.apiKey,
                redirectUri: this.config.callbackUrl,
                tokenPath: this.config.tokenPath
            });

            // Initialize connection
            await this.client.initialize();
            this.connected = true;
            console.log('Connected to Charles Schwab API');
            return true;
        } catch (error) {
            console.error('Failed to connect to Schwab:', error);
            return false;
        }
    }

    async getAccountInfo() {
        if (!this.connected) return {};
        try {
            const accounts = await this.client.getAccounts();
            return accounts[0] || {};
        } catch (error) {
            console.error('Error getting account info:', error);
            return {};
        }
    }

    async getPositions() {
        if (!this.connected) return [];
        try {
            const accounts = await this.client.getAccounts();
            if (!accounts || accounts.length === 0) return [];
            const accountId = accounts[0].accountId;
            const positions = await this.client.getAccountPositions(accountId);
            return positions || [];
        } catch (error) {
            console.error('Error getting positions:', error);
            return [];
        }
    }

    async getMarketData(ticker) {
        if (!this.connected) return { price: 0, indicators: {} };
        try {
            const quote = await this.client.getQuote(ticker);
            const price = parseFloat(quote.lastPrice || 0);

            const indicators = {
                bid: parseFloat(quote.bidPrice || 0),
                ask: parseFloat(quote.askPrice || 0),
                volume: parseInt(quote.totalVolume || 0),
                high: parseFloat(quote.highPrice || 0),
                low: parseFloat(quote.lowPrice || 0)
            };

            return { price, indicators };
        } catch (error) {
            console.error(`Error getting market data for ${ticker}:`, error);
            return { price: 0, indicators: {} };
        }
    }

    async getOptionsChain(ticker, expirationDate = null) {
        if (!this.connected) return [];
        try {
            const optionChain = await this.client.getOptionChain({
                symbol: ticker,
                contractType: 'ALL',
                strikeCount: 10,
                includeQuotes: true
            });
            return optionChain.callExpDateMap || [];
        } catch (error) {
            console.error(`Error getting options chain for ${ticker}:`, error);
            return [];
        }
    }

    async placeOrder(ticker, action, quantity, orderType = 'MARKET', price = null,
                     optionType = null, strike = null, expiration = null) {
        if (!this.connected) return false;
        try {
            const accounts = await this.client.getAccounts();
            if (!accounts || accounts.length === 0) return false;
            const accountId = accounts[0].accountId;

            // Build order
            const order = {
                orderType: orderType,
                session: 'NORMAL',
                duration: 'DAY',
                orderStrategyType: 'SINGLE',
                quantity: quantity
            };

            // Handle options vs stocks/ETFs
            if (optionType) {
                order.complexOrderStrategyType = 'NONE';
                order.orderLegCollection = [{
                    instruction: action,
                    quantity: quantity,
                    instrument: {
                        symbol: ticker,
                        assetType: 'OPTION',
                        putCall: optionType.toUpperCase()
                    }
                }];
            } else {
                order.orderLegCollection = [{
                    instruction: action,
                    quantity: quantity,
                    instrument: {
                        symbol: ticker,
                        assetType: 'EQUITY'
                    }
                }];
            }

            if (orderType === 'LIMIT' && price) {
                order.price = price;
            }

            const result = await this.client.placeOrder(accountId, order);
            console.log('Order placed:', result);
            return true;
        } catch (error) {
            console.error('Error placing order:', error);
            return false;
        }
    }

    async isETF(ticker) {
        if (!this.connected) return false;
        try {
            const instrument = await this.client.searchInstruments(ticker, 'symbol-search');
            if (instrument) {
                return instrument.assetType === 'ETF';
            }
            return false;
        } catch (error) {
            console.error('Error checking ETF status:', error);
            return false;
        }
    }
}

class RobinhoodBroker extends BrokerInterface {
    constructor(config) {
        super();
        this.config = config;
        this.session = null;
        this.connected = false;
    }

    async connect() {
        try {
            // Note: Robinhood doesn't have an official API
            // This is a placeholder implementation
            // You would need to use an unofficial library or implement your own
            console.warn('Robinhood API integration requires unofficial library');
            console.warn('Please use Python version for Robinhood or implement custom integration');
            
            if (!this.config.username || !this.config.password) {
                console.error('Robinhood credentials not configured');
                return false;
            }

            // Placeholder - implement actual connection here
            // This would require reverse engineering Robinhood's API or using an unofficial library
            this.connected = false; // Set to true when implemented
            return false;
        } catch (error) {
            console.error('Failed to connect to Robinhood:', error);
            return false;
        }
    }

    async getAccountInfo() {
        if (!this.connected) return {};
        // Implement Robinhood account info retrieval
        return {};
    }

    async getPositions() {
        if (!this.connected) return [];
        // Implement Robinhood positions retrieval
        return [];
    }

    async getMarketData(ticker) {
        if (!this.connected) return { price: 0, indicators: {} };
        // Implement Robinhood market data retrieval
        return { price: 0, indicators: {} };
    }

    async getOptionsChain(ticker, expirationDate = null) {
        if (!this.connected) return [];
        // Implement Robinhood options chain retrieval
        return [];
    }

    async placeOrder(ticker, action, quantity, orderType = 'MARKET', price = null,
                     optionType = null, strike = null, expiration = null) {
        if (!this.connected) return false;
        // Implement Robinhood order placement
        return false;
    }

    async isETF(ticker) {
        if (!this.connected) return false;
        // Implement ETF check for Robinhood
        return false;
    }
}

// --- CORE LOGIC MODULES ---
function checkWashSale(ticker, state) {
    /**
     * Returns true if the stock is currently in a Wash Sale 'Cooldown' period.
     * Returns false if it is safe to trade.
     */
    const washLog = state.wash_sale_log || {};

    if (washLog[ticker]) {
        const lastLossDateStr = washLog[ticker];
        const lastLossDate = new Date(lastLossDateStr);
        const now = new Date();

        // Calculate days passed
        const daysPassed = Math.floor((now - lastLossDate) / (1000 * 60 * 60 * 24));

        if (daysPassed < WASH_SALE_DAYS) {
            console.warn(`🚫 [WASH SALE WARNING] ${ticker} is in cooldown. ${WASH_SALE_DAYS - daysPassed} days remaining.`);
            return true; // BLOCKED
        } else {
            // Cooldown over, clean up the log
            delete state.wash_sale_log[ticker];
            saveState(state);
            return false; // SAFE
        }
    }

    return false; // SAFE
}

function analyzeErosion(ticker, currentPrice, avgCost, totalDividends) {
    /**
     * Calculates if capital erosion exceeds dividend gains.
     */
    const capitalLoss = currentPrice - avgCost;
    const netPosition = capitalLoss + totalDividends;

    if (netPosition < 0 && Math.abs(capitalLoss) > (avgCost * MAX_DRAWDOWN_PCT)) {
        return 'SELL_CRITICAL';
    }
    return 'HOLD';
}

async function analyzeOptionsOpportunity(ticker, currentPrice, optionsChain) {
    /**
     * Analyze options chain for trading opportunities
     * Returns object with opportunity details or null
     */
    if (!optionsChain || optionsChain.length === 0) {
        return null;
    }

    // Simple strategy: Look for options with good volume and reasonable premiums
    // This is a placeholder - implement your own options strategy here
    console.log(`Analyzing options for ${ticker}`);
    return null;
}

// --- MAIN CONTROLLER ---
class TradingBot {
    constructor() {
        this.brokers = [];
        this.state = loadState();
        this.initializeBrokers();
    }

    async initializeBrokers() {
        /** Initialize enabled brokers */
        if (BROKERS.schwab.enabled) {
            const schwab = new SchwabBroker(BROKERS.schwab);
            if (await schwab.connect()) {
                this.brokers.push(schwab);
            }
        }

        if (BROKERS.robinhood.enabled) {
            const robinhood = new RobinhoodBroker(BROKERS.robinhood);
            if (await robinhood.connect()) {
                this.brokers.push(robinhood);
            }
        }

        if (this.brokers.length === 0) {
            console.warn('No brokers connected. Please configure at least one broker.');
        }
    }

    async runBotCycle() {
        /** Run one cycle of the trading bot */
        if (this.brokers.length === 0) {
            console.error('No brokers available');
            return;
        }

        const broker = this.brokers[0]; // Use first available broker

        // 1. THE WATCHLIST LOOP
        for (const ticker of WATCHLIST) {
            console.log(`\n--- Analyzing ${ticker} ---`);

            // 2. CHECK WASH SALE STATUS FIRST
            if (checkWashSale(ticker, this.state)) {
                continue; // Skip this stock, move to the next one
            }

            // 3. GET DATA
            const { price, indicators } = await broker.getMarketData(ticker);
            if (price === 0) {
                console.warn(`Could not get price data for ${ticker}`);
                continue;
            }

            // 4. GET POSITION DATA
            const positions = await broker.getPositions();
            const positionData = positions.find(p => 
                (p.symbol || p.instrument?.symbol || '').toUpperCase() === ticker.toUpperCase()
            );

            if (positionData) {
                // We have a position, analyze it
                const avgCost = parseFloat(positionData.average_price || positionData.average_buy_price || 0);
                const quantity = parseInt(positionData.quantity || positionData.shares || 0);
                const dividends = parseFloat(positionData.dividends || 0);

                const decision = analyzeErosion(ticker, price, avgCost, dividends);

                // 5. EXECUTION & LOGGING
                if (decision === 'SELL_CRITICAL') {
                    const success = await broker.placeOrder(ticker, 'SELL', quantity);
                    if (success) {
                        // MARK AS WASH SALE RISK
                        this.state.wash_sale_log = this.state.wash_sale_log || {};
                        this.state.wash_sale_log[ticker] = new Date().toISOString().split('T')[0];
                        saveState(this.state);
                        console.log(`⚠️ ${ticker} logged for Wash Sale Cooldown.`);
                    }
                } else if (decision === 'HOLD') {
                    console.log(`✅ ${ticker} is holding steady.`);
                }
            } else {
                console.log(`📊 ${ticker} - No position, monitoring price: $${price.toFixed(2)}`);
            }
        }

        // 6. OPTIONS ANALYSIS
        for (const ticker of OPTIONS_WATCHLIST) {
            console.log(`\n--- Analyzing Options for ${ticker} ---`);
            const { price } = await broker.getMarketData(ticker);
            if (price > 0) {
                const optionsChain = await broker.getOptionsChain(ticker);
                const opportunity = await analyzeOptionsOpportunity(ticker, price, optionsChain);
                if (opportunity) {
                    console.log(`🎯 Options opportunity found for ${ticker}:`, opportunity);
                }
            }
        }

        console.log('\n✅ Cycle Complete. Sleeping...');
    }

    async start() {
        /** Main entry point */
        if (this.brokers.length === 0) {
            console.error('Cannot start bot without any connected brokers.');
            console.log('Please configure broker credentials in environment variables or .env file');
            return;
        }

        console.log('Starting trading bot...');
        console.log(`Environment: ${ENVIRONMENT}`);
        console.log(`Watching: ${WATCHLIST.join(', ')}`);
        console.log(`Options watchlist: ${OPTIONS_WATCHLIST.join(', ')}`);
        console.log(`Cycle interval: ${CYCLE_INTERVAL_SECONDS} seconds`);

        // Run initial cycle
        await this.runBotCycle();

        // Set up interval based on configured cycle interval
        setInterval(async () => {
            try {
                await this.runBotCycle();
            } catch (error) {
                console.error('Error in bot cycle:', error);
            }
        }, CYCLE_INTERVAL_SECONDS * 1000); // Convert seconds to milliseconds
    }
}

// --- MAIN EXECUTION ---
if (require.main === module) {
    const bot = new TradingBot();
    bot.start().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });

    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.log('\nBot stopped by user');
        process.exit(0);
    });
}

module.exports = { TradingBot, SchwabBroker, RobinhoodBroker };

