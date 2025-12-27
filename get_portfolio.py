#!/usr/bin/env python3
"""
Portfolio Summary Script
Displays comprehensive portfolio information from your broker
"""

import os
import sys
import json
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    
    env = os.getenv('ENVIRONMENT', 'local').lower()
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv('.env')
except ImportError:
    pass
except Exception as e:
    print(f"Warning: Error loading .env file: {e}")

from trading_bot import TradingBot, BROKERS

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_percent(value):
    """Format value as percentage"""
    color = Colors.GREEN if value >= 0 else Colors.RED
    sign = "+" if value >= 0 else ""
    return f"{color}{sign}{value:.2f}%{Colors.RESET}"

def print_portfolio_summary(summary, broker_name):
    """Print formatted portfolio summary"""
    if not summary:
        print(f"{Colors.RED}✗ Could not retrieve portfolio summary{Colors.RESET}")
        return
    
    print_header(f"{broker_name} Portfolio Summary")
    
    # Account Info
    print(f"{Colors.BOLD}Account Information:{Colors.RESET}")
    print(f"  Account ID: {summary.get('account_id', 'N/A')}")
    print(f"  Account Type: {summary.get('account_type', 'N/A')}")
    print()
    
    # Portfolio Totals
    print(f"{Colors.BOLD}Portfolio Totals:{Colors.RESET}")
    total_value = summary.get('total_value', 0)
    cash_balance = summary.get('cash_balance', 0)
    total_equity = summary.get('total_equity', 0)
    
    print(f"  Total Portfolio Value: {Colors.BOLD}{format_currency(total_value)}{Colors.RESET}")
    print(f"  Cash Balance: {format_currency(cash_balance)}")
    print(f"  Total Equity: {format_currency(total_equity)}")
    print()
    
    # Performance Summary
    print(f"{Colors.BOLD}Performance Summary:{Colors.RESET}")
    total_cost_basis = summary.get('total_cost_basis', 0)
    total_current_value = summary.get('total_current_value', 0)
    total_gain_loss = summary.get('total_gain_loss', 0)
    total_gain_loss_pct = summary.get('total_gain_loss_pct', 0)
    
    print(f"  Total Cost Basis: {format_currency(total_cost_basis)}")
    print(f"  Current Value: {format_currency(total_current_value)}")
    print(f"  Total Gain/Loss: {format_currency(total_gain_loss)} ({format_percent(total_gain_loss_pct)})")
    print()
    
    # Positions
    positions = summary.get('positions', [])
    positions_count = summary.get('positions_count', 0)
    
    print(f"{Colors.BOLD}Positions ({positions_count}):{Colors.RESET}")
    print()
    
    if positions:
        # Header
        print(f"{'Symbol':<10} {'Qty':>10} {'Avg Price':>12} {'Current':>12} {'Cost Basis':>14} {'Value':>12} {'Gain/Loss':>14} {'%':>10}")
        print("-" * 100)
        
        # Sort by current value (descending)
        sorted_positions = sorted(positions, key=lambda x: x.get('current_value', 0), reverse=True)
        
        for pos in sorted_positions:
            symbol = pos.get('symbol', 'N/A')
            quantity = pos.get('quantity', 0)
            avg_price = pos.get('average_price', 0)
            current_price = pos.get('current_price', 0)
            cost_basis = pos.get('cost_basis', 0)
            current_value = pos.get('current_value', 0)
            gain_loss = pos.get('gain_loss', 0)
            gain_loss_pct = pos.get('gain_loss_pct', 0)
            
            print(f"{symbol:<10} {quantity:>10.2f} {format_currency(avg_price):>12} "
                  f"{format_currency(current_price):>12} {format_currency(cost_basis):>14} "
                  f"{format_currency(current_value):>12} {format_currency(gain_loss):>14} "
                  f"{format_percent(gain_loss_pct):>10}")
        
        print("-" * 100)
        
        # Totals row
        print(f"{'TOTALS':<10} {'':>10} {'':>12} {'':>12} "
              f"{format_currency(total_cost_basis):>14} {format_currency(total_current_value):>12} "
              f"{format_currency(total_gain_loss):>14} {format_percent(total_gain_loss_pct):>10}")
    else:
        print(f"  {Colors.YELLOW}No positions found{Colors.RESET}")
    
    print()

def main():
    """Main function"""
    print_header("Portfolio Summary Tool")
    
    env = os.getenv('ENVIRONMENT', 'local').lower()
    print(f"{Colors.BLUE}Environment: {env}{Colors.RESET}\n")
    
    # Initialize bot
    bot = TradingBot()
    
    if not bot.brokers:
        print(f"{Colors.RED}✗ No brokers connected{Colors.RESET}")
        print("Please configure broker credentials in your .env file")
        sys.exit(1)
    
    # Get portfolio summary from each connected broker
    for broker in bot.brokers:
        broker_name = "Charles Schwab" if isinstance(broker, type(bot.brokers[0])) and 'Schwab' in str(type(broker)) else "Robinhood"
        
        if 'Schwab' in str(type(broker)):
            broker_name = "Charles Schwab"
        elif 'Robinhood' in str(type(broker)):
            broker_name = "Robinhood"
        else:
            broker_name = str(type(broker).__name__)
        
        print(f"{Colors.BLUE}Retrieving portfolio from {broker_name}...{Colors.RESET}")
        summary = broker.get_portfolio_summary()
        
        if summary:
            print_portfolio_summary(summary, broker_name)
            
            # Optionally save to JSON
            if '--json' in sys.argv or '-j' in sys.argv:
                output_file = f"portfolio_summary_{env}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w') as f:
                    json.dump(summary, f, indent=2)
                print(f"{Colors.GREEN}✓ Portfolio summary saved to {output_file}{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Failed to retrieve portfolio summary{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}✓ Portfolio summary complete{Colors.RESET}")

if __name__ == "__main__":
    main()

