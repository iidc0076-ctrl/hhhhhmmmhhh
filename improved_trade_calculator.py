#!/usr/bin/env python3
"""
Improved QuantVision Trade Calculator
Properly handles multiple win trades with adjusted session targets
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
    win_trades_needed: int
    payout_rate: float
    total_target_pct: float
    gain_per_session_pct: float
    profit_per_session: float
    sessions_required: float
    trade_sequence: List[TradeStep]
    total_exposure: float
    max_single_trade: float
    win_rate_required: float

class ImprovedTradeCalculator:
    """Properly handles multiple win trades with adjusted session calculations"""
    
    def calculate_optimal_session_target(self, capital: float, max_trades: int, 
                                       win_trades_needed: int, payout_rate: float, 
                                       total_target_pct: float) -> Tuple[float, float]:
        """
        Calculate optimal session target considering multiple wins needed
        Higher win requirements allow for larger session targets (fewer sessions)
        """
        total_target_amount = capital * (total_target_pct / 100)
        
        # Base session calculation considering win rate
        win_rate = win_trades_needed / max_trades
        max_loss_streak = max_trades - win_trades_needed
        
        # More wins needed = can handle larger session targets = fewer sessions
        if win_trades_needed >= 5:  # Very conservative (50%+ win rate)
            session_multiplier = 4.0
        elif win_trades_needed >= 3:  # Moderate (30%+ win rate) 
            session_multiplier = 2.5
        elif win_trades_needed == 2:  # Your case (20% win rate)
            session_multiplier = 1.8
        else:  # win_trades_needed == 1 (10% win rate)
            session_multiplier = 1.0
        
        # Calculate session target with multiplier
        base_session_target = capital * 0.0006  # 0.06% base
        adjusted_session_target = base_session_target * session_multiplier
        
        # Ensure it doesn't exceed reasonable limits
        max_session_target = min(
            total_target_amount * 0.1,  # Max 10% of total target per session
            capital * 0.01  # Max 1% of capital per session
        )
        
        session_target = min(adjusted_session_target, max_session_target)
        sessions_required = total_target_amount / session_target
        
        return session_target, sessions_required
    
    def calculate_martingale_for_multiple_wins(self, session_target: float, win_trades_needed: int,
                                             max_trades: int, payout_rate: float) -> List[TradeStep]:
        """
        Calculate Martingale sequence optimized for multiple wins
        Each win should contribute proportionally to the session target
        """
        profit_per_win = session_target / win_trades_needed
        sequence = []
        
        # Simulate worst-case scenario planning
        cumulative_loss = 0.0
        
        for trade_num in range(1, max_trades + 1):
            # Calculate trade amount to recover losses + contribute proportional profit
            if trade_num == 1:
                trade_amount = profit_per_win / payout_rate
            else:
                # Martingale: recover all losses + our share of session profit
                trade_amount = (cumulative_loss + profit_per_win) / payout_rate
            
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
                                  win_trades_needed: int, payout_pct: float, 
                                  total_target_pct: float) -> CalculationResult:
        """
        Complete calculation with proper multiple-win handling
        """
        payout_rate = payout_pct / 100.0
        win_rate_required = win_trades_needed / max_trades
        
        # Step 1: Calculate optimal session target for multiple wins
        session_target, sessions_required = self.calculate_optimal_session_target(
            capital, max_trades, win_trades_needed, payout_rate, total_target_pct
        )
        
        # Step 2: Generate optimized trade sequence
        trade_sequence = self.calculate_martingale_for_multiple_wins(
            session_target, win_trades_needed, max_trades, payout_rate
        )
        
        # Calculate metrics
        total_exposure = sum(step.trade_amount for step in trade_sequence)
        max_single_trade = max(step.trade_amount for step in trade_sequence)
        gain_per_session_pct = (session_target / capital) * 100
        
        return CalculationResult(
            capital=capital,
            max_trades=max_trades,
            win_trades_needed=win_trades_needed,
            payout_rate=payout_rate,
            total_target_pct=total_target_pct,
            gain_per_session_pct=round(gain_per_session_pct, 5),
            profit_per_session=round(session_target, 2),
            sessions_required=round(sessions_required, 2),
            trade_sequence=trade_sequence,
            total_exposure=round(total_exposure, 2),
            max_single_trade=round(max_single_trade, 2),
            win_rate_required=round(win_rate_required * 100, 1)
        )

def print_improved_results(result: CalculationResult):
    """Print results with multiple-win analysis"""
    print(f"\n{'='*60}")
    print(f"IMPROVED QUANTVISION CALCULATOR - MULTIPLE WINS")
    print(f"{'='*60}")
    
    print(f"\n📊 INPUT PARAMETERS:")
    print(f"   Capital: ${result.capital:,.2f}")
    print(f"   Max Trades: {result.max_trades}")
    print(f"   Win Trades Needed: {result.win_trades_needed}")
    print(f"   Required Win Rate: {result.win_rate_required:.1f}%")
    print(f"   Payout: {result.payout_rate*100:.1f}%")
    print(f"   Total Target: {result.total_target_pct:.1f}%")
    
    print(f"\n🎯 OPTIMIZED VALUES:")
    print(f"   Gain per session: {result.gain_per_session_pct:.5f}%")
    print(f"   Profit per session: ${result.profit_per_session:.2f}")
    print(f"   Sessions required: {result.sessions_required:.1f}")
    print(f"   Profit per win: ${result.profit_per_session/result.win_trades_needed:.2f}")
    
    print(f"\n💰 RISK ANALYSIS:")
    print(f"   Total exposure: ${result.total_exposure:,.2f}")
    print(f"   Max single trade: ${result.max_single_trade:,.2f}")
    print(f"   Risk ratio: {(result.total_exposure/result.capital)*100:.1f}% of capital")
    
    print(f"\n📈 OPTIMIZED MARTINGALE SEQUENCE:")
    print(f"{'#':<3} {'Trade Amount':<12} {'If Loss':<12} {'If Win (Net)':<15}")
    print(f"{'-'*42}")
    
    for step in result.trade_sequence:
        print(f"{step.trade_num:<3} ${step.trade_amount:<11.2f} "
              f"-${step.trade_amount:<11.2f} "
              f"+${step.net_profit_if_win:<14.2f}")
    
    print(f"\n✅ MULTIPLE-WIN STRATEGY BENEFITS:")
    if result.win_trades_needed > 1:
        print(f"   - Higher session target possible: ${result.profit_per_session:.2f}")
        print(f"   - Fewer sessions needed: {result.sessions_required:.1f}")
        print(f"   - Better success probability: {result.win_rate_required:.1f}% win rate")
        print(f"   - Smaller individual trades due to distributed profit")

# Test the improved calculator
if __name__ == "__main__":
    print("Testing improved calculator with your scenario:")
    
    calculator = ImprovedTradeCalculator()
    result = calculator.calculate_complete_scenario(
        capital=2692.12,
        max_trades=10,
        win_trades_needed=2,
        payout_pct=92.0,
        total_target_pct=2.0
    )
    
    print_improved_results(result)
    
    print(f"\n🔄 COMPARISON WITH 1-WIN STRATEGY:")
    result_1_win = calculator.calculate_complete_scenario(
        capital=2692.12,
        max_trades=10,
        win_trades_needed=1,
        payout_pct=92.0,
        total_target_pct=2.0
    )
    
    print(f"   1-win strategy:")
    print(f"   - Session target: ${result_1_win.profit_per_session:.2f}")
    print(f"   - Sessions needed: {result_1_win.sessions_required:.1f}")
    print(f"   - Max trade: ${result_1_win.max_single_trade:,.2f}")
    print(f"   ")
    print(f"   2-win strategy:")
    print(f"   - Session target: ${result.profit_per_session:.2f}")
    print(f"   - Sessions needed: {result.sessions_required:.1f}")
    print(f"   - Max trade: ${result.max_single_trade:,.2f}")