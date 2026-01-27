"""
Binary Options Trade Manager
Mathematical martingale-based system for binary options trading
Follows exact specifications with proper capital management and risk controls
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TradeResult:
    """Individual trade result data"""
    trade_number: int
    previous_losses: float
    trade_amount: float
    payout_if_win: float
    net_profit_if_win: float
    total_exposure: float

@dataclass
class SessionAnalysis:
    """Complete session analysis results"""
    capital: float
    payout_percentage: float
    target_gain_percentage: float
    target_gain_amount: float
    optimal_trade_depth: int
    session_gain: float
    session_gain_percentage: float
    required_sessions: int
    trades: List[TradeResult]
    total_exposure: float
    capital_sufficient: bool
    max_safe_trades: int

class BinaryOptionsTradeManager:
    """
    Binary Options Trade Manager with martingale progression
    Ensures first trade >= $1 and follows exact mathematical formula
    """
    
    def __init__(self):
        self.min_first_trade = 1.00
        self.max_exposure_ratio = 0.95  # 95% of capital max exposure
        
    def calculate_trade_sequence(self, capital: float, payout_pct: float, 
                               target_gain_pct: float, max_trades: int = 10) -> SessionAnalysis:
        """
        Calculate complete trade sequence with martingale progression
        Matches exact examples provided by user
        
        Args:
            capital: Available trading capital (minimum $50)
            payout_pct: Payout percentage (e.g., 92 for 92%)
            target_gain_pct: Target gain percentage (e.g., 2 for 2%)
            max_trades: Maximum number of trades to calculate
            
        Returns:
            SessionAnalysis with complete trade breakdown
        """
        
        # Validate inputs
        if capital < 50:
            raise ValueError("Capital must be at least $50")
        if payout_pct <= 0 or payout_pct > 100:
            raise ValueError("Payout percentage must be between 0 and 100")
        if target_gain_pct <= 0:
            raise ValueError("Target gain percentage must be positive")
            
        # Convert percentage to decimal
        payout_ratio = payout_pct / 100
        target_gain_amount = capital * (target_gain_pct / 100)
        
        # Find optimal trade depth and session gain
        best_analysis = None
        best_efficiency = 0
        
        # Test different trade depths to find optimal
        for num_trades in range(3, max_trades + 1):
            analysis = self._analyze_trade_depth(
                capital, payout_ratio, target_gain_amount, num_trades
            )
            
            if analysis and analysis.capital_sufficient:
                # Calculate efficiency: session_gain / total_exposure
                efficiency = analysis.session_gain / analysis.total_exposure if analysis.total_exposure > 0 else 0
                
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_analysis = analysis
        
        # If no optimal found, use the safest option
        if not best_analysis:
            for num_trades in range(3, max_trades + 1):
                analysis = self._analyze_trade_depth(
                    capital, payout_ratio, target_gain_amount, num_trades
                )
                if analysis:
                    best_analysis = analysis
                    break
        
        if not best_analysis:
            # Fallback to simple calculation
            best_analysis = self._create_fallback_analysis(
                capital, payout_ratio, target_gain_pct, target_gain_amount
            )
        
        return best_analysis
    
    def _analyze_trade_depth(self, capital: float, payout_ratio: float, 
                           target_gain_amount: float, num_trades: int) -> Optional[SessionAnalysis]:
        """Analyze specific trade depth configuration"""
        
        trades = []
        cumulative_losses = 0.0
        total_exposure = 0.0
        
        # Calculate optimal session gain for this depth
        # Start with a conservative session gain and adjust
        session_gain = self._calculate_optimal_session_gain(
            capital, target_gain_amount, num_trades, payout_ratio
        )
        
        for i in range(num_trades):
            trade_num = i + 1
            
            if i == 0:
                # First trade calculation to ensure >= $1
                trade_amount = max(self.min_first_trade, session_gain / payout_ratio)
            else:
                # Martingale formula: (previous_losses + session_gain) / payout_ratio
                trade_amount = (cumulative_losses + session_gain) / payout_ratio
            
            # Round to 2 decimal places
            trade_amount = round(trade_amount, 2)
            
            # Calculate trade metrics
            payout_if_win = round(trade_amount * payout_ratio, 2)
            net_profit_if_win = round(payout_if_win - cumulative_losses, 2)
            total_exposure += trade_amount
            
            # Create trade result
            trade_result = TradeResult(
                trade_number=trade_num,
                previous_losses=round(cumulative_losses, 2),
                trade_amount=trade_amount,
                payout_if_win=payout_if_win,
                net_profit_if_win=net_profit_if_win,
                total_exposure=round(total_exposure, 2)
            )
            
            trades.append(trade_result)
            cumulative_losses += trade_amount
            
            # Check if we exceed capital
            if total_exposure > capital * self.max_exposure_ratio:
                break
        
        # Determine if capital is sufficient
        capital_sufficient = total_exposure <= capital * self.max_exposure_ratio
        max_safe_trades = len(trades) if capital_sufficient else len(trades) - 1
        
        # Calculate session metrics
        session_gain_pct = (session_gain / capital) * 100
        required_sessions = math.ceil(target_gain_amount / session_gain) if session_gain > 0 else 999
        
        return SessionAnalysis(
            capital=capital,
            payout_percentage=payout_ratio * 100,
            target_gain_percentage=target_gain_amount / capital * 100,
            target_gain_amount=target_gain_amount,
            optimal_trade_depth=len(trades),
            session_gain=session_gain,
            session_gain_percentage=session_gain_pct,
            required_sessions=required_sessions,
            trades=trades,
            total_exposure=round(total_exposure, 2),
            capital_sufficient=capital_sufficient,
            max_safe_trades=max_safe_trades
        )
    
    def _calculate_optimal_session_gain(self, capital: float, target_gain: float, 
                                      num_trades: int, payout_ratio: float) -> float:
        """Calculate optimal session gain based on capital and trade depth"""
        
        # Base session gain on capital size and trade depth
        if capital >= 1000:
            base_ratio = 0.001 + (0.0005 * (num_trades - 3))  # 0.1% to 0.45%
        elif capital >= 500:
            base_ratio = 0.002 + (0.001 * (num_trades - 3))   # 0.2% to 0.9%
        elif capital >= 100:
            base_ratio = 0.005 + (0.002 * (num_trades - 3))   # 0.5% to 1.9%
        else:
            base_ratio = 0.01 + (0.005 * (num_trades - 3))    # 1% to 4.5%
        
        # Calculate session gain
        session_gain = capital * base_ratio
        
        # Ensure minimum session gain
        min_session_gain = max(0.50, capital * 0.001)
        session_gain = max(session_gain, min_session_gain)
        
        # Cap session gain to be reasonable
        max_session_gain = min(target_gain * 0.5, capital * 0.05)
        session_gain = min(session_gain, max_session_gain)
        
        return round(session_gain, 2)
    
    def _create_fallback_analysis(self, capital: float, payout_ratio: float, 
                                target_gain_pct: float, target_gain_amount: float) -> SessionAnalysis:
        """Create fallback analysis when optimal calculation fails"""
        
        session_gain = capital * 0.01  # 1% session gain
        trades = []
        cumulative_losses = 0.0
        total_exposure = 0.0
        
        # Simple 5-trade sequence
        for i in range(5):
            trade_num = i + 1
            
            if i == 0:
                trade_amount = max(1.0, session_gain / payout_ratio)
            else:
                trade_amount = (cumulative_losses + session_gain) / payout_ratio
            
            trade_amount = round(trade_amount, 2)
            payout_if_win = round(trade_amount * payout_ratio, 2)
            net_profit_if_win = round(payout_if_win - cumulative_losses, 2)
            total_exposure += trade_amount
            
            trade_result = TradeResult(
                trade_number=trade_num,
                previous_losses=round(cumulative_losses, 2),
                trade_amount=trade_amount,
                payout_if_win=payout_if_win,
                net_profit_if_win=net_profit_if_win,
                total_exposure=round(total_exposure, 2)
            )
            
            trades.append(trade_result)
            cumulative_losses += trade_amount
        
        return SessionAnalysis(
            capital=capital,
            payout_percentage=payout_ratio * 100,
            target_gain_percentage=target_gain_pct,
            target_gain_amount=target_gain_amount,
            optimal_trade_depth=5,
            session_gain=session_gain,
            session_gain_percentage=(session_gain / capital) * 100,
            required_sessions=math.ceil(target_gain_amount / session_gain),
            trades=trades,
            total_exposure=round(total_exposure, 2),
            capital_sufficient=total_exposure <= capital * 0.95,
            max_safe_trades=5
        )
    
    def format_analysis_table(self, analysis: SessionAnalysis) -> str:
        """Format analysis results as a table"""
        
        # Header
        table = f"""
═══════════════════════════════════════════════════════════════════════════════
                            BINARY OPTIONS TRADE MANAGER
═══════════════════════════════════════════════════════════════════════════════

💰 CAPITAL ANALYSIS:
   Capital: ${analysis.capital:,.2f}
   Payout: {analysis.payout_percentage:.0f}%
   Target Gain: {analysis.target_gain_percentage:.1f}% → ${analysis.target_gain_amount:,.2f}
   First trade must be ≥ $1.00

✅ RESULTS:
   Session gain: ${analysis.session_gain:,.2f}
   Session gain %: {analysis.session_gain_percentage:.2f}%
   Required sessions: ~{analysis.required_sessions}
   Optimal trade depth: {analysis.optimal_trade_depth} trades

📊 TRADE SEQUENCE:
"""
        
        # Table header
        table += "\n┌─────────┬─────────────┬───────────┬────────────┬────────────┬──────────────┐"
        table += "\n│ Trade # │ Prev Losses │ Trade ($) │ Payout ($) │ Net Profit │ Total Expose │"
        table += "\n├─────────┼─────────────┼───────────┼────────────┼────────────┼──────────────┤"
        
        # Trade rows
        for trade in analysis.trades:
            table += f"\n│   {trade.trade_number:>2}    │   {trade.previous_losses:>8.2f}  │  {trade.trade_amount:>7.2f}  │   {trade.payout_if_win:>7.2f}  │   {trade.net_profit_if_win:>7.2f}  │   {trade.total_exposure:>9.2f}  │"
        
        table += "\n└─────────┴─────────────┴───────────┴────────────┴────────────┴──────────────┘"
        
        # Summary
        table += f"\n\n💡 SUMMARY:"
        table += f"\n   Total exposure: ${analysis.total_exposure:,.2f}"
        table += f"\n   Capital utilization: {(analysis.total_exposure/analysis.capital)*100:.1f}%"
        
        if not analysis.capital_sufficient:
            table += f"\n   ⚠️  WARNING: Capital insufficient for full sequence"
            table += f"\n   ⚠️  Safe limit: {analysis.max_safe_trades} trades"
        else:
            table += f"\n   ✅ Capital sufficient for full sequence"
        
        table += f"\n\n🎯 TO REACH TARGET:"
        table += f"\n   Sessions needed: {analysis.required_sessions}"
        table += f"\n   Total profit: ${analysis.required_sessions * analysis.session_gain:,.2f}"
        table += f"\n   Final balance: ${analysis.capital + (analysis.required_sessions * analysis.session_gain):,.2f}"
        
        table += "\n\n═══════════════════════════════════════════════════════════════════════════════"
        
        return table
    
    def get_quick_examples(self) -> str:
        """Generate quick examples for common scenarios"""
        
        examples = []
        test_cases = [
            (50, 92, 2),      # Example 1
            (100, 92, 2),     # Example 2  
            (160, 92, 2),     # Example 3
            (840.11, 92, 2),  # Example 4
            (1000, 92, 3),    # Example 5
        ]
        
        for capital, payout, target in test_cases:
            try:
                analysis = self.calculate_trade_sequence(capital, payout, target)
                examples.append(f"Capital ${capital:,.2f}: {analysis.optimal_trade_depth} trades, ${analysis.session_gain:.2f} session gain, {analysis.required_sessions} sessions needed")
            except Exception as e:
                examples.append(f"Capital ${capital:,.2f}: Error - {str(e)}")
        
        return "\n".join(examples)

def main():
    """Interactive main function for user input"""
    
    print("🎯 BINARY OPTIONS TRADE MANAGER")
    print("=" * 50)
    
    manager = BinaryOptionsTradeManager()
    
    try:
        # Get user inputs
        capital = float(input("Enter your capital ($): "))
        payout_pct = float(input("Enter payout percentage (%): "))
        target_gain_pct = float(input("Enter target gain percentage (%): "))
        
        # Calculate analysis
        analysis = manager.calculate_trade_sequence(capital, payout_pct, target_gain_pct)
        
        # Display results
        print(manager.format_analysis_table(analysis))
        
    except ValueError as e:
        print(f"❌ Input Error: {e}")
    except Exception as e:
        print(f"❌ Calculation Error: {e}")

def run_examples():
    """Run the specific examples from the requirements"""
    
    manager = BinaryOptionsTradeManager()
    
    examples = [
        (50.00, 92, 2),
        (100.00, 92, 2),
        (160.00, 92, 2),
        (840.11, 92, 2),
        (1000.00, 92, 3),
    ]
    
    for i, (capital, payout, target) in enumerate(examples, 1):
        print(f"\n🧪 EXAMPLE {i} — Capital: ${capital}")
        print("=" * 60)
        
        try:
            analysis = manager.calculate_trade_sequence(capital, payout, target)
            print(manager.format_analysis_table(analysis))
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    # Run examples first to demonstrate
    print("Running example calculations...")
    run_examples()
    
    # Then interactive mode
    print("\n\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    main()