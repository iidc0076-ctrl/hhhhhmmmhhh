#!/usr/bin/env python3
"""
Analyze optimal settings for small capital accounts
"""

def analyze_small_capital_recommendations():
    """Analyze optimal settings for $14 capital"""
    print("Small Capital Account Analysis ($14)")
    print("=" * 40)
    
    try:
        from trade_manager_system import TradeManagerSystem
        
        tm_system = TradeManagerSystem()
        capital = 14.0
        payout_pct = 92.0  # Assuming 92% payout
        
        print(f"Capital: ${capital}")
        print(f"Payout: {payout_pct}%")
        print()
        
        # Test different account gain percentages
        test_gains = [5.0, 7.0, 10.0, 15.0, 20.0]
        recommendations = []
        
        for gain_pct in test_gains:
            target_profit = capital * (gain_pct / 100)
            
            # Test different trade counts
            for total_trades in [5, 7, 10]:
                try:
                    # Generate betting sequence
                    sizing_params = {'account_gain_adjustment': gain_pct}
                    sequence = tm_system._generate_betting_sequence(
                        capital, total_trades, 1, payout_pct, sizing_params
                    )
                    
                    if len(sequence) >= 3:
                        max_bet = max(sequence)
                        max_bet_pct = (max_bet / capital) * 100
                        
                        # Calculate risk level
                        if max_bet_pct < 50:
                            risk_level = "Low"
                        elif max_bet_pct < 80:
                            risk_level = "Medium"
                        else:
                            risk_level = "High"
                        
                        recommendations.append({
                            'gain_pct': gain_pct,
                            'target_profit': target_profit,
                            'total_trades': total_trades,
                            'sequence': sequence[:5],  # First 5 trades
                            'max_bet': max_bet,
                            'max_bet_pct': max_bet_pct,
                            'risk_level': risk_level
                        })
                        
                except Exception as e:
                    continue
        
        # Sort by risk level and target profit
        recommendations.sort(key=lambda x: (x['risk_level'] == 'High', x['max_bet_pct']))
        
        print("RECOMMENDED SETTINGS:")
        print("=" * 40)
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\nOption {i} - {rec['risk_level']} Risk:")
            print(f"  Account Gain: {rec['gain_pct']}%")
            print(f"  Target Profit: ${rec['target_profit']:.2f}")
            print(f"  Total Trades: {rec['total_trades']}")
            print(f"  Win Target: 1 trade")
            print(f"  Max Bet: ${rec['max_bet']:.2f} ({rec['max_bet_pct']:.1f}% of capital)")
            print(f"  Sequence: {', '.join([f'${x:.2f}' for x in rec['sequence']])}")
        
        # Provide specific recommendation
        best = recommendations[0] if recommendations else None
        if best:
            print(f"\n🎯 BEST RECOMMENDATION:")
            print(f"   Capital: ${capital}")
            print(f"   Account Gain: {best['gain_pct']}%")
            print(f"   Total Trades: {best['total_trades']}")
            print(f"   Win Target: 1")
            print(f"   Target Profit: ${best['target_profit']:.2f} per session")
            print(f"   Risk Level: {best['risk_level']}")
            
            return {
                'capital': capital,
                'account_gain': best['gain_pct'],
                'total_trades': best['total_trades'],
                'win_target': 1,
                'target_profit': best['target_profit'],
                'risk_level': best['risk_level']
            }
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = analyze_small_capital_recommendations()
    if result:
        print(f"\nRecommendation generated successfully!")
    else:
        print("Failed to generate recommendations")