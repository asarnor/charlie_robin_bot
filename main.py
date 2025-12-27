import time
import json
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WATCHLIST = ['ULTY', 'TSLA', 'NVDA'] # Add your tickers here
MAX_DRAWDOWN_PCT = 0.10  # Sell if loss > 10%
WASH_SALE_DAYS = 31      # IRS rule is 30 days; we use 31 to be safe

# --- STATE MANAGEMENT (PERSISTENCE) ---
# This file mimics a database. It stores when you last sold a stock for a loss.
LOG_FILE = 'bot_state.json'

def load_state():
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"wash_sale_log": {}} # Format: {'TICKER': '2025-12-15'}

def save_state(state):
    with open(LOG_FILE, 'w') as f:
        json.dump(state, f, indent=4)

# --- CORE LOGIC MODULES ---

def check_wash_sale(ticker, state):
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
            print(f"🚫 [WASH SALE WARNING] {ticker} is in cooldown. {31 - days_passed} days remaining.")
            return True # BLOCKED
        else:
            # Cooldown over, clean up the log
            del state["wash_sale_log"][ticker]
            save_state(state)
            return False # SAFE
            
    return False # SAFE

def get_market_data(ticker):
    """
    Placeholder: Fetch Real-Time Price & Technicals
    Returns: current_price (float), tech_indicators (dict)
    """
    # TODO: Connect to yfinance or Schwab API here
    # Mock data for demonstration:
    print(f"🔍 Fetching data for {ticker}...")
    return 38.57, {"rsi": 45, "trend": "stable"}

def analyze_erosion(ticker, current_price, my_avg_cost, total_dividends):
    """
    Calculates if capital erosion exceeds dividend gains.
    """
    # Example logic
    capital_loss = (current_price - my_avg_cost)
    net_position = capital_loss + total_dividends
    
    if net_position < 0 and abs(capital_loss) > (my_avg_cost * MAX_DRAWDOWN_PCT):
        return "SELL_CRITICAL"
    return "HOLD"

def execute_trade(action, ticker):
    """
    Placeholder: Send order to Broker API
    """
    print(f"🚀 EXECUTING ORDER: {action} on {ticker}")
    # TODO: Schwab/Robinhood Order Function goes here
    return True

# --- MAIN CONTROLLER ---

def run_bot_cycle():
    state = load_state()
    
    # 1. THE WATCHLIST LOOP
    for ticker in WATCHLIST:
        print(f"\n--- Analyzing {ticker} ---")
        
        # 2. CHECK WASH SALE STATUS FIRST
        if check_wash_sale(ticker, state):
            continue # Skip this stock, move to the next one
            
        # 3. GET DATA
        price, indicators = get_market_data(ticker)
        
        # 4. DECISION ENGINE
        # (You would pull these numbers from your portfolio API)
        my_avg_cost = 40.00 
        my_dividends = 0.55
        
        decision = analyze_erosion(ticker, price, my_avg_cost, my_dividends)
        
        # 5. EXECUTION & LOGGING
        if decision == "SELL_CRITICAL":
            success = execute_trade("SELL", ticker)
            if success:
                # MARK AS WASH SALE RISK
                # We record today's date so we don't buy it back for 31 days
                state["wash_sale_log"][ticker] = datetime.now().strftime("%Y-%m-%d")
                save_state(state)
                print(f"⚠️ {ticker} logged for Wash Sale Cooldown.")
                
        elif decision == "HOLD":
            print(f"✅ {ticker} is holding steady.")
            
    print("\nCycle Complete. Sleeping...")

# --- RUN LOOP ---
if __name__ == "__main__":
    while True:
        run_bot_cycle()
        # Sleep for 15 minutes to respect API limits and not over-trade
        time.sleep(900)