#!/usr/bin/env python3
"""
Connection Test Script for Trading Bot
Tests connectivity to Charles Schwab and Robinhood brokers
"""

import os
import sys
from typing import Dict, List, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Determine environment (defaults to 'local')
    env = os.getenv('ENVIRONMENT', 'local').lower()
    
    # Load environment-specific .env file
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✓ Loaded environment from {env_file}")
    else:
        # Fallback to .env if environment-specific file doesn't exist
        load_dotenv('.env')
        print("✓ Loaded environment from .env")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Import broker classes from trading_bot
from trading_bot import SchwabBroker, RobinhoodBroker, BROKERS

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_header(message: str):
    """Print header message"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def test_schwab_connection() -> Tuple[bool, Dict]:
    """Test Charles Schwab connection"""
    print_header("Testing Charles Schwab Connection")
    
    config = BROKERS['schwab']
    
    # Check if enabled
    if not config['enabled']:
        print_warning("Schwab is not enabled in configuration")
        print_info("Set SCHWAB_ENABLED=true in your .env file to test")
        return False, {}
    
    # Check credentials
    if not config['api_key'] or not config['app_secret']:
        print_error("Schwab API credentials not configured")
        print_info("Set SCHWAB_API_KEY and SCHWAB_APP_SECRET in your .env file")
        return False, {}
    
    print_info(f"API Key: {config['api_key'][:10]}... (hidden)")
    print_info(f"Callback URL: {config['callback_url']}")
    print_info(f"Token Path: {config['token_path']}")
    
    # Test connection
    try:
        broker = SchwabBroker(config)
        print_info("Attempting to connect to Charles Schwab API...")
        
        if broker.connect():
            print_success("Successfully connected to Charles Schwab API")
            
            # Test account info retrieval
            print_info("Testing account information retrieval...")
            account_info = broker.get_account_info()
            
            if account_info:
                print_success("Successfully retrieved account information")
                account_id = account_info.get('accountId', 'N/A')
                account_type = account_info.get('type', 'N/A')
                print_info(f"  Account ID: {account_id}")
                print_info(f"  Account Type: {account_type}")
                
                # Test positions retrieval
                print_info("Testing positions retrieval...")
                positions = broker.get_positions()
                print_success(f"Successfully retrieved {len(positions)} positions")
                
                # Test market data retrieval
                print_info("Testing market data retrieval (SPY)...")
                price, indicators = broker.get_market_data('SPY')
                if price > 0:
                    print_success(f"Successfully retrieved market data for SPY: ${price:.2f}")
                    print_info(f"  Bid: ${indicators.get('bid', 0):.2f}")
                    print_info(f"  Ask: ${indicators.get('ask', 0):.2f}")
                    print_info(f"  Volume: {indicators.get('volume', 0):,}")
                else:
                    print_warning("Market data retrieval returned no price")
                
                return True, {
                    'account_id': account_id,
                    'account_type': account_type,
                    'positions_count': len(positions),
                    'market_data_working': price > 0
                }
            else:
                print_warning("Connected but could not retrieve account information")
                return True, {'account_info': False}
        else:
            print_error("Failed to connect to Charles Schwab API")
            return False, {}
            
    except Exception as e:
        print_error(f"Error testing Schwab connection: {e}")
        import traceback
        print_info("Full error details:")
        traceback.print_exc()
        return False, {}

def test_robinhood_connection() -> Tuple[bool, Dict]:
    """Test Robinhood connection"""
    print_header("Testing Robinhood Connection")
    
    config = BROKERS['robinhood']
    
    # Check if enabled
    if not config['enabled']:
        print_warning("Robinhood is not enabled in configuration")
        print_info("Set ROBINHOOD_ENABLED=true in your .env file to test")
        return False, {}
    
    # Check credentials
    if not config['username'] or not config['password']:
        print_error("Robinhood credentials not configured")
        print_info("Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in your .env file")
        return False, {}
    
    print_info(f"Username: {config['username']}")
    print_info("Password: *** (hidden)")
    if config.get('mfa_code'):
        print_info("MFA Code: *** (hidden)")
    
    # Test connection
    try:
        broker = RobinhoodBroker(config)
        print_info("Attempting to connect to Robinhood API...")
        
        if broker.connect():
            print_success("Successfully connected to Robinhood API")
            
            # Test account info retrieval
            print_info("Testing account information retrieval...")
            account_info = broker.get_account_info()
            
            if account_info:
                print_success("Successfully retrieved account information")
                username = account_info.get('username', 'N/A')
                print_info(f"  Username: {username}")
                
                # Test positions retrieval
                print_info("Testing positions retrieval...")
                positions = broker.get_positions()
                print_success(f"Successfully retrieved {len(positions)} positions")
                
                # Test market data retrieval
                print_info("Testing market data retrieval (SPY)...")
                price, indicators = broker.get_market_data('SPY')
                if price > 0:
                    print_success(f"Successfully retrieved market data for SPY: ${price:.2f}")
                    print_info(f"  Bid: ${indicators.get('bid', 0):.2f}")
                    print_info(f"  Ask: ${indicators.get('ask', 0):.2f}")
                    print_info(f"  Volume: {indicators.get('volume', 0):,}")
                else:
                    print_warning("Market data retrieval returned no price")
                
                return True, {
                    'username': username,
                    'positions_count': len(positions),
                    'market_data_working': price > 0
                }
            else:
                print_warning("Connected but could not retrieve account information")
                return True, {'account_info': False}
        else:
            print_error("Failed to connect to Robinhood API")
            print_info("Check your username, password, and MFA code if enabled")
            return False, {}
            
    except Exception as e:
        print_error(f"Error testing Robinhood connection: {e}")
        import traceback
        print_info("Full error details:")
        traceback.print_exc()
        return False, {}

def main():
    """Main test function"""
    print_header("Trading Bot Connection Test")
    
    env = os.getenv('ENVIRONMENT', 'local').lower()
    print_info(f"Environment: {env}")
    print_info(f"Testing brokers based on configuration...\n")
    
    results = {
        'schwab': {'success': False, 'details': {}},
        'robinhood': {'success': False, 'details': {}}
    }
    
    # Test Schwab
    schwab_success, schwab_details = test_schwab_connection()
    results['schwab'] = {'success': schwab_success, 'details': schwab_details}
    
    # Test Robinhood
    robinhood_success, robinhood_details = test_robinhood_connection()
    results['robinhood'] = {'success': robinhood_success, 'details': robinhood_details}
    
    # Print summary
    print_header("Test Summary")
    
    if results['schwab']['success']:
        print_success("Charles Schwab: CONNECTED ✓")
        if results['schwab']['details']:
            details = results['schwab']['details']
            print_info(f"  Account ID: {details.get('account_id', 'N/A')}")
            print_info(f"  Positions: {details.get('positions_count', 0)}")
            print_info(f"  Market Data: {'Working' if details.get('market_data_working') else 'Not Working'}")
    else:
        if BROKERS['schwab']['enabled']:
            print_error("Charles Schwab: FAILED ✗")
        else:
            print_warning("Charles Schwab: DISABLED (not configured)")
    
    if results['robinhood']['success']:
        print_success("Robinhood: CONNECTED ✓")
        if results['robinhood']['details']:
            details = results['robinhood']['details']
            print_info(f"  Username: {details.get('username', 'N/A')}")
            print_info(f"  Positions: {details.get('positions_count', 0)}")
            print_info(f"  Market Data: {'Working' if details.get('market_data_working') else 'Not Working'}")
    else:
        if BROKERS['robinhood']['enabled']:
            print_error("Robinhood: FAILED ✗")
        else:
            print_warning("Robinhood: DISABLED (not configured)")
    
    # Exit code
    if results['schwab']['success'] or results['robinhood']['success']:
        print_success("\n✓ At least one broker connection successful!")
        sys.exit(0)
    else:
        print_error("\n✗ No broker connections successful. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()

