"""
Trading Bot for ETFs and Options
Supports Charles Schwab and Robinhood
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging

# Load environment variables from .env file
import os
try:
    from dotenv import load_dotenv
    
    # Determine environment (defaults to 'local')
    env = os.getenv('ENVIRONMENT', 'local').lower()
    
    # Load environment-specific .env file
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
    else:
        # Fallback to .env if environment-specific file doesn't exist
        load_dotenv('.env')
        print("Loaded environment from .env")
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"Error loading .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Load from environment variables with defaults
WATCHLIST = os.getenv('WATCHLIST', 'SPY,QQQ,TSLA,NVDA').split(',') if os.getenv('WATCHLIST') else ['SPY', 'QQQ', 'TSLA', 'NVDA']
OPTIONS_WATCHLIST = os.getenv('OPTIONS_WATCHLIST', 'SPY,QQQ').split(',') if os.getenv('OPTIONS_WATCHLIST') else ['SPY', 'QQQ']
MAX_DRAWDOWN_PCT = float(os.getenv('MAX_DRAWDOWN_PCT', '0.10'))
WASH_SALE_DAYS = int(os.getenv('WASH_SALE_DAYS', '31'))
LOG_FILE = os.getenv('LOG_FILE', 'bot_state.json')
CYCLE_INTERVAL_SECONDS = int(os.getenv('CYCLE_INTERVAL_SECONDS', '900'))  # 15 minutes default
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local').lower()

# Broker configuration
BROKERS = {
    'schwab': {
        'enabled': os.getenv('SCHWAB_ENABLED', 'false').lower() == 'true',
        'api_key': os.getenv('SCHWAB_API_KEY', ''),
        'app_secret': os.getenv('SCHWAB_APP_SECRET', ''),
        'callback_url': os.getenv('SCHWAB_CALLBACK_URL', 'https://127.0.0.1:8182/'),
        'token_path': os.getenv('SCHWAB_TOKEN_PATH', './schwab_token.json'),
        'account_id': os.getenv('SCHWAB_ACCOUNT_ID', ''),  # Optional: specific account ID
        'base_url': os.getenv('SCHWAB_BASE_URL', ''),  # Optional: for sandbox/production URLs
    },
    'robinhood': {
        'enabled': os.getenv('ROBINHOOD_ENABLED', 'false').lower() == 'true',
        'username': os.getenv('ROBINHOOD_USERNAME', ''),
        'password': os.getenv('ROBINHOOD_PASSWORD', ''),
        'mfa_code': os.getenv('ROBINHOOD_MFA_CODE', ''),
        'api_key': os.getenv('ROBINHOOD_API_KEY', ''),  # If using API key instead of username/password
        'device_token': os.getenv('ROBINHOOD_DEVICE_TOKEN', ''),  # Device token for authentication
    }
}


# --- STATE MANAGEMENT ---
def load_state():
    """Load bot state from JSON file"""
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"wash_sale_log": {}, "positions": {}}


def save_state(state):
    """Save bot state to JSON file"""
    with open(LOG_FILE, 'w') as f:
        json.dump(state, f, indent=4)


# --- BROKER INTERFACE ---
class BrokerInterface(ABC):
    """Abstract base class for broker implementations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_market_data(self, ticker: str) -> Tuple[float, Dict]:
        """Get current price and technical indicators"""
        pass
    
    @abstractmethod
    def get_options_chain(self, ticker: str, expiration_date: Optional[str] = None) -> List[Dict]:
        """Get options chain for a ticker"""
        pass
    
    @abstractmethod
    def place_order(self, ticker: str, action: str, quantity: int, 
                   order_type: str = 'MARKET', price: Optional[float] = None,
                   option_type: Optional[str] = None, strike: Optional[float] = None,
                   expiration: Optional[str] = None) -> bool:
        """Place a trade order"""
        pass
    
    @abstractmethod
    def is_etf(self, ticker: str) -> bool:
        """Check if ticker is an ETF"""
        pass


class SchwabBroker(BrokerInterface):
    """Charles Schwab broker implementation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Schwab API"""
        try:
            # Try to import schwab-py library
            try:
                from schwab import auth
            except ImportError:
                logger.error("schwab-py library not installed. Install with: pip install schwab-py")
                return False
            
            if not self.config['api_key'] or not self.config['app_secret']:
                logger.error("Schwab API credentials not configured")
                return False
            
            self.client = auth.easy_client(
                self.config['api_key'],
                self.config['app_secret'],
                self.config['callback_url'],
                self.config['token_path']
            )
            self.connected = True
            logger.info("Connected to Charles Schwab API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Schwab: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            return {}
        try:
            accounts = self.client.get_accounts()
            return accounts[0] if accounts else {}
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.connected:
            return []
        try:
            accounts = self.client.get_accounts()
            if not accounts:
                return []
            account_id = accounts[0].get('accountId')
            positions = self.client.get_account_positions(account_id)
            return positions if positions else []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_market_data(self, ticker: str) -> Tuple[float, Dict]:
        """Get current price and technical indicators"""
        if not self.connected:
            return 0.0, {}
        try:
            quote = self.client.get_quote(ticker)
            price = float(quote.get('lastPrice', 0))
            
            # Get additional market data for indicators
            indicators = {
                'bid': float(quote.get('bidPrice', 0)),
                'ask': float(quote.get('askPrice', 0)),
                'volume': int(quote.get('totalVolume', 0)),
                'high': float(quote.get('highPrice', 0)),
                'low': float(quote.get('lowPrice', 0))
            }
            
            return price, indicators
        except Exception as e:
            logger.error(f"Error getting market data for {ticker}: {e}")
            return 0.0, {}
    
    def get_options_chain(self, ticker: str, expiration_date: Optional[str] = None) -> List[Dict]:
        """Get options chain for a ticker"""
        if not self.connected:
            return []
        try:
            # Get option chain
            option_chain = self.client.get_option_chain(
                ticker,
                contract_type='ALL',
                strike_count=10,
                include_quotes=True
            )
            return option_chain.get('callExpDateMap', {}) if option_chain else []
        except Exception as e:
            logger.error(f"Error getting options chain for {ticker}: {e}")
            return []
    
    def place_order(self, ticker: str, action: str, quantity: int,
                   order_type: str = 'MARKET', price: Optional[float] = None,
                   option_type: Optional[str] = None, strike: Optional[float] = None,
                   expiration: Optional[str] = None) -> bool:
        """Place a trade order"""
        if not self.connected:
            return False
        try:
            accounts = self.client.get_accounts()
            if not accounts:
                return False
            account_id = accounts[0].get('accountId')
            
            # Build order
            order = {
                'orderType': order_type,
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'quantity': quantity
            }
            
            # Handle options vs stocks/ETFs
            if option_type:
                # Options order
                order['complexOrderStrategyType'] = 'NONE'
                order['orderLegCollection'] = [{
                    'instruction': action,
                    'quantity': quantity,
                    'instrument': {
                        'symbol': ticker,
                        'assetType': 'OPTION',
                        'putCall': option_type.upper()
                    }
                }]
            else:
                # Stock/ETF order
                order['orderLegCollection'] = [{
                    'instruction': action,
                    'quantity': quantity,
                    'instrument': {
                        'symbol': ticker,
                        'assetType': 'EQUITY'
                    }
                }]
            
            if order_type == 'LIMIT' and price:
                order['price'] = price
            
            result = self.client.place_order(account_id, order)
            logger.info(f"Order placed: {result}")
            return True
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    def is_etf(self, ticker: str) -> bool:
        """Check if ticker is an ETF"""
        if not self.connected:
            return False
        try:
            instrument = self.client.search_instruments(ticker, projection='symbol-search')
            if instrument:
                asset_type = instrument.get('assetType', '')
                return asset_type == 'ETF'
            return False
        except Exception as e:
            logger.error(f"Error checking ETF status: {e}")
            return False


class RobinhoodBroker(BrokerInterface):
    """Robinhood broker implementation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Robinhood API"""
        try:
            # Try to import robin_stocks library
            try:
                import robin_stocks.robinhood as rh
                self.rh = rh
            except ImportError:
                logger.error("robin_stocks library not installed. Install with: pip install robin_stocks")
                return False
            
            if not self.config['username'] or not self.config['password']:
                logger.error("Robinhood credentials not configured")
                return False
            
            # Login
            login_result = self.rh.login(
                username=self.config['username'],
                password=self.config['password'],
                mfa_code=self.config.get('mfa_code')
            )
            
            if login_result:
                self.connected = True
                logger.info("Connected to Robinhood API")
                return True
            else:
                logger.error("Failed to login to Robinhood")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Robinhood: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            return {}
        try:
            account_info = self.rh.load_account_profile()
            return account_info if account_info else {}
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.connected:
            return []
        try:
            positions = self.rh.get_open_stock_positions()
            return positions if positions else []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_market_data(self, ticker: str) -> Tuple[float, Dict]:
        """Get current price and technical indicators"""
        if not self.connected:
            return 0.0, {}
        try:
            quote = self.rh.get_quotes(ticker)
            if not quote:
                return 0.0, {}
            
            price_data = quote[0] if isinstance(quote, list) else quote
            price = float(price_data.get('last_trade_price', 0))
            
            indicators = {
                'bid': float(price_data.get('bid_price', 0)),
                'ask': float(price_data.get('ask_price', 0)),
                'volume': int(price_data.get('volume', 0)),
                'high': float(price_data.get('high_price', 0)),
                'low': float(price_data.get('low_price', 0))
            }
            
            return price, indicators
        except Exception as e:
            logger.error(f"Error getting market data for {ticker}: {e}")
            return 0.0, {}
    
    def get_options_chain(self, ticker: str, expiration_date: Optional[str] = None) -> List[Dict]:
        """Get options chain for a ticker"""
        if not self.connected:
            return []
        try:
            # Get option chain
            option_chain = self.rh.get_option_chain(ticker)
            return option_chain if option_chain else []
        except Exception as e:
            logger.error(f"Error getting options chain for {ticker}: {e}")
            return []
    
    def place_order(self, ticker: str, action: str, quantity: int,
                   order_type: str = 'MARKET', price: Optional[float] = None,
                   option_type: Optional[str] = None, strike: Optional[float] = None,
                   expiration: Optional[str] = None) -> bool:
        """Place a trade order"""
        if not self.connected:
            return False
        try:
            if option_type:
                # Options order
                result = self.rh.order_buy_option_limit(
                    positionEffect='open',
                    creditOrDebit='debit',
                    price=price or 0.01,
                    symbol=ticker,
                    quantity=quantity,
                    expirationDate=expiration,
                    strike=strike,
                    optionType=option_type.lower()
                ) if action == 'BUY' else self.rh.order_sell_option_limit(
                    positionEffect='close',
                    creditOrDebit='credit',
                    price=price or 0.01,
                    symbol=ticker,
                    quantity=quantity,
                    expirationDate=expiration,
                    strike=strike,
                    optionType=option_type.lower()
                )
            else:
                # Stock/ETF order
                if action == 'BUY':
                    if order_type == 'LIMIT' and price:
                        result = self.rh.order_buy_limit(ticker, quantity, price)
                    else:
                        result = self.rh.order_buy_market(ticker, quantity)
                else:
                    if order_type == 'LIMIT' and price:
                        result = self.rh.order_sell_limit(ticker, quantity, price)
                    else:
                        result = self.rh.order_sell_market(ticker, quantity)
            
            logger.info(f"Order placed: {result}")
            return result is not None
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    def is_etf(self, ticker: str) -> bool:
        """Check if ticker is an ETF"""
        if not self.connected:
            return False
        try:
            instrument = self.rh.get_instruments_by_symbols(ticker)
            if instrument and len(instrument) > 0:
                return instrument[0].get('type', '').upper() == 'ETF'
            return False
        except Exception as e:
            logger.error(f"Error checking ETF status: {e}")
            return False


# --- CORE LOGIC MODULES ---
def check_wash_sale(ticker: str, state: Dict) -> bool:
    """
    Returns True if the stock is currently in a Wash Sale 'Cooldown' period.
    Returns False if it is safe to trade.
    """
    wash_log = state.get("wash_sale_log", {})
    
    if ticker in wash_log:
        last_loss_date_str = wash_log[ticker]
        last_loss_date = datetime.strptime(last_loss_date_str, "%Y-%m-%d")
        
        # Calculate days passed
        days_passed = (datetime.now() - last_loss_date).days
        
        if days_passed < WASH_SALE_DAYS:
            logger.warning(f"🚫 [WASH SALE WARNING] {ticker} is in cooldown. {WASH_SALE_DAYS - days_passed} days remaining.")
            return True  # BLOCKED
        else:
            # Cooldown over, clean up the log
            del state["wash_sale_log"][ticker]
            save_state(state)
            return False  # SAFE
            
    return False  # SAFE


def analyze_erosion(ticker: str, current_price: float, avg_cost: float, total_dividends: float) -> str:
    """
    Calculates if capital erosion exceeds dividend gains.
    """
    capital_loss = current_price - avg_cost
    net_position = capital_loss + total_dividends
    
    if net_position < 0 and abs(capital_loss) > (avg_cost * MAX_DRAWDOWN_PCT):
        return "SELL_CRITICAL"
    return "HOLD"


def analyze_options_opportunity(ticker: str, current_price: float, options_chain: List[Dict]) -> Optional[Dict]:
    """
    Analyze options chain for trading opportunities
    Returns dict with opportunity details or None
    """
    if not options_chain:
        return None
    
    # Simple strategy: Look for options with good volume and reasonable premiums
    # This is a placeholder - implement your own options strategy here
    logger.info(f"Analyzing options for {ticker}")
    return None


# --- MAIN CONTROLLER ---
class TradingBot:
    """Main trading bot controller"""
    
    def __init__(self):
        self.brokers: List[BrokerInterface] = []
        self.state = load_state()
        self._initialize_brokers()
    
    def _initialize_brokers(self):
        """Initialize enabled brokers"""
        if BROKERS['schwab']['enabled']:
            schwab = SchwabBroker(BROKERS['schwab'])
            if schwab.connect():
                self.brokers.append(schwab)
        
        if BROKERS['robinhood']['enabled']:
            robinhood = RobinhoodBroker(BROKERS['robinhood'])
            if robinhood.connect():
                self.brokers.append(robinhood)
        
        if not self.brokers:
            logger.warning("No brokers connected. Please configure at least one broker.")
    
    def run_bot_cycle(self):
        """Run one cycle of the trading bot"""
        if not self.brokers:
            logger.error("No brokers available")
            return
        
        broker = self.brokers[0]  # Use first available broker
        
        # 1. THE WATCHLIST LOOP
        for ticker in WATCHLIST:
            logger.info(f"\n--- Analyzing {ticker} ---")
            
            # 2. CHECK WASH SALE STATUS FIRST
            if check_wash_sale(ticker, self.state):
                continue  # Skip this stock, move to the next one
            
            # 3. GET DATA
            price, indicators = broker.get_market_data(ticker)
            if price == 0:
                logger.warning(f"Could not get price data for {ticker}")
                continue
            
            # 4. GET POSITION DATA
            positions = broker.get_positions()
            position_data = next((p for p in positions if p.get('symbol', '').upper() == ticker.upper()), None)
            
            if position_data:
                # We have a position, analyze it
                avg_cost = float(position_data.get('average_price', 0))
                quantity = int(position_data.get('quantity', 0))
                dividends = float(position_data.get('dividends', 0))
                
                decision = analyze_erosion(ticker, price, avg_cost, dividends)
                
                # 5. EXECUTION & LOGGING
                if decision == "SELL_CRITICAL":
                    success = broker.place_order(ticker, "SELL", quantity)
                    if success:
                        # MARK AS WASH SALE RISK
                        self.state["wash_sale_log"][ticker] = datetime.now().strftime("%Y-%m-%d")
                        save_state(self.state)
                        logger.info(f"⚠️ {ticker} logged for Wash Sale Cooldown.")
                elif decision == "HOLD":
                    logger.info(f"✅ {ticker} is holding steady.")
            else:
                logger.info(f"📊 {ticker} - No position, monitoring price: ${price:.2f}")
        
        # 6. OPTIONS ANALYSIS
        for ticker in OPTIONS_WATCHLIST:
            logger.info(f"\n--- Analyzing Options for {ticker} ---")
            price, _ = broker.get_market_data(ticker)
            if price > 0:
                options_chain = broker.get_options_chain(ticker)
                opportunity = analyze_options_opportunity(ticker, price, options_chain)
                if opportunity:
                    logger.info(f"🎯 Options opportunity found for {ticker}: {opportunity}")
        
        logger.info("\n✅ Cycle Complete. Sleeping...")


def main():
    """Main entry point"""
    bot = TradingBot()
    
    if not bot.brokers:
        logger.error("Cannot start bot without any connected brokers.")
        logger.info("Please configure broker credentials in environment variables or .env file")
        return
    
    logger.info("Starting trading bot...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Watching: {WATCHLIST}")
    logger.info(f"Options watchlist: {OPTIONS_WATCHLIST}")
    logger.info(f"Cycle interval: {CYCLE_INTERVAL_SECONDS} seconds")
    
    while True:
        try:
            bot.run_bot_cycle()
            # Sleep based on configured interval to respect API limits and not over-trade
            time.sleep(CYCLE_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in bot cycle: {e}")
            time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    main()

