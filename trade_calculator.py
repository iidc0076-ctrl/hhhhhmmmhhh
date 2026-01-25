#!/usr/bin/env python3
"""
QuantVision Trade Calculator
Implements the exact logic you described for calculating:
1. Profit per session
2. Trade amounts (Martingale sequence)
3. Sessions required
"""

import math
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class TradeStep:
    trade_num: int
    trade_amount: float
    cumulative_loss: float
    payout_if_win: float
    net_profit_if_win: float

@dataclass
class CalculationResult:
    capital: float
    max_trades: int
    payout_rate: float
    total_target_pct: float
    gain_per_session_pct: float
    profit_per_session: float
    sessions_required: float
    trade_sequence: List[TradeStep]
    total_exposure: float
    max_single_trade: float

class TradeCalculator:
    """Implements your exact step-by-step calculation logic"""
    
    def calculate_safe_gain_per_session(self, capital: float, max_trades: int, payout_rate: float) -> float:
        """
        Step 1: Find the highest safe gain per session %
        Tests different values until maximum losing streak fits in risk limits
        """
        # Start with a conservative gain and work up
        test_gain_pct = 0.0001  # 0.01%
        max_safe_gain_pct = 0.0001
        
        # Test gains up to 1% per session
        while test_gain_pct <= 0.01:
            profit_target = capital * test_gain_pct
            
            # Simulate worst case: lose first (max_trades - 1) trades, win the last one
            total_exposure = 0.0
            cumulative_losses = 0.0
            
            for trade_num in range(1, max_trades + 1):
                if trade_num == 1:
                    trade_amount = profit_target / payout_rate
                else:
                    trade_amount = (cumulative_losses + profit_target) / payout_rate
                
                total_exposure += trade_amount
                
                # If this is not the final trade, add to cumulative losses
                if trade_num < max_trades:
                    cumulative_losses += trade_amount
                else:
                    # Final trade - check if we can still win our target
                    payout_if_win = trade_amount * payout_rate
                    net_profit = payout_if_win - cumulative_losses
                    if net_profit >= profit_target * 0.95:  # Allow 5% tolerance
                        max_safe_gain_pct = test_gain_pct
            
            # Safety check: don't risk more than 80% of capital
            if total_exposure > capital * 0.80:
                break
                
            test_gain_pct += 0.0001  # Increment by 0.01%
        
        return max_safe_gain_pct
    
    def calculate_trade_sequence(self, profit_per_session: float, payout_rate: float, max_trades: int) -> List[TradeStep]:
        """
        Step 2: Generate the complete Martingale trade sequence
        """
        sequence = []
        cumulative_loss = 0.0
        
        for trade_num in range(1, max_trades + 1):
            if trade_num == 1:
                trade_amount = profit_per_session / payout_rate
            else:
                trade_amount = (cumulative_loss + profit_per_session) / payout_rate
            
            # Round to 2 decimal places
            trade_amount = round(trade_amount, 2)
            payout_if_win = round(trade_amount * payout_rate, 2)
            net_profit_if_win = round(payout_if_win - cumulative_loss, 2)
            
            step = TradeStep(
                trade_num=trade_num,
                trade_amount=trade_amount,
                cumulative_loss=round(cumulative_loss, 2),
                payout_if_win=payout_if_win,
                net_profit_if_win=net_profit_if_win
            )
            
            sequence.append(step)
            cumulative_loss += trade_amount
        
        return sequence
    
    def calculate_complete_scenario(self, capital: float, max_trades: int, 
                                  payout_pct: float, total_target_pct: float) -> CalculationResult:
        """
        Complete calculation following your 3-step logic exactly
        """
        payout_rate = payout_pct / 100.0
        
        # Step 1: Calculate safe gain per session
        gain_per_session_pct = self.calculate_safe_gain_per_session(capital, max_trades, payout_rate)
        profit_per_session = capital * gain_per_session_pct
        
        # Step 3: Calculate sessions required
        sessions_required = total_target_pct / (gain_per_session_pct * 100)
        
        # Step 2: Generate trade sequence
        trade_sequence = self.calculate_trade_sequence(profit_per_session, payout_rate, max_trades)
        
        # Calculate totals
        total_exposure = sum(step.trade_amount for step in trade_sequence)
        max_single_trade = max(step.trade_amount for step in trade_sequence)
        
        return CalculationResult(
            capital=capital,
            max_trades=max_trades,
            payout_rate=payout_rate,
            total_target_pct=total_target_pct,
            gain_per_session_pct=gain_per_session_pct * 100,  # Convert to percentage
            profit_per_session=round(profit_per_session, 2),
            sessions_required=round(sessions_required, 2),
            trade_sequence=trade_sequence,
            total_exposure=round(total_exposure, 2),
            max_single_trade=round(max_single_trade, 2)
        )

