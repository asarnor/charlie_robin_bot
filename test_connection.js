#!/usr/bin/env node
/**
 * Connection Test Script for Trading Bot
 * Tests connectivity to Charles Schwab and Robinhood brokers
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
    console.log(`✓ Loaded environment from ${envFile}`);
} else {
    // Fallback to .env if environment-specific file doesn't exist
    require('dotenv').config();
    console.log('✓ Loaded environment from .env');
}

// Import broker classes from trading_bot
const { SchwabBroker, RobinhoodBroker } = require('./trading_bot');

// Broker configuration
const BROKERS = {
    schwab: {
        enabled: process.env.SCHWAB_ENABLED === 'true',
        apiKey: process.env.SCHWAB_API_KEY || '',
        appSecret: process.env.SCHWAB_APP_SECRET || '',
        callbackUrl: process.env.SCHWAB_CALLBACK_URL || 'https://127.0.0.1:8182/',
        tokenPath: process.env.SCHWAB_TOKEN_PATH || './schwab_token.json',
        accountId: process.env.SCHWAB_ACCOUNT_ID || '',
        baseUrl: process.env.SCHWAB_BASE_URL || ''
    },
    robinhood: {
        enabled: process.env.ROBINHOOD_ENABLED === 'true',
        username: process.env.ROBINHOOD_USERNAME || '',
        password: process.env.ROBINHOOD_PASSWORD || '',
        mfaCode: process.env.ROBINHOOD_MFA_CODE || '',
        apiKey: process.env.ROBINHOOD_API_KEY || '',
        deviceToken: process.env.ROBINHOOD_DEVICE_TOKEN || ''
    }
};

// Color codes for terminal output
const Colors = {
    GREEN: '\x1b[32m',
    RED: '\x1b[31m',
    YELLOW: '\x1b[33m',
    BLUE: '\x1b[34m',
    RESET: '\x1b[0m',
    BOLD: '\x1b[1m'
};

function printSuccess(message) {
    console.log(`${Colors.GREEN}✓ ${message}${Colors.RESET}`);
}

function printError(message) {
    console.log(`${Colors.RED}✗ ${message}${Colors.RESET}`);
}

function printWarning(message) {
    console.log(`${Colors.YELLOW}⚠ ${message}${Colors.RESET}`);
}

function printInfo(message) {
    console.log(`${Colors.BLUE}ℹ ${message}${Colors.RESET}`);
}

function printHeader(message) {
    console.log(`\n${Colors.BOLD}${Colors.BLUE}${'='.repeat(60)}${Colors.RESET}`);
    console.log(`${Colors.BOLD}${Colors.BLUE}${message}${Colors.RESET}`);
    console.log(`${Colors.BOLD}${Colors.BLUE}${'='.repeat(60)}${Colors.RESET}\n`);
}

async function testSchwabConnection() {
    printHeader('Testing Charles Schwab Connection');
    
    const config = BROKERS.schwab;
    
    // Check if enabled
    if (!config.enabled) {
        printWarning('Schwab is not enabled in configuration');
        printInfo('Set SCHWAB_ENABLED=true in your .env file to test');
        return { success: false, details: {} };
    }
    
    // Check credentials
    if (!config.apiKey || !config.appSecret) {
        printError('Schwab API credentials not configured');
        printInfo('Set SCHWAB_API_KEY and SCHWAB_APP_SECRET in your .env file');
        return { success: false, details: {} };
    }
    
    printInfo(`API Key: ${config.apiKey.substring(0, 10)}... (hidden)`);
    printInfo(`Callback URL: ${config.callbackUrl}`);
    printInfo(`Token Path: ${config.tokenPath}`);
    
    // Test connection
    try {
        const broker = new SchwabBroker(config);
        printInfo('Attempting to connect to Charles Schwab API...');
        
        const connected = await broker.connect();
        if (connected) {
            printSuccess('Successfully connected to Charles Schwab API');
            
            // Test account info retrieval
            printInfo('Testing account information retrieval...');
            const accountInfo = await broker.getAccountInfo();
            
            if (accountInfo && Object.keys(accountInfo).length > 0) {
                printSuccess('Successfully retrieved account information');
                const accountId = accountInfo.accountId || 'N/A';
                const accountType = accountInfo.type || 'N/A';
                printInfo(`  Account ID: ${accountId}`);
                printInfo(`  Account Type: ${accountType}`);
                
                // Test positions retrieval
                printInfo('Testing positions retrieval...');
                const positions = await broker.getPositions();
                printSuccess(`Successfully retrieved ${positions.length} positions`);
                
                // Test market data retrieval
                printInfo('Testing market data retrieval (SPY)...');
                const { price, indicators } = await broker.getMarketData('SPY');
                if (price > 0) {
                    printSuccess(`Successfully retrieved market data for SPY: $${price.toFixed(2)}`);
                    printInfo(`  Bid: $${(indicators.bid || 0).toFixed(2)}`);
                    printInfo(`  Ask: $${(indicators.ask || 0).toFixed(2)}`);
                    printInfo(`  Volume: ${(indicators.volume || 0).toLocaleString()}`);
                } else {
                    printWarning('Market data retrieval returned no price');
                }
                
                return {
                    success: true,
                    details: {
                        accountId,
                        accountType,
                        positionsCount: positions.length,
                        marketDataWorking: price > 0
                    }
                };
            } else {
                printWarning('Connected but could not retrieve account information');
                return { success: true, details: { accountInfo: false } };
            }
        } else {
            printError('Failed to connect to Charles Schwab API');
            return { success: false, details: {} };
        }
    } catch (error) {
        printError(`Error testing Schwab connection: ${error.message}`);
        printInfo('Full error details:');
        console.error(error);
        return { success: false, details: {} };
    }
}

async function testRobinhoodConnection() {
    printHeader('Testing Robinhood Connection');
    
    const config = BROKERS.robinhood;
    
    // Check if enabled
    if (!config.enabled) {
        printWarning('Robinhood is not enabled in configuration');
        printInfo('Set ROBINHOOD_ENABLED=true in your .env file to test');
        return { success: false, details: {} };
    }
    
    // Check credentials
    if (!config.username || !config.password) {
        printError('Robinhood credentials not configured');
        printInfo('Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in your .env file');
        return { success: false, details: {} };
    }
    
    printInfo(`Username: ${config.username}`);
    printInfo('Password: *** (hidden)');
    if (config.mfaCode) {
        printInfo('MFA Code: *** (hidden)');
    }
    
    // Test connection
    try {
        const broker = new RobinhoodBroker(config);
        printInfo('Attempting to connect to Robinhood API...');
        
        const connected = await broker.connect();
        if (connected) {
            printSuccess('Successfully connected to Robinhood API');
            
            // Test account info retrieval
            printInfo('Testing account information retrieval...');
            const accountInfo = await broker.getAccountInfo();
            
            if (accountInfo && Object.keys(accountInfo).length > 0) {
                printSuccess('Successfully retrieved account information');
                const username = accountInfo.username || 'N/A';
                printInfo(`  Username: ${username}`);
                
                // Test positions retrieval
                printInfo('Testing positions retrieval...');
                const positions = await broker.getPositions();
                printSuccess(`Successfully retrieved ${positions.length} positions`);
                
                // Test market data retrieval
                printInfo('Testing market data retrieval (SPY)...');
                const { price, indicators } = await broker.getMarketData('SPY');
                if (price > 0) {
                    printSuccess(`Successfully retrieved market data for SPY: $${price.toFixed(2)}`);
                    printInfo(`  Bid: $${(indicators.bid || 0).toFixed(2)}`);
                    printInfo(`  Ask: $${(indicators.ask || 0).toFixed(2)}`);
                    printInfo(`  Volume: ${(indicators.volume || 0).toLocaleString()}`);
                } else {
                    printWarning('Market data retrieval returned no price');
                }
                
                return {
                    success: true,
                    details: {
                        username,
                        positionsCount: positions.length,
                        marketDataWorking: price > 0
                    }
                };
            } else {
                printWarning('Connected but could not retrieve account information');
                return { success: true, details: { accountInfo: false } };
            }
        } else {
            printError('Failed to connect to Robinhood API');
            printInfo('Check your username, password, and MFA code if enabled');
            return { success: false, details: {} };
        }
    } catch (error) {
        printError(`Error testing Robinhood connection: ${error.message}`);
        printInfo('Full error details:');
        console.error(error);
        return { success: false, details: {} };
    }
}

async function main() {
    printHeader('Trading Bot Connection Test');
    
    const env = (process.env.ENVIRONMENT || 'local').toLowerCase();
    printInfo(`Environment: ${env}`);
    printInfo('Testing brokers based on configuration...\n');
    
    const results = {
        schwab: { success: false, details: {} },
        robinhood: { success: false, details: {} }
    };
    
    // Test Schwab
    const schwabResult = await testSchwabConnection();
    results.schwab = schwabResult;
    
    // Test Robinhood
    const robinhoodResult = await testRobinhoodConnection();
    results.robinhood = robinhoodResult;
    
    // Print summary
    printHeader('Test Summary');
    
    if (results.schwab.success) {
        printSuccess('Charles Schwab: CONNECTED ✓');
        if (results.schwab.details && Object.keys(results.schwab.details).length > 0) {
            const details = results.schwab.details;
            printInfo(`  Account ID: ${details.accountId || 'N/A'}`);
            printInfo(`  Positions: ${details.positionsCount || 0}`);
            printInfo(`  Market Data: ${details.marketDataWorking ? 'Working' : 'Not Working'}`);
        }
    } else {
        if (BROKERS.schwab.enabled) {
            printError('Charles Schwab: FAILED ✗');
        } else {
            printWarning('Charles Schwab: DISABLED (not configured)');
        }
    }
    
    if (results.robinhood.success) {
        printSuccess('Robinhood: CONNECTED ✓');
        if (results.robinhood.details && Object.keys(results.robinhood.details).length > 0) {
            const details = results.robinhood.details;
            printInfo(`  Username: ${details.username || 'N/A'}`);
            printInfo(`  Positions: ${details.positionsCount || 0}`);
            printInfo(`  Market Data: ${details.marketDataWorking ? 'Working' : 'Not Working'}`);
        }
    } else {
        if (BROKERS.robinhood.enabled) {
            printError('Robinhood: FAILED ✗');
        } else {
            printWarning('Robinhood: DISABLED (not configured)');
        }
    }
    
    // Exit code
    if (results.schwab.success || results.robinhood.success) {
        printSuccess('\n✓ At least one broker connection successful!');
        process.exit(0);
    } else {
        printError('\n✗ No broker connections successful. Please check your configuration.');
        process.exit(1);
    }
}

// Run tests
main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});

