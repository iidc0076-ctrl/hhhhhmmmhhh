#!/usr/bin/env python3
"""
Validate the exact user examples with precise calculations
"""

def calculate_exact_sequence(capital, total_trades, win_trades, payout_rate, session_target):
    """Calculate exact trade sequence for given parameters"""
    
    profit_per_win = session_target / win_trades
    trades = []
    cumulative_pl = 0.0
    
    print(f"Session Target: ${session_target:.2f}")
    print(f"Profit per win needed: ${profit_per_win:.2f}")
    print(f"Payout rate: {payout_rate*100:.0f}%")
    print()
    
    for trade_num in range(1, total_trades + 1):
        if trade_num == 1:
            trade_amount = profit_per_win / payout_rate
        else:
            # Need to recover losses + generate profit
            losses_to_recover = abs(min(0, cumulative_pl))
            trade_amount = (losses_to_recover + profit_per_win) / payout_rate
        
        trades.append(trade_amount)
        print(f"Trade {trade_num}: ${trade_amount:.2f}")
        
        # Check if trade exceeds capital limit
        if trade_amount > capital * 0.9:
            print(f"  ⚠️  Exceeds 90% capital limit (${capital * 0.9:.2f})")
            return None, trades
        
        # For simulation, assume this is a loss (worst case)
        cumulative_pl -= trade_amount
    
    print(f"\nWorst case cumulative loss: ${abs(cumulative_pl):.2f}")
    print(f"Max trade: ${max(trades):.2f} ({max(trades)/capital*100:.1f}% of capital)")
    
    return max(trades), trades

def find_optimal_target(capital, total_trades, win_trades, payout_rate, target_percentage_range):
    """Find optimal session target within range"""
    
    print(f"Testing session targets for {win_trades}/{total_trades} win strategy...")
    print(f"Capital: ${capital:.0f}, Payout: {payout_rate*100:.0f}%")
    print("="*50)
    
    best_target = 0
    
    # Test from high to low percentage
    for pct in target_percentage_range:
        session_target = capital * (pct / 100)
        print(f"\nTesting {pct:.1f}% (${session_target:.2f}):")
        
        max_trade, trades = calculate_exact_sequence(capital, total_trades, win_trades, payout_rate, session_target)
        
        if max_trade and max_trade <= capital * 0.9:
            print(f"✅ SAFE - Max trade ${max_trade:.2f} is within limits")
            best_target = session_target
            break
        else:
            print(f"❌ UNSAFE - Exceeds capital limits")
    
    return best_target

# Test User Example 1: 2 wins in 5 trades
print("USER EXAMPLE 1: 2 wins in 5 trades")
print("="*60)
target1 = find_optimal_target(
    capital=50.0,
    total_trades=5,
    win_trades=2,
    payout_rate=0.92,
    target_percentage_range=[10.0, 8.0, 6.0, 5.9, 5.8, 5.7, 5.6, 5.5, 5.0, 4.5, 4.0]
)
print(f"\nOptimal session target: ${target1:.2f} ({target1/50*100:.1f}% of capital)")
sessions_needed = 5.0 / target1  # $5 total target
print(f"Sessions needed for 10% gain: {sessions_needed:.1f}")

print("\n" + "="*60)

# Test User Example 2: 1 win in 5 trades  
print("USER EXAMPLE 2: 1 win in 5 trades")
print("="*60)
target2 = find_optimal_target(
    capital=50.0,
    total_trades=5,
    win_trades=1,
    payout_rate=0.92,
    target_percentage_range=[10.0, 8.0, 6.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0]
)
print(f"\nOptimal session target: ${target2:.2f} ({target2/50*100:.1f}% of capital)")
sessions_needed = 5.0 / target2  # $5 total target
print(f"Sessions needed for 10% gain: {sessions_needed:.1f}")