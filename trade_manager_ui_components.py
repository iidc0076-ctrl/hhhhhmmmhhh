"""
Trade Manager UI Components
Discord Views, Modals, Buttons, and Embeds for the QuantVision V1 trade manager system
"""

import discord
from discord.ext import commands
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from trade_manager_system import (
    get_trade_manager_status,
    create_trading_session,
    record_trade_result,
    get_user_performance,
    TradeManagerSystem,
    calculate_session_plan
)

# ===== TRADE MANAGER UI COMPONENTS =====

class AutoSessionStartView(discord.ui.View):
    """View that automatically starts a new session with updated capital from the last session"""
    
    def __init__(self, user_id: int, final_capital: float, last_session_info: dict):
        super().__init__(timeout=300)  # 5 minutes
        self.user_id = user_id
        self.final_capital = final_capital
        self.last_session_info = last_session_info
    
    @discord.ui.button(label="✅ Start New Session", style=discord.ButtonStyle.success)
    async def start_auto_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start new session with auto-updated capital"""
        try:
            from trade_manager_system import TradeManagerSystem
            tm_system = TradeManagerSystem()
            
            # Start new session with the final capital from last session
            result = tm_system.start_new_session(str(self.user_id), self.final_capital)
            
            if result.get('success'):
                # Get session status for display
                session_status = tm_system.get_session_status(str(self.user_id))
                next_trade_amount = session_status.get('next_trade_amount', 0) if session_status.get('success') else 0
                
                embed = discord.Embed(
                    title="✅ New Session Started Automatically",
                    description=f"Session #{result.get('session_number')} is now active\n*Capital automatically updated from previous session*",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="📊 Previous Session",
                    value=f"P/L: ${self.last_session_info.get('final_pl', 0):+.2f}\nResult: {self.last_session_info.get('session_result', 'Unknown').title()}",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 Updated Capital", 
                    value=f"${self.final_capital:,.2f}", 
                    inline=True
                )
                
                if next_trade_amount > 0:
                    embed.add_field(
                        name="💡 Next Trade Amount",
                        value=f"${next_trade_amount:.2f}",
                        inline=True
                    )
                
                # Create active view for the new session
                view = TradeManagerActiveView(self.user_id)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = discord.Embed(
                    title="❌ Session Error",
                    description=result.get('error', 'Failed to start new session'),
                    color=discord.Color.red()
                )
                await interaction.response.edit_message(embed=embed, view=None)
                
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to start new session: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="✏️ Enter Different Capital", style=discord.ButtonStyle.secondary)
    async def manual_capital_input(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allow user to manually enter different capital amount"""
        modal = NewSessionCapitalModal(self.user_id)
        await interaction.response.send_modal(modal)

class NewSessionCapitalModal(discord.ui.Modal):
    """Modal for manually updating capital when starting a new session"""
    
    def __init__(self, user_id: int):
        super().__init__(title="New Session - Manual Capital")
        self.user_id = user_id
    
    new_capital = discord.ui.TextInput(
        label="New Capital Amount",
        placeholder="Enter your current capital amount (numbers only)",
        required=True,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            from trade_manager_system import TradeManagerSystem
            tm_system = TradeManagerSystem()
            
            # Parse and validate capital
            try:
                updated_capital = float(self.new_capital.value.strip())
                if updated_capital <= 0:
                    raise ValueError("Capital must be positive")
                if updated_capital > 10000000:  # 10 million limit
                    raise ValueError("Capital amount is too large")
            except ValueError:
                raise ValueError("Please enter a valid number for capital")
            
            # Start new session with updated capital
            result = tm_system.start_new_session(str(self.user_id), updated_capital)
            
            if result.get('success'):
                # Get session status for display
                session_status = tm_system.get_session_status(str(self.user_id))
                next_trade_amount = session_status.get('next_trade_amount', 0) if session_status.get('success') else 0
                
                embed = discord.Embed(
                    title="✅ New Session Started",
                    description=f"Session #{result.get('session_number')} is now active",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="💰 Updated Capital", 
                    value=f"${updated_capital:,.2f}", 
                    inline=True
                )
                
                if next_trade_amount > 0:
                    embed.add_field(
                        name="💡 Next Trade Amount",
                        value=f"${next_trade_amount:.2f}",
                        inline=True
                    )
                
                # Create active view for the new session
                view = TradeManagerActiveView(self.user_id)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Session Error",
                    description=result.get('error', 'Failed to start new session'),
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description=str(e),
                color=discord.Color.red()
            )
            embed.add_field(
                name="💡 Format",
                value="Enter only numbers (no $ symbol)\nExample: 1000",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to start new session: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ResetConfirmationView(discord.ui.View):
    """Confirmation view for resetting user settings"""
    
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
    
    @discord.ui.button(label="✅ Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm settings reset"""
        try:
            from trade_manager_system import TradeManagerSystem
            tm_system = TradeManagerSystem()
            
            result = tm_system.reset_user_settings(str(self.user_id))
            
            if result.get('success'):
                embed = discord.Embed(
                    title="✅ Settings Reset",
                    description=result.get('message', 'All settings and data reset successfully'),
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Reset Error",
                    description=result.get('error', 'Failed to reset settings'),
                    color=discord.Color.red()
                )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to reset settings: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel settings reset"""
        embed = discord.Embed(
            title="❌ Reset Cancelled",
            description="Settings reset has been cancelled.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class TradeManagerSetupView(discord.ui.View):
    """View for setting up a new trade manager session"""

    def __init__(self, user_id: int):
        super().__init__(timeout=600)  # 10 minutes
        self.user_id = user_id

    @discord.ui.button(label="📊 New Session", style=discord.ButtonStyle.primary)
    async def new_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start new trading session setup with mode selection"""
        # Task 5: Show trading mode selection first
        embed = discord.Embed(
            title="🎯 Select Trading Mode",
            description="Choose your risk level and trading approach",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛡️ Conservative",
            value="Lower risk, smaller positions, steady growth",
            inline=True
        )
        
        embed.add_field(
            name="⚖️ Balanced",
            value="Moderate risk, standard calculations",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Aggressive",
            value="Higher risk, faster growth potential",
            inline=True
        )
        
        modal = TradeManagerSetupModal(self.user_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="❓ How It Works", style=discord.ButtonStyle.secondary)
    async def how_it_works(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show explanation of how the system works"""
        embed = discord.Embed(
            title="💼 How Smart Trade Manager Works",
            description="Mathematical algorithms for profitable trading even with low win rates",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🧮 Mathematical Foundation",
            value="• **Modified Kelly Criterion** for optimal position sizing\n• **Progressive Betting Algorithms** to recover losses\n• **Risk Management** to protect capital\n• **Statistical Analysis** for performance optimization",
            inline=False
        )

        embed.add_field(
            name="💡 Key Principle",
            value="The system calculates trade amounts so that even if you lose 9 trades in a row, winning the 10th trade will still result in overall profit. This is achieved through mathematical position sizing, not traditional martingale.",
            inline=False
        )

        embed.add_field(
            name="📊 Example Scenario",
            value="**Capital**: $1000\n**Target**: 5 wins out of 10 trades (max 50%)\n**Payout**: 80%\n\n✅ **Smart Sessions**: System calculates optimal session count based on your settings\n⚡ **Capital Protection**: Trade amounts automatically limited to protect your capital",
            inline=False
        )

        embed.add_field(
            name="⚡ Enhanced Features",
            value="• **Smart Session Calculation**: Automatically determines optimal session count\n• **Conservative Limits**: Max 20 trades, max 50% win rate required\n• **Capital Protection**: Progressive trade limits based on session requirements\n• **Real-time Calculations**: Dynamic trade amount based on current performance\n• **Risk Management**: Never exceed safe percentage of remaining capital",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class TradeManagerSetupModal(discord.ui.Modal):
    """Modal for collecting trade manager session parameters"""

    def __init__(self, user_id: int):
        super().__init__(title="💼 Trade Manager Setup")
        self.user_id = user_id

    initial_capital = discord.ui.TextInput(
        label="Initial Capital (numbers only)",
        placeholder="1000 (no $ symbol)",
        required=True,
        max_length=10
    )

    total_trades = discord.ui.TextInput(
        label="Total Trades per Session",
        placeholder="10 (range: 1-20)",
        required=True,
        max_length=2
    )

    gain_target = discord.ui.TextInput(
        label="Gain Target (% or $)",
        placeholder="2.5% or 25$ (% for percentage, $ for dollar amount)",
        required=True,
        max_length=10
    )

    payout_percentage = discord.ui.TextInput(
        label="Payout Percentage",
        placeholder="92 (range: 50-95, no % symbol)",
        required=True,
        max_length=2
    )

    win_trades_target = discord.ui.TextInput(
        label="Target Wins",
        placeholder="5 (max half of total trades)",
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            from trade_manager_system import TradeManagerSystem
            
            # Validate inputs are not empty
            if not self.initial_capital.value.strip():
                raise ValueError("Initial capital is required")
            if not self.total_trades.value.strip():
                raise ValueError("Total trades is required")
            if not self.win_trades_target.value.strip():
                raise ValueError("Target wins is required")
            if not self.payout_percentage.value.strip():
                raise ValueError("Payout percentage is required")
            if not self.gain_target.value.strip():
                raise ValueError("Gain target is required")
            
            # Parse and validate inputs with better error handling
            try:
                capital = float(self.initial_capital.value.strip().replace('$', '').replace(',', ''))
            except ValueError:
                raise ValueError("Invalid capital amount. Use numbers only (e.g., 1000)")
            
            try:
                total_trades = int(self.total_trades.value.strip())
            except ValueError:
                raise ValueError("Invalid total trades. Use whole numbers only (e.g., 10)")
            
            try:
                win_trades_wanted = int(self.win_trades_target.value.strip())
            except ValueError:
                raise ValueError("Invalid target wins. Use whole numbers only (e.g., 7)")
            
            try:
                payout_percentage = float(self.payout_percentage.value.strip().replace('%', ''))
            except ValueError:
                raise ValueError("Invalid payout percentage. Use numbers only (e.g., 92)")
            
            # Parse gain target (% or $) with better error handling
            gain_target_input = self.gain_target.value.strip()
            try:
                if '%' in gain_target_input:
                    gain_target_value = float(gain_target_input.replace('%', ''))
                    gain_target_type = 'percent'
                elif '$' in gain_target_input:
                    gain_target_value = float(gain_target_input.replace('$', ''))
                    gain_target_type = 'dollar'
                else:
                    # Default to percentage if no symbol
                    gain_target_value = float(gain_target_input)
                    gain_target_type = 'percent'
            except ValueError:
                raise ValueError("Invalid gain target. Use format like '2.5%' or '25$'")
            
            # Validate ranges
            if capital <= 0:
                raise ValueError("Capital must be positive")
            if capital > 1000000:
                raise ValueError("Capital must be less than $1,000,000")
            if not 1 <= total_trades <= 20:
                raise ValueError("Total trades must be between 1 and 20")
            max_wins = total_trades // 2
            if not 1 <= win_trades_wanted <= max_wins:
                raise ValueError(f"Target wins must be between 1 and {max_wins} (maximum half of total trades)")
            if not 50 <= payout_percentage <= 100:
                raise ValueError("Payout percentage must be between 50% and 100%")
            if gain_target_value <= 0:
                raise ValueError("Gain target must be positive")
            if gain_target_type == 'percent' and gain_target_value > 1000:
                raise ValueError("Percentage gain target must be reasonable (max 1000%)")
            if gain_target_type == 'dollar' and gain_target_value > capital * 10:
                raise ValueError("Dollar gain target is too high relative to capital")
            
            # Create user settings using the new system
            tm_system = TradeManagerSystem()
            result = tm_system.create_user_settings(
                user_id=str(self.user_id),
                capital=capital,
                total_trades=total_trades,
                win_trades_wanted=win_trades_wanted,
                payout_percentage=payout_percentage,
                gain_target_value=gain_target_value,
                gain_target_type=gain_target_type,

            )

            print(f"Session creation result: {result.get('success', False)}")

            if not result.get("success"):
                error_msg = result.get("error", "Unable to create trading session")
                embed = discord.Embed(
                    title="❌ Setup Error",
                    description=error_msg,
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Create success embed with the calculated session info
            embed = discord.Embed(
                title="✅ QuantVision Trade Manager 0V Setup Complete",
                description="Your trading system has been configured successfully",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="💰 Capital Settings",
                value=f"Initial Capital: ${capital:,.2f}\nGain Target: {gain_target_value}{'%' if gain_target_type == 'percent' else '$'}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Trading Settings", 
                value=f"Total Trades: {total_trades}\nWin Target: {win_trades_wanted}\nPayout: {payout_percentage}%",
                inline=True
            )
            
            sessions_required = result.get('sessions_required', 1)
            session_profit = result.get('session_profit_target', 0)
            
            # Calculate if sessions were extended for safety by checking base calculation
            if gain_target_type == 'percent':
                total_profit_target = capital * (gain_target_value / 100)
            else:
                total_profit_target = gain_target_value
            profit_ratio = total_profit_target / capital
            
            # Base session calculation (same logic as in TradeManagerSystem)
            if profit_ratio <= 0.02:
                base_sessions = 1
            elif profit_ratio <= 0.05:
                base_sessions = 2
            elif profit_ratio <= 0.10:
                base_sessions = 3
            elif profit_ratio <= 0.15:
                base_sessions = 4
            elif profit_ratio <= 0.25:
                base_sessions = 5
            elif profit_ratio <= 0.40:
                base_sessions = 6
            elif profit_ratio <= 0.60:
                base_sessions = 8
            elif profit_ratio <= 1.0:
                base_sessions = 10
            else:
                base_sessions = min(50, max(10, int(profit_ratio * 15)))
                
            sessions_extended = sessions_required > base_sessions
            
            embed.add_field(
                name="🎯 Session Plan",
                value=f"Sessions Required: **{sessions_required}**\nProfit per Session: **${session_profit:.2f}**",
                inline=False
            )
            
            # Start first session automatically
            session_result = tm_system.start_new_session(str(self.user_id))
            
            if session_result.get('success'):
                # Get the first trade amount from the new session
                session_status = tm_system.get_session_status(str(self.user_id))
                first_trade_amount = session_status.get('next_trade_amount', 0) if session_status.get('success') else 0
                
                embed.add_field(
                    name="🚀 Session Started",
                    value=f"Session #{session_result.get('session_number')} is now active",
                    inline=False
                )
                
                # Add trade amount field - this was missing before
                if first_trade_amount > 0:
                    embed.add_field(
                        name="💡 Next Trade Amount",
                        value=f"**Your first trade:** ${first_trade_amount:.2f}\n\nUse the buttons below to record your trade results.",
                        inline=False
                    )
                
                view = TradeManagerActiveView(self.user_id)
            else:
                view = TradeManagerSetupView(self.user_id)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except ValueError as e:
            print(f"Validation error: {e}")
            embed = discord.Embed(
                title="❌ Invalid Input",
                description=f"{str(e)}",
                color=discord.Color.red()
            )
            embed.add_field(
                name="📝 Correct Format Examples",
                value="• **Capital**: 1000 (no $ symbol)\n• **Trades**: 10 (whole number)\n• **Gain Target**: 2.5% or 25$ (include symbol)\n• **Payout**: 92 (no % symbol)\n• **Wins**: 7 (whole number)",
                inline=False
            )
            embed.add_field(
                name="💡 Tips",
                value="• Capital and Payout: numbers only\n• Gain Target: include % or $ symbol\n• Trades and Wins: whole numbers only",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            error_msg = str(e)
            print(f"Unexpected error in modal submission: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Provide more specific error information
            embed = discord.Embed(
                title="❌ Setup Error",
                description="There was an issue setting up your trade manager.",
                color=discord.Color.red()
            )
            
            if "database" in error_msg.lower():
                embed.add_field(
                    name="Database Issue",
                    value="Please try again in a few seconds. If the issue persists, contact support.",
                    inline=False
                )
            elif "import" in error_msg.lower():
                embed.add_field(
                    name="System Issue",
                    value="Trade manager system is temporarily unavailable. Please try again later.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Error Details",
                    value=f"Error: {error_msg[:200]}{'...' if len(error_msg) > 200 else ''}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

class SessionConfirmationView(discord.ui.View):
    """View for confirming session creation"""

    def __init__(self, user_id: int, capital: float, payout: float, total_trades: int, target_gain: float, plan: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.capital = capital
        self.payout = payout
        self.total_trades = total_trades
        self.target_gain = target_gain
        self.plan = plan

    @discord.ui.button(label="✅ Create Session", style=discord.ButtonStyle.success)
    async def create_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create the trading session"""
        try:
            # Create session parameters dict for the function
            parameters = {
                'initial_capital': self.capital,
                'capital': self.capital,  # Add this for compatibility
                'total_trades': self.total_trades,
                'target_gain_percent': self.target_gain,
                'payout_percentage': self.payout * 100,  # Convert back to percentage
                'win_trades_target': max(1, int(self.total_trades * 0.7)),  # Default 70% target
                'currency': 'USD'
            }

            result = create_trading_session(str(self.user_id), parameters)

            if result.get("success"):
                embed = await create_unified_session_created_embed(result)
                view = TradeManagerActiveView(self.user_id)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = discord.Embed(
                    title="❌ Session Creation Failed",
                    description=result.get("error", "Unknown error"),
                    color=discord.Color.red()
                )
                await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to create session: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel session creation"""
        embed = discord.Embed(
            title="❌ Session Cancelled",
            description="Session creation has been cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class TradeManagerActiveView(discord.ui.View):
    """View for managing active trading session"""

    def __init__(self, user_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.user_id = user_id

    @discord.ui.button(label="✅ Record Win", style=discord.ButtonStyle.success)
    async def record_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Record a winning trade"""
        await self._record_trade_result(interaction, "win")

    @discord.ui.button(label="❌ Record Loss", style=discord.ButtonStyle.danger)
    async def record_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Record a losing trade"""
        await self._record_trade_result(interaction, "loss")

    

    @discord.ui.button(label="📈 Performance", style=discord.ButtonStyle.secondary)
    async def show_performance(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show performance statistics"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            performance = get_user_performance(str(interaction.user.id))

            if performance.get('success'):
                embed = await create_performance_embed(performance)
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                embed = discord.Embed(
                    title="❌ Performance Error",
                    description=performance.get('error', 'Unable to retrieve performance data'),
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=self)

        except Exception as e:
            print(f"Error showing performance: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve performance data",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="🔄 Refresh Counter", style=discord.ButtonStyle.secondary)
    async def refresh_counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset session counter and clear performance statistics to start fresh"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            tm_system = TradeManagerSystem()
            reset_result = tm_system.reset_session_counter(str(interaction.user.id))
            
            if reset_result.get('success'):
                embed = discord.Embed(
                    title="🔄 Counter & Performance Refreshed",
                    description="Session counter has been reset to #1 and all performance statistics have been cleared. Your current session and settings remain unchanged.\n\nYour next new session will start as Session #1 with fresh performance tracking.",
                    color=discord.Color.blue()
                )
                await interaction.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Refresh Failed",
                    description=reset_result.get('error', 'Failed to refresh session counter and performance data'),
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                
        except Exception as e:
            print(f"Error refreshing counter: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to refresh session counter",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            print(f"Error getting performance: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve performance data",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="🆕 New Session", style=discord.ButtonStyle.success, row=1)
    async def new_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start new session with smart capital handling"""
        try:
            from trade_manager_system import TradeManagerSystem
            tm_system = TradeManagerSystem()
            
            # Check if there's an active session
            current_session = tm_system.get_session_status(str(interaction.user.id))
            
            # Check for last completed session
            last_session_result = tm_system.get_last_session_result(str(interaction.user.id))
            
            if current_session.get('success'):
                # There's an active session - ask for manual capital input
                embed = discord.Embed(
                    title="🚀 Start New Session",
                    description="You have an active session. Please enter your current capital to start a new session.",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="ℹ️ Note",
                    value="Since you're starting a new session during an active one, you'll need to manually enter your capital amount.",
                    inline=False
                )
                
                modal = NewSessionCapitalModal(interaction.user.id)
                await interaction.response.send_modal(modal)
                
            elif (last_session_result.get('success') and 
                  last_session_result.get('has_completed_session')):
                # Previous session completed - offer automatic capital update
                final_capital = last_session_result.get('final_capital', 0)
                
                embed = discord.Embed(
                    title="🎯 Previous Session Completed",
                    description="Your last session has ended. Start a new session with automatically updated capital?",
                    color=discord.Color.gold()
                )
                
                embed.add_field(
                    name="📊 Last Session Summary",
                    value=f"P/L: ${last_session_result.get('final_pl', 0):+.2f}\nResult: {last_session_result.get('session_result', 'Unknown').title()}",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 New Capital",
                    value=f"${final_capital:,.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="🔄 Action",
                    value="Capital will be automatically updated\nbased on your previous session results",
                    inline=False
                )
                
                # Use the automatic session start view
                view = AutoSessionStartView(interaction.user.id, final_capital, last_session_result)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                
            else:
                # No completed session found - ask for manual capital input
                embed = discord.Embed(
                    title="🚀 Start New Session",
                    description="Please enter your capital amount to start a new trading session.",
                    color=discord.Color.blue()
                )
                
                modal = NewSessionCapitalModal(interaction.user.id)
                await interaction.response.send_modal(modal)
            
        except Exception as e:
            print(f"Error starting new session: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to start new session",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Reset Settings", style=discord.ButtonStyle.danger, row=1)
    async def reset_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset settings and show setup modal for new configuration"""
        try:
            from trade_manager_system import TradeManagerSystem
            tm_system = TradeManagerSystem()
            
            # Reset all user settings and data
            reset_result = tm_system.reset_user_settings(str(interaction.user.id))
            
            if reset_result.get('success'):
                # Show setup modal directly after reset
                embed = discord.Embed(
                    title="✅ Settings Reset Complete",
                    description="All data has been cleared. Setting up your new trading configuration...",
                    color=discord.Color.green()
                )
                
                modal = TradeManagerSetupModal(interaction.user.id)
                await interaction.response.send_modal(modal)
            else:
                embed = discord.Embed(
                    title="❌ Reset Failed",
                    description=reset_result.get('error', 'Failed to reset settings'),
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error resetting settings: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to reset settings",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _record_trade_result(self, interaction: discord.Interaction, outcome: str):
        """Record trade result and update session"""
        try:
            from trade_manager_system import TradeManagerSystem
            
            # Defer response for longer processing time
            await interaction.response.defer(ephemeral=True)
            
            tm_system = TradeManagerSystem()
            
            # Get current session status to determine trade amount
            session_status = tm_system.get_session_status(str(interaction.user.id))
            
            if not session_status.get('success'):
                error_msg = session_status.get('error', 'No active session found')
                embed = discord.Embed(
                    title="❌ No Active Session",
                    description=f"Please start a new trading session first.\n\n**Error details:** {error_msg}",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=TradeManagerSetupView(interaction.user.id))
                return
            
            # Get the next trade amount from session status
            trade_amount = session_status.get('next_trade_amount', 0)
            
            if trade_amount <= 0:
                embed = discord.Embed(
                    title="❌ Invalid Trade Amount",
                    description="Unable to calculate trade amount. Please check your session.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=self)
                return
            
            # Record the trade result
            result = tm_system.record_trade_result(str(interaction.user.id), outcome, trade_amount)
            
            if not result.get('success'):
                embed = discord.Embed(
                    title="❌ Recording Error",
                    description=result.get('error', 'Failed to record trade'),
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=self)
                return
            
            # Create result embed
            session_data = session_status['session_data']
            trade_number = result['trade_number']
            profit_loss = result['profit_loss']
            new_pl = result['new_pl']
            is_completed = result['is_completed']
            session_result = result.get('session_result', 'active')
            
            embed = discord.Embed(
                title=f"{'✅' if outcome == 'win' else '❌'} Trade #{trade_number} Recorded",
                description=f"Trade Amount: ${trade_amount:.2f}",
                color=discord.Color.green() if outcome == 'win' else discord.Color.red()
            )
            
            embed.add_field(
                name="Trade Result",
                value=f"{'Win' if outcome == 'win' else 'Loss'}: ${profit_loss:+.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Session P/L",
                value=f"${new_pl:+.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Progress",
                value=f"{trade_number}/{session_data['total_trades']} trades",
                inline=True
            )
            
            if is_completed:
                # Check if all required sessions are complete
                sessions_completed = result.get('sessions_completed', 0)
                sessions_required = result.get('sessions_required', 1)
                current_wins = result.get('current_wins', 0)
                win_target = session_data.get('win_trades_wanted', 1)
                
                if session_result == 'success':
                    embed.add_field(
                        name="🎉 Session Complete",
                        value=f"Target reached! Wins: {current_wins}/{win_target}\nProfit: ${new_pl:.2f}",
                        inline=False
                    )
                    embed.color = discord.Color.gold()
                else:
                    embed.add_field(
                        name="📊 Session Complete", 
                        value=f"Session finished. Wins: {current_wins}/{win_target}\nFinal P/L: ${new_pl:.2f}",
                        inline=False
                    )
                
                # Check if this session completion fulfills the gain target
                sessions_completed = result.get('sessions_completed', 0)
                sessions_required = result.get('sessions_required', 1)
                
                # Only show gain target achieved if:
                # 1. Current session was successful
                # 2. We've completed exactly the required number of sessions
                # 3. This isn't just completing the first session when multiple are required
                gain_target_achieved = (session_result == 'success' and 
                    sessions_completed >= sessions_required and
                    (sessions_required == 1 or sessions_completed == sessions_required))
                
                if gain_target_achieved:
                    # Reset session counter automatically when gain target achieved
                    reset_result = tm_system.reset_session_counter(str(interaction.user.id))
                    
                    # Create completion notification
                    completion_embed = discord.Embed(
                        title="🎯 Gain Target Achieved!",
                        description="You have successfully reached your gain target across all required sessions!\n\n✅ Session counter has been reset - your next session will be Session #1.",
                        color=discord.Color.gold()
                    )
                    completion_embed.add_field(
                        name="Sessions Completed",
                        value=f"{sessions_completed} sessions",
                        inline=True
                    )
                    completion_embed.add_field(
                        name="Next Steps",
                        value="Use 'New Session' to continue trading or 'Reset Settings' to change your configuration",
                        inline=False
                    )
                    
                    # Send completion notification
                    await interaction.followup.send(embed=completion_embed, ephemeral=True)
                    
                    # Show setup view only when gain target is achieved
                    view = TradeManagerSetupView(interaction.user.id)
                else:
                    # Session completed but gain target not achieved - show auto session start
                    # Calculate final capital for next session
                    original_capital = session_data.get('capital', 0)
                    final_capital = original_capital + new_pl
                    
                    # Create session completion info
                    session_info = {
                        'final_pl': new_pl,
                        'session_result': session_result,
                        'original_capital': original_capital
                    }
                    
                    # Add session completion message to the embed
                    embed.add_field(
                        name="🔄 Ready for Next Session",
                        value=f"Capital updated: ${original_capital:,.2f} → ${final_capital:,.2f}\nClick 'Start New Session' to continue automatically",
                        inline=False
                    )
                    
                    # Show auto session start view with calculated capital
                    view = AutoSessionStartView(interaction.user.id, final_capital, session_info)
            else:
                # Get next trade amount for display
                updated_status = tm_system.get_session_status(str(interaction.user.id))
                next_amount = updated_status.get('next_trade_amount', 0)
                
                embed.add_field(
                    name="Next Trade Amount",
                    value=f"${next_amount:.2f}",
                    inline=False
                )
                view = self
            
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error recording trade: {e}")
            embed = discord.Embed(
                title="❌ Recording Error",
                description="Failed to record trade result",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=self)

# ===== EMBED CREATION FUNCTIONS =====

async def create_trade_manager_status_embed(session_status: Dict[str, Any], user_id: int) -> discord.Embed:
    """Create embed showing current trade manager session status"""
    if not session_status.get('success'):
        embed = discord.Embed(
            title="❌ No Active Session",
            description="No active trading session found",
            color=discord.Color.red()
        )
        return embed
    
    session_data = session_status['session_data']
    next_trade_amount = session_status.get('next_trade_amount', 0)
    
    embed = discord.Embed(
        title="💼 QuantVision Trade Manager 0V - Active Session",
        description=f"Session #{session_data['session_number']} Status",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💰 Capital Info",
        value=f"Initial: ${session_data['capital']:,.2f}\nCurrent P/L: ${session_data['current_pl']:+.2f}",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Session Target",
        value=f"Target: ${session_data['profit_target']:.2f}\nPayout: {session_data['payout_percentage']}%",
        inline=True
    )
    
    # Calculate current wins
    from trade_manager_system import TradeManagerSystem
    tm_system = TradeManagerSystem()
    current_wins = tm_system._count_wins_in_session(session_data['session_id'])
    
    # Determine current trade display
    current_trade_display = session_data['current_trade'] if session_data['current_trade'] > 0 else 0
    next_trade_display = current_trade_display + 1
    
    embed.add_field(
        name="📊 Progress",
        value=f"Trade: {current_trade_display}/{session_data['total_trades']}\nWins: {current_wins}/{session_data['win_trades_wanted']}",
        inline=True
    )
    
    embed.add_field(
        name="💡 Next Trade",
        value=f"Trade #{next_trade_display}: ${next_trade_amount:.2f}",
        inline=False
    )
    
    return embed

async def create_performance_embed(performance_data: Dict[str, Any]) -> discord.Embed:
    """Create embed showing user performance statistics"""
    if not performance_data.get('success'):
        embed = discord.Embed(
            title="❌ Performance Error",
            description="Unable to retrieve performance data",
            color=discord.Color.red()
        )
        return embed
    
    user_settings = performance_data['user_settings']
    session_perf = performance_data['session_performance']
    trade_perf = performance_data['trade_performance']
    
    embed = discord.Embed(
        title="📈 QuantVision Trade Manager 0V - Performance",
        description="Your trading performance statistics",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="⚙️ Current Settings",
        value=f"Capital: ${user_settings['capital']:,.2f}\nGain Target: {user_settings['gain_target_value']}{'%' if user_settings['gain_target_type'] == 'percent' else '$'}\nSessions Required: {user_settings['sessions_required']}",
        inline=True
    )
    
    embed.add_field(
        name="📊 Session Performance",
        value=f"Total Sessions: {session_perf['total_sessions']}\nSuccessful: {session_perf['successful_sessions']}\nSuccess Rate: {session_perf['success_rate']}%",
        inline=True
    )
    
    embed.add_field(
        name="💰 Profit Statistics",
        value=f"Total Profit: ${session_perf['total_profit']:+.2f}\nAvg Session P/L: ${session_perf['avg_session_pl']:+.2f}",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Trade Statistics",
        value=f"Total Trades: {trade_perf['total_trades']}\nWins: {trade_perf['total_wins']}\nWin Rate: {trade_perf['win_rate']}%",
        inline=False
    )
    
    return embed

# ===== LEGACY EMBED FUNCTIONS =====

async def create_unified_session_preview_embed(plan: Dict[str, Any]) -> discord.Embed:
    """Create embed showing session plan preview"""
    embed = discord.Embed(
        title="📊 QuantVision V1 Session Plan",
        description="Review your optimized trading session configuration",
        color=discord.Color.blue()
    )

    # Safe key access with fallbacks
    capital = plan.get('initial_capital', plan.get('capital', 0))
    session_gain = plan.get('session_gain', plan.get('target_gain', 0))
    target_gain_pct = plan.get('target_gain_percent', plan.get('account_gain_percent', 0))
    total_trades = plan.get('total_trades', 0)
    payout_ratio = plan.get('payout_ratio', 0.8)
    sessions_required = plan.get('sessions_required', 1)

    embed.add_field(
        name="💰 Financial Summary",
        value=f"**Capital**: ${capital:,.2f}\n"
              f"**Target Gain**: ${session_gain:,.2f} ({target_gain_pct}%)\n"
              f"**Session Gain**: ${session_gain:,.2f}\n"
              f"**Sessions Required**: {sessions_required}",
        inline=False
    )

    # Safe access for trade configuration
    final_trade = plan.get('final_trade', plan.get('betting_sequence', [0])[-1] if plan.get('betting_sequence') else 0)
    capital_usage = plan.get('capital_utilization_percent', 0)

    embed.add_field(
        name="🎯 Trade Configuration",
        value=f"**Trades per Session**: {total_trades}\n"
              f"**Payout Ratio**: {payout_ratio*100:.0f}%\n"
              f"**Final Trade**: ${final_trade:,.2f}\n"
              f"**Capital Usage**: {capital_usage:.1f}%",
        inline=False
    )

    # Safe access for trade sequence
    trade_sequence = plan.get('trade_sequence', plan.get('betting_sequence', []))
    if trade_sequence:
        trade_preview = ", ".join([f"${t:.2f}" for t in trade_sequence[:5]])
        if len(trade_sequence) > 5:
            trade_preview += "..."
    else:
        trade_preview = "No sequence available"

    # Safe access for risk metrics
    risk_metrics = plan.get('risk_metrics', {})
    risk_reward = risk_metrics.get('risk_reward_ratio', 0)
    max_trade = risk_metrics.get('max_trade_amount', final_trade)

    embed.add_field(
        name="📈 Trade Sequence Preview",
        value=f"**First Trades**: {trade_preview}\n"
              f"**Risk/Reward**: {risk_reward:.3f}\n"
              f"**Max Trade**: ${max_trade:,.2f}",
        inline=False
    )

    embed.set_footer(text="✅ Click 'Create Session' to start trading | ❌ Click 'Cancel' to modify")

    return embed

async def create_unified_session_created_embed(result: Dict[str, Any]) -> discord.Embed:
    """Create embed confirming session creation"""
    plan = result.get('plan', result.get('session_plan', {}))

    embed = discord.Embed(
        title="✅ Session Created Successfully!",
        description="Your QuantVision V1 trading session is now active",
        color=discord.Color.green()
    )

    # Safe key access
    session_id = result.get('session_id', 'unknown')
    capital = plan.get('capital', plan.get('initial_capital', 0))
    target_gain = plan.get('target_gain', plan.get('session_gain', 0))
    target_gain_pct = plan.get('target_gain_percent', plan.get('account_gain_percentage', 0))
    sessions_required = plan.get('sessions_required', 1)
    total_trades = plan.get('total_trades', 0)

    embed.add_field(
        name="🎯 Session Details",
        value=f"**Session ID**: {session_id[-8:] if len(session_id) >= 8 else session_id}...\n"
              f"**Capital**: ${capital:,.2f}\n"
              f"**Target**: ${target_gain:,.2f} ({target_gain_pct}%)\n"
              f"**Sessions**: {sessions_required}",
        inline=False
    )

    # Safe access for trade sequence
    trade_sequence = plan.get('trade_sequence', plan.get('betting_sequence', [0]))
    first_trade = trade_sequence[0] if trade_sequence else 0

    embed.add_field(
        name="📊 Next Trade",
        value=f"**Amount**: ${first_trade:,.2f}\n"
              f"**Trade 1 of {total_trades}**\n"
              f"**Session 1 of {sessions_required}**",
        inline=False
    )

    embed.add_field(
        name="🎮 Getting Started",
        value="Use the buttons below to:\n"
              "• Record trade results (Win/Loss)\n"
              "• Check session status\n"
              "• View performance metrics",
        inline=False
    )

    embed.set_footer(text="Trade with discipline and follow the calculated amounts exactly")

    return embed







# ===== SIMPLIFIED SETUP FLOW =====

# Import these classes in main.py
__all__ = [
    'TradeManagerSetupView', 'TradeManagerActiveView',
    'create_trade_manager_status_embed', 'create_detailed_session_status_embed', 'create_trade_result_embed'
]