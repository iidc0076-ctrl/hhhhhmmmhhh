"""
Signal Feedback Commands
Discord commands for viewing signal feedback and improvement suggestions
"""

import discord
from discord import app_commands
from typing import Optional


class SignalFeedbackCommands(discord.Cog):
    """Cog for signal feedback Discord commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="signal_report",
        description="View signal feedback report and win rate statistics"
    )
    @app_commands.describe(
        pair="Optional: Specific pair to analyze (e.g., EUR/USD)",
        days="Number of days to analyze (default 7)"
    )
    async def signal_report(self, interaction: discord.Interaction, 
                           pair: Optional[str] = None, days: int = 7):
        """Get signal performance report"""
        
        await interaction.response.defer()
        
        try:
            from signal_feedback_integration import get_signal_feedback_integration
            
            integration = get_signal_feedback_integration()
            report = await integration.get_signal_report(pair, days)
            
            embed = discord.Embed(
                title="📊 Signal Feedback Report",
                description=f"Last {days} days",
                color=discord.Color.blue()
            )
            
            # Win rate section
            wr = report['win_rate']
            if wr.get('total', 0) > 0:
                embed.add_field(
                    name="📈 Win Rate Statistics",
                    value=f"Total Signals: {wr['total']}\n"
                          f"Wins: {wr['wins']} ({wr['win_rate']:.1f}%)\n"
                          f"Losses: {wr['losses']}\n"
                          f"Avg Pips: {wr.get('avg_pips', 0):.1f}\n"
                          f"Avg %: {wr.get('avg_percent', 0):.2f}%",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📈 Win Rate Statistics",
                    value="No signals to analyze yet",
                    inline=False
                )
            
            # Improvement suggestions
            suggestions = report['improvement_suggestions']
            if suggestions:
                suggestions_text = "\n".join([
                    f"**{s['category'].upper()}**: {s['description']}\n"
                    f"  Impact: {s['expected_impact']} | Action: {s['implementation']}"
                    for s in suggestions[:3]  # Top 3 suggestions
                ])
                embed.add_field(
                    name="💡 Top Improvement Suggestions",
                    value=suggestions_text,
                    inline=False
                )
            
            # Indicator performance
            ind_perf = report['indicator_performance']
            if ind_perf:
                perf_text = ""
                for indicator, stats in list(ind_perf.items())[:5]:
                    total = stats['wins'] + stats['losses']
                    if total > 0:
                        win_pct = stats['wins'] / total * 100
                        perf_text += f"**{indicator}**: {win_pct:.0f}% ({stats['wins']}W/{stats['losses']}L)\n"
                
                if perf_text:
                    embed.add_field(
                        name="🎯 Top Indicator Performance",
                        value=perf_text,
                        inline=False
                    )
            
            embed.set_footer(text="Feedback system powered by Signal Automation")
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to generate report: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="signal_history",
        description="View recent signal execution history"
    )
    @app_commands.describe(
        pair="Specific pair to view (e.g., EUR/USD)",
        limit="Number of signals to show (max 10)"
    )
    async def signal_history(self, interaction: discord.Interaction,
                            pair: Optional[str] = None, limit: int = 5):
        """Get signal execution history"""
        
        await interaction.response.defer()
        
        try:
            from signal_feedback_integration import get_signal_feedback_integration
            
            integration = get_signal_feedback_integration()
            history = await integration.get_signal_history(pair, days=30)
            
            if not history:
                embed = discord.Embed(
                    title="📋 Signal History",
                    description="No signals found",
                    color=discord.Color.greyple()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Signal Execution History",
                description=f"{'Last ' + str(limit) + ' signals' if pair else 'Recent signals'}",
                color=discord.Color.blue()
            )
            
            for signal in history[:limit]:
                outcome_emoji = "✅" if signal['outcome'] == 'WIN' else "❌" if signal['outcome'] == 'LOSS' else "➖"
                
                field_value = (
                    f"Direction: **{signal['direction']}**\n"
                    f"Expiry: {signal['expiry']}\n"
                    f"Confidence: {signal['entry_confidence']:.1f}%\n"
                    f"P&L: {signal['pips_change']:.1f} pips ({signal['percent_change']:.3f}%)\n"
                    f"Time: {signal['time_to_outcome']}s\n"
                    f"Reason: {signal['root_cause'][:60]}..."
                )
                
                embed.add_field(
                    name=f"{outcome_emoji} {signal['pair']} - {signal['outcome']}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="Oldest signal shown first")
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve history: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="signal_status",
        description="Check active signals being monitored"
    )
    async def signal_status(self, interaction: discord.Interaction):
        """Get status of active signals"""
        
        await interaction.response.defer()
        
        try:
            from signal_feedback_integration import get_signal_feedback_integration
            
            integration = get_signal_feedback_integration()
            active = await integration.get_active_signals()
            
            embed = discord.Embed(
                title="🔴 Active Signals",
                description=f"Currently monitoring {len(active)} signal(s)",
                color=discord.Color.brand_red() if active else discord.Color.greyple()
            )
            
            if not active:
                embed.description = "No active signals being monitored"
                await interaction.followup.send(embed=embed)
                return
            
            for signal_id, execution in list(active.items())[:10]:  # Show max 10
                elapsed = (execution.entry_time).isoformat()[-8:]
                embed.add_field(
                    name=f"🕐 {execution.pair} - {execution.direction}",
                    value=f"Confidence: {execution.entry_confidence:.1f}%\n"
                          f"Entry: {execution.entry_price:.5f}\n"
                          f"Started: {elapsed}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to get status: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup the feedback commands cog"""
    await bot.add_cog(SignalFeedbackCommands(bot))