def print_calculation_results(result: CalculationResult):
    """Pretty print the calculation results"""
    print(f"\n{'='*60}")
    print(f"QUANTVISION TRADE CALCULATOR RESULTS")
    print(f"{'='*60}")
    
    print(f"\n📊 INPUT PARAMETERS:")
    print(f"   Capital: ${result.capital:,.2f}")
    print(f"   Max Trades: {result.max_trades}")
    print(f"   Payout: {result.payout_rate*100:.1f}%")
    print(f"   Total Target: {result.total_target_pct:.1f}%")
    
    print(f"\n🎯 CALCULATED VALUES:")
    print(f"   Gain per session: {result.gain_per_session_pct:.5f}%")
    print(f"   Profit per session: ${result.profit_per_session:.2f}")
    print(f"   Sessions required: {result.sessions_required:.2f}")
    
    print(f"\n💰 RISK ANALYSIS:")
    print(f"   Total exposure: ${result.total_exposure:,.2f}")
    print(f"   Max single trade: ${result.max_single_trade:,.2f}")
    print(f"   Risk ratio: {(result.total_exposure/result.capital)*100:.1f}% of capital")
    
    print(f"\n📈 MARTINGALE SEQUENCE:")
    print(f"{'#':<3} {'Trade Amount':<12} {'If Loss':<12} {'If Win (Net)':<15}")
    print(f"{'-'*42}")
    
    for step in result.trade_sequence:
        print(f"{step.trade_num:<3} ${step.trade_amount:<11.2f} "
              f"-${step.trade_amount:<11.2f} "
              f"+${step.net_profit_if_win:<14.2f}")
    
    print(f"\n✅ VERIFICATION:")
    final_step = result.trade_sequence[-1]
    print(f"   Final trade profit if won: ${final_step.net_profit_if_win:.2f}")
    print(f"   Target profit per session: ${result.profit_per_session:.2f}")
    print(f"   Match: {'✓' if abs(final_step.net_profit_if_win - result.profit_per_session) < 0.10 else '✗'}")

def main():
    """Interactive calculator"""
    print("QuantVision Trade Calculator")
    print("Enter your trading parameters:")
    
    try:
        capital = float(input("\nCapital ($): "))
        max_trades = int(input("Max trades per session: "))
        payout_pct = float(input("Payout percentage (%): "))
        total_target_pct = float(input("Total target growth (%): "))
        
        calculator = TradeCalculator()
        result = calculator.calculate_complete_scenario(capital, max_trades, payout_pct, total_target_pct)
        
        print_calculation_results(result)
        
        # Ask if they want to try another calculation
        while input("\nCalculate another scenario? (y/n): ").lower() == 'y':
            capital = float(input("\nCapital ($): "))
            max_trades = int(input("Max trades per session: "))
            payout_pct = float(input("Payout percentage (%): "))
            total_target_pct = float(input("Total target growth (%): "))
            
            result = calculator.calculate_complete_scenario(capital, max_trades, payout_pct, total_target_pct)
            print_calculation_results(result)
            
    except ValueError:
        print("Please enter valid numbers.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with your example
    print("Testing with your example:")
    calculator = TradeCalculator()
    result = calculator.calculate_complete_scenario(
        capital=2624.13,
        max_trades=10,
        payout_pct=92.0,
        total_target_pct=2.0
    )
    print_calculation_results(result)
    
    print("\n" + "="*60)
    input("Press Enter to start interactive calculator...")
    main()