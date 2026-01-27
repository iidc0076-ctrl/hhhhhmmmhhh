"""
Enhanced Embed Creators for Forex and Stock Analysis
Creates comprehensive analysis embeds with all confluences and advanced features
"""

import discord
from datetime import datetime
from typing import Dict, Any, List, Optional

async def create_forex_analysis_embed(forex_analysis: Dict[str, Any], pair: str, 
                                    timeframe: str, regime_analysis: Dict = None) -> discord.Embed:
    """Create comprehensive forex analysis embed"""
    try:
        # Extract main signal data
        forex_signals = forex_analysis.get('forex_signals', {})
        signal = forex_signals.get('signal', 'NEUTRAL')
        confidence = forex_analysis.get('confidence', 0)
        
        # Color based on signal
        color = discord.Color.green() if signal == "BUY" else discord.Color.red() if signal == "SELL" else discord.Color.orange()
        signal_emoji = ""
        
        # Create embed without signal indicators
        embed = discord.Embed(
            title=f"{signal_emoji} {pair} Forex Analysis",
            description=f"📊 **Timeframe**: {timeframe} | 🎯 **Confidence**: {confidence:.1f}%",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Trend Analysis
        trend_analysis = forex_analysis.get('trend_analysis', {})
        if trend_analysis:
            trend_text = f"**Direction**: {trend_analysis.get('overall_trend', 'Unknown').title()}\n"
            trend_text += f"**Strength**: {trend_analysis.get('trend_strength', 0):.0f}%\n"
            trend_text += f"**Quality**: {trend_analysis.get('trend_quality', 'Unknown').title()}\n"
            trend_text += f"**ADX**: {trend_analysis.get('adx', 0):.1f}"
            embed.add_field(name="📈 Trend Analysis", value=trend_text, inline=True)
        
        # Enhanced Signal Confluences with Agreement/Conflict Analysis
        confluence_analysis = forex_analysis.get('enhanced_confluence_analysis', {})
        if confluence_analysis and confluence_analysis.get('confluence_factors'):
            # Get confluence summary
            agreement = confluence_analysis.get('agreement_analysis', {})
            summary = confluence_analysis.get('confluence_summary', {})
            factors = confluence_analysis.get('confluence_factors', [])
            
            # Create detailed confluence field
            confluence_text = f"**Agreement**: {agreement.get('bullish_count', 0)} | {agreement.get('bearish_count', 0)} | {agreement.get('neutral_count', 0)}\n"
            confluence_text += f"**Quality**: {summary.get('quality', 'unknown').title()} ({summary.get('confidence', 0):.0f}%)\n"
            
            if agreement.get('conflicts', False):
                confluence_text += f"⚠️ **Conflicts**: {agreement.get('conflict_score', 0)} opposing factors\n"
            
            confluence_text += f"**Score**: {confluence_analysis.get('confluence_score', 0):.1f}/100\n\n"
            
            # Show top factors with details
            top_factors = sorted(factors, key=lambda x: x.get('confidence', 0) * x.get('weight', 1), reverse=True)[:4]
            for factor in top_factors:
                direction = factor.get('direction', 'neutral')
                strength = factor.get('strength', 'weak')
                emoji = "" if direction == 'bullish' else "" if direction == 'bearish' else "•"
                strength_emoji = "💪" if strength in ['strong', 'very_strong'] else "👍" if strength == 'moderate' else "👌"
                
                factor_desc = factor.get('description', factor.get('name', 'Unknown'))
                confluence_text += f"{emoji}{strength_emoji} {factor_desc}\n"
            
            embed.add_field(name="🎯 Enhanced Confluence Analysis", value=confluence_text, inline=False)
        else:
            # Fallback to basic confluence display
            confluences = []
            
            # ICT/SMC Analysis
            ict_analysis = forex_analysis.get('ict_analysis', {})
            if ict_analysis:
                ict_signal = ict_analysis.get('signal', 'NEUTRAL')
                ict_confidence = ict_analysis.get('confidence', 0)
                confluences.append(f"ICT/SMC: {ict_signal} ({ict_confidence:.0f}%)")
            
            # Liquidity Analysis
            liquidity_analysis = forex_analysis.get('liquidity_analysis', {})
            if liquidity_analysis:
                liq_signal = liquidity_analysis.get('signal', 'NEUTRAL')
                liq_confidence = liquidity_analysis.get('confidence', 0)
                confluences.append(f"Liquidity: {liq_signal} ({liq_confidence:.0f}%)")
            
            # Institutional Flow
            institutional_flow = forex_analysis.get('institutional_flow', {})
            if institutional_flow:
                inst_signal = institutional_flow.get('signal', 'NEUTRAL')
                inst_confidence = institutional_flow.get('confidence', 0)
                confluences.append(f"Smart Money: {inst_signal} ({inst_confidence:.0f}%)")
            
            # Fractal Zones
            fractal_zones = forex_analysis.get('fractal_zones', {})
            if fractal_zones:
                frac_signal = fractal_zones.get('signal', 'NEUTRAL')
                frac_confidence = fractal_zones.get('confidence', 0)
                confluences.append(f"Fractal: {frac_signal} ({frac_confidence:.0f}%)")
            
            if confluences:
                confluence_text = "\n".join(confluences[:6])  # Show top 6
                embed.add_field(name="🎯 Signal Confluences", value=confluence_text, inline=True)
        
        # Risk Management
        risk_management = forex_analysis.get('risk_management', {})
        if risk_management:
            smart_stops = risk_management.get('smart_stops', {})
            if smart_stops:
                long_stops = smart_stops.get('long_stops', {})
                short_stops = smart_stops.get('short_stops', {})
                
                risk_text = ""
                if signal == 'BUY' and long_stops:
                    risk_text += f"**Stop Loss**: {long_stops.get('recommended_stop', 0):.5f}\n"
                elif signal == 'SELL' and short_stops:
                    risk_text += f"**Stop Loss**: {short_stops.get('recommended_stop', 0):.5f}\n"
                
                risk_text += f"**Risk %**: {risk_management.get('recommended_risk_pct', 2):.1f}%\n"
                atr_pips = risk_management.get('atr_pips', 0)
                risk_text += f"**ATR**: {atr_pips:.1f} pips"
                
                embed.add_field(name="⚖️ Risk Management", value=risk_text, inline=True)
        
        # Market Conditions
        market_conditions = forex_analysis.get('market_conditions', {})
        if market_conditions:
            conditions_text = f"**Phase**: {market_conditions.get('market_phase', 'Normal').title()}\n"
            conditions_text += f"**Conditions**: {market_conditions.get('conditions', 'Moderate').title()}"
            embed.add_field(name="🌍 Market Conditions", value=conditions_text, inline=True)
        
        # Session Analysis
        session_analysis = forex_analysis.get('session_analysis', {})
        if session_analysis:
            session_text = f"**Session**: {session_analysis.get('current_session', 'Unknown')}\n"
            session_text += f"**Bias**: {session_analysis.get('session_bias', 'Neutral').title()}"
            embed.add_field(name="🕒 Session Analysis", value=session_text, inline=True)
        
        # Entry Strategy
        entry_strategy = forex_analysis.get('entry_strategy', {})
        if entry_strategy and entry_strategy.get('direction') != 'WAIT':
            strategy_text = f"**Direction**: {entry_strategy.get('direction')}\n"
            strategy_text += f"**Type**: {entry_strategy.get('entry_type', 'Market').replace('_', ' ').title()}"
            embed.add_field(name="🎯 Entry Strategy", value=strategy_text, inline=True)
        
        # Footer
        embed.set_footer(text="Enhanced Forex Analysis System • Real-time data", 
                        icon_url="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/512px/1f4c8.png")
        
        return embed
        
    except Exception as e:
        print(f"Error creating forex embed: {e}")
        error_embed = discord.Embed(
            title="❌ Analysis Error",
            description="Unable to generate forex analysis",
            color=discord.Color.red()
        )
        return error_embed

async def create_stock_analysis_embed(stock_analysis: Dict[str, Any], symbol: str, 
                                    timeframe: str, regime_analysis: Dict = None) -> discord.Embed:
    """Create comprehensive stock analysis embed"""
    try:
        # Extract main signal data
        stock_signals = stock_analysis.get('stock_signals', {})
        signal = stock_signals.get('signal', 'NEUTRAL')
        confidence = stock_analysis.get('confidence', 0)
        
        # Color based on signal
        color = discord.Color.green() if signal == "BUY" else discord.Color.red() if signal == "SELL" else discord.Color.orange()
        signal_emoji = ""
        
        # Create embed without signal indicators
        embed = discord.Embed(
            title=f"{signal_emoji} {symbol} Stock Analysis",
            description=f"📊 **Timeframe**: {timeframe} | 🎯 **Confidence**: {confidence:.1f}%",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Trend Analysis
        trend_analysis = stock_analysis.get('trend_analysis', {})
        if trend_analysis:
            trend_text = f"**Direction**: {trend_analysis.get('overall_trend', 'Unknown').title()}\n"
            trend_text += f"**Strength**: {trend_analysis.get('trend_strength', 0):.0f}%\n"
            trend_text += f"**Quality**: {trend_analysis.get('trend_quality', 'Unknown').title()}"
            embed.add_field(name="📈 Trend Analysis", value=trend_text, inline=True)
        
        # Sector Analysis
        sector_analysis = stock_analysis.get('sector_analysis', {})
        if sector_analysis:
            sector_text = f"**Sector**: {sector_analysis.get('sector', 'Unknown')}\n"
            sector_text += f"**Performance**: {sector_analysis.get('sector_performance', 'Neutral').title()}\n"
            sector_text += f"**Rotation**: {sector_analysis.get('rotation_status', 'Stable').title()}"
            embed.add_field(name="🏭 Sector Analysis", value=sector_text, inline=True)
        
        # Enhanced Signal Confluences with Agreement/Conflict Analysis
        confluence_analysis = stock_analysis.get('enhanced_confluence_analysis', {})
        if confluence_analysis and confluence_analysis.get('confluence_factors'):
            # Get confluence summary
            agreement = confluence_analysis.get('agreement_analysis', {})
            summary = confluence_analysis.get('confluence_summary', {})
            factors = confluence_analysis.get('confluence_factors', [])
            
            # Create detailed confluence field
            confluence_text = f"**Agreement**: {agreement.get('bullish_count', 0)} | {agreement.get('bearish_count', 0)} | {agreement.get('neutral_count', 0)}\n"
            confluence_text += f"**Quality**: {summary.get('quality', 'unknown').title()} ({summary.get('confidence', 0):.0f}%)\n"
            
            if agreement.get('conflicts', False):
                confluence_text += f"⚠️ **Conflicts**: {agreement.get('conflict_score', 0)} opposing factors\n"
            
            confluence_text += f"**Score**: {confluence_analysis.get('confluence_score', 0):.1f}/100\n\n"
            
            # Show top factors with details
            top_factors = sorted(factors, key=lambda x: x.get('confidence', 0) * x.get('weight', 1), reverse=True)[:4]
            for factor in top_factors:
                direction = factor.get('direction', 'neutral')
                strength = factor.get('strength', 'weak')
                emoji = "" if direction == 'bullish' else "" if direction == 'bearish' else "•"
                strength_emoji = "💪" if strength in ['strong', 'very_strong'] else "👍" if strength == 'moderate' else "👌"
                
                factor_desc = factor.get('description', factor.get('name', 'Unknown'))
                confluence_text += f"{emoji}{strength_emoji} {factor_desc}\n"
            
            embed.add_field(name="🎯 Enhanced Confluence Analysis", value=confluence_text, inline=False)
        else:
            # Fallback to basic confluence display
            confluences = []
            
            # ICT/SMC Analysis
            ict_analysis = stock_analysis.get('ict_analysis', {})
            if ict_analysis:
                ict_signal = ict_analysis.get('signal', 'NEUTRAL')
                ict_confidence = ict_analysis.get('confidence', 0)
                confluences.append(f"ICT/SMC: {ict_signal} ({ict_confidence:.0f}%)")
            
            # Liquidity Analysis
            liquidity_analysis = stock_analysis.get('liquidity_analysis', {})
            if liquidity_analysis:
                liq_signal = liquidity_analysis.get('signal', 'NEUTRAL')
                liq_confidence = liquidity_analysis.get('confidence', 0)
                confluences.append(f"Liquidity: {liq_signal} ({liq_confidence:.0f}%)")
            
            # Institutional Flow
            institutional_flow = stock_analysis.get('institutional_flow', {})
            if institutional_flow:
                inst_signal = institutional_flow.get('signal', 'NEUTRAL')
                inst_confidence = institutional_flow.get('confidence', 0)
                confluences.append(f"Smart Money: {inst_signal} ({inst_confidence:.0f}%)")
            
            # Fractal Zones
            fractal_zones = stock_analysis.get('fractal_zones', {})
            if fractal_zones:
                frac_signal = fractal_zones.get('signal', 'NEUTRAL')
                frac_confidence = fractal_zones.get('confidence', 0)
                confluences.append(f"Fractal: {frac_signal} ({frac_confidence:.0f}%)")
            
            if confluences:
                confluence_text = "\n".join(confluences[:6])  # Show top 6
                embed.add_field(name="🎯 Signal Confluences", value=confluence_text, inline=True)
        
        # Risk Management
        risk_management = stock_analysis.get('risk_management', {})
        if risk_management:
            risk_text = f"**Risk %**: {risk_management.get('recommended_risk_pct', 2):.1f}%\n"
            risk_text += f"**Position Size**: Conservative\n"
            volatility = risk_management.get('volatility_assessment', {})
            if volatility:
                risk_text += f"**Volatility**: {volatility.get('regime', 'Medium').title()}"
            embed.add_field(name="⚖️ Risk Management", value=risk_text, inline=True)
        
        # Market Conditions
        market_conditions = stock_analysis.get('market_conditions', {})
        if market_conditions:
            conditions_text = f"**Market**: {market_conditions.get('overall_market', 'Neutral').title()}\n"
            conditions_text += f"**Sentiment**: {market_conditions.get('sentiment', 'Mixed').title()}"
            embed.add_field(name="🌍 Market Conditions", value=conditions_text, inline=True)
        
        # Entry Strategy
        entry_strategy = stock_analysis.get('entry_strategy', {})
        if entry_strategy and entry_strategy.get('direction') != 'WAIT':
            strategy_text = f"**Direction**: {entry_strategy.get('direction')}\n"
            strategy_text += f"**Type**: {entry_strategy.get('entry_type', 'Market').replace('_', ' ').title()}"
            embed.add_field(name="🎯 Entry Strategy", value=strategy_text, inline=True)
        
        # Footer
        embed.set_footer(text="Enhanced Stock Analysis System • Real-time data", 
                        icon_url="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/512px/1f4c8.png")
        
        return embed
        
    except Exception as e:
        print(f"Error creating stock embed: {e}")
        error_embed = discord.Embed(
            title="❌ Analysis Error",
            description="Unable to generate stock analysis",
            color=discord.Color.red()
        )
        return error_embed

class ForexAnalysisView(discord.ui.View):
    """Enhanced view for forex analysis with comprehensive buttons"""
    
    def __init__(self, pair: str, timeframe: str, analysis: Dict[str, Any], user_id: int):
        super().__init__(timeout=180)
        self.pair = pair
        self.timeframe = timeframe
        self.analysis = analysis
        self.user_id = user_id
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the forex analysis"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            from forex_stock_trading_systems import get_forex_analysis
            from ranging_trending_systems import detect_market_regime
            from main import fetch_batch_data
            
            # Fetch fresh data
            data_result = await fetch_batch_data([self.pair], self.timeframe, 0, 200)
            if not data_result or self.pair not in data_result:
                embed = discord.Embed(
                    title="❌ Refresh Error",
                    description="Unable to fetch fresh data",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            df = data_result[self.pair]
            
            # Get updated analysis
            forex_analysis = get_forex_analysis(df, self.pair)
            regime_analysis = detect_market_regime(df)
            
            # Update stored analysis
            self.analysis = forex_analysis
            
            # Create new embed
            embed = await create_forex_analysis_embed(forex_analysis, self.pair, self.timeframe, regime_analysis)
            
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
            
        except Exception as e:
            print(f"Error refreshing forex analysis: {e}")
            error_embed = discord.Embed(
                title="❌ Refresh Failed",
                description="Unable to refresh analysis",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    @discord.ui.button(label="📊 More Details", style=discord.ButtonStyle.secondary)
    async def more_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed analysis breakdown"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📊 Detailed Analysis - {self.pair}",
            description="Complete breakdown of all analysis components",
            color=discord.Color.blue()
        )
        
        # Risk Management Details
        risk_mgmt = self.analysis.get('risk_management', {})
        if risk_mgmt:
            risk_text = ""
            smart_stops = risk_mgmt.get('smart_stops', {})
            if smart_stops:
                risk_text += f"**Stop Strategy**: {smart_stops.get('recommended', 'ATR-based')}\n"
            
            take_profits = risk_mgmt.get('take_profits', {})
            if take_profits:
                risk_text += f"**TP Strategy**: {take_profits.get('strategy', 'Partial profits')}\n"
            
            risk_text += f"**Max Risk**: {risk_mgmt.get('recommended_risk_pct', 2):.1f}%\n"
            risk_text += f"**R:R Ratio**: {risk_mgmt.get('risk_reward', {}).get('minimum_rr', 2):.1f}:1"
            
            embed.add_field(name="⚖️ Risk Management", value=risk_text, inline=False)
        
        # Signal Factors
        forex_signals = self.analysis.get('forex_signals', {})
        factors = forex_signals.get('factors', [])
        if factors:
            factors_text = "\n".join([f"• {factor}" for factor in factors[:10]])
            embed.add_field(name="🎯 Signal Factors", value=factors_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📈 Generate Chart", style=discord.ButtonStyle.secondary)
    async def generate_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Generate analysis chart"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        await interaction.response.send_message("Chart generation feature coming soon!", ephemeral=True)

class StockAnalysisView(discord.ui.View):
    """Enhanced view for stock analysis with comprehensive buttons"""
    
    def __init__(self, symbol: str, timeframe: str, analysis: Dict[str, Any], user_id: int):
        super().__init__(timeout=180)
        self.symbol = symbol
        self.timeframe = timeframe
        self.analysis = analysis
        self.user_id = user_id
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the stock analysis"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            from forex_stock_trading_systems import get_stock_analysis
            from ranging_trending_systems import detect_market_regime
            from main import fetch_batch_data, convert_timeframe_for_provider
            
            # Fetch fresh data with correct timeframe
            timeframe = convert_timeframe_for_provider(self.timeframe, "polygon")
            data_result = await fetch_batch_data([self.symbol], timeframe, 0, 200)
            if not data_result or self.symbol not in data_result:
                embed = discord.Embed(
                    title="❌ Refresh Error",
                    description="Unable to fetch fresh data",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            df = data_result[self.symbol]
            
            # Get updated analysis
            stock_analysis = get_stock_analysis(df, self.symbol)
            regime_analysis = detect_market_regime(df)
            
            # Update stored analysis
            self.analysis = stock_analysis
            
            # Create new embed
            embed = await create_stock_analysis_embed(stock_analysis, self.symbol, self.timeframe, regime_analysis)
            
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
            
        except Exception as e:
            print(f"Error refreshing stock analysis: {e}")
            error_embed = discord.Embed(
                title="❌ Refresh Failed",
                description="Unable to refresh analysis",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    @discord.ui.button(label="📊 More Details", style=discord.ButtonStyle.secondary)
    async def more_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed analysis breakdown"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📊 Detailed Analysis - {self.symbol}",
            description="Complete breakdown of all analysis components",
            color=discord.Color.blue()
        )
        
        # Sector Analysis Details
        sector_analysis = self.analysis.get('sector_analysis', {})
        if sector_analysis:
            sector_text = f"**Sector**: {sector_analysis.get('sector', 'Unknown')}\n"
            sector_text += f"**Industry**: {sector_analysis.get('industry', 'N/A')}\n"
            sector_text += f"**Sector Strength**: {sector_analysis.get('sector_strength', 50):.0f}%\n"
            sector_text += f"**Relative Performance**: {sector_analysis.get('relative_performance', 'Neutral')}"
            embed.add_field(name="🏭 Sector Details", value=sector_text, inline=False)
        
        # Signal Factors
        stock_signals = self.analysis.get('stock_signals', {})
        factors = stock_signals.get('factors', [])
        if factors:
            factors_text = "\n".join([f"• {factor}" for factor in factors[:10]])
            embed.add_field(name="🎯 Signal Factors", value=factors_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📈 Generate Chart", style=discord.ButtonStyle.secondary)
    async def generate_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Generate analysis chart"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This analysis belongs to another user.", ephemeral=True)
            return
        
        await interaction.response.send_message("Chart generation feature coming soon!", ephemeral=True)


async def create_stock_analysis_embed(stock_analysis: Dict[str, Any], symbol: str, 
                                    timeframe: str, regime_analysis: Dict = None) -> discord.Embed:
    """Create comprehensive stock analysis embed"""
    try:
        # Extract main signal data
        stock_signals = stock_analysis.get('stock_signals', {})
        signal = stock_signals.get('signal', 'NEUTRAL')
        confidence = stock_analysis.get('confidence', 0)
        
        # Color based on signal
        color = discord.Color.green() if signal == "BUY" else discord.Color.red() if signal == "SELL" else discord.Color.orange()
        signal_emoji = ""
        
        # Create embed without signal indicators
        embed = discord.Embed(
            title=f"{signal_emoji} {symbol} Stock Analysis",
            description=f"📊 **Timeframe**: {timeframe} | 🎯 **Confidence**: {confidence:.1f}%",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Sector Analysis
        sector_analysis = stock_analysis.get('sector_analysis', {})
        if sector_analysis:
            sector_text = f"**Sector**: {sector_analysis.get('sector', 'Unknown')}\n"
            sector_text += f"**Bias**: {sector_analysis.get('sector_bias', 'neutral').title()}\n"
            sector_text += f"**Strength**: {sector_analysis.get('sector_strength', 0):.0f}%"
            embed.add_field(name="🏢 Sector Analysis", value=sector_text, inline=True)
        
        # Trend Analysis
        trend_analysis = stock_analysis.get('trend_analysis', {})
        if trend_analysis:
            trend_text = f"**Direction**: {trend_analysis.get('overall_trend', 'Unknown').title()}\n"
            trend_text += f"**Strength**: {trend_analysis.get('trend_strength', 0):.0f}%\n"
            trend_text += f"**Quality**: {trend_analysis.get('trend_quality', 'Unknown').title()}\n"
            trend_text += f"**Momentum**: {trend_analysis.get('momentum', 0):.0f}%"
            embed.add_field(name="📈 Trend Analysis", value=trend_text, inline=True)
        
        # Signal Confluences
        confluences = []
        
        # ICT/SMC Analysis
        ict_analysis = stock_analysis.get('ict_analysis', {})
        if ict_analysis:
            ict_signal = ict_analysis.get('signal', 'NEUTRAL')
            ict_confidence = ict_analysis.get('confidence', 0)
            confluences.append(f"ICT/SMC: {ict_signal} ({ict_confidence:.0f}%)")
        
        # Liquidity Analysis
        liquidity_analysis = stock_analysis.get('liquidity_analysis', {})
        if liquidity_analysis:
            liq_signal = liquidity_analysis.get('signal', 'NEUTRAL')
            liq_confidence = liquidity_analysis.get('confidence', 0)
            confluences.append(f"Liquidity: {liq_signal} ({liq_confidence:.0f}%)")
        
        # Institutional Flow
        institutional_flow = stock_analysis.get('institutional_flow', {})
        if institutional_flow:
            inst_signal = institutional_flow.get('signal', 'NEUTRAL')
            inst_confidence = institutional_flow.get('confidence', 0)
            confluences.append(f"Smart Money: {inst_signal} ({inst_confidence:.0f}%)")
        
        # Fractal Zones
        fractal_zones = stock_analysis.get('fractal_zones', {})
        if fractal_zones:
            frac_signal = fractal_zones.get('signal', 'NEUTRAL')
            frac_confidence = fractal_zones.get('confidence', 0)
            confluences.append(f"Fractal: {frac_signal} ({frac_confidence:.0f}%)")
        
        if confluences:
            confluence_text = "\n".join(confluences[:6])  # Show top 6
            embed.add_field(name="🎯 Signal Confluences", value=confluence_text, inline=True)
        
        # Risk Management
        risk_management = stock_analysis.get('risk_management', {})
        if risk_management:
            risk_text = f"**Risk %**: {risk_management.get('recommended_risk_pct', 1):.1f}%\n"
            risk_text += f"**Stop Loss**: {risk_management.get('stop_loss_pct', 5):.1f}%\n"
            risk_text += f"**Take Profit**: {risk_management.get('take_profit_pct', 10):.1f}%"
            embed.add_field(name="⚖️ Risk Management", value=risk_text, inline=True)
        
        # Market Conditions
        market_conditions = stock_analysis.get('market_conditions', {})
        if market_conditions:
            conditions_text = f"**Phase**: {market_conditions.get('market_phase', 'Normal').title()}\n"
            conditions_text += f"**Conditions**: {market_conditions.get('conditions', 'Moderate').Title()}"
            embed.add_field(name="📊 Market Conditions", value=conditions_text, inline=True)
        
        # Signal Factors
        factors = stock_signals.get('factors', [])
        if factors:
            factors_text = "\n".join([f"• {factor}" for factor in factors[:4]])
            if len(factors_text) > 1024:
                factors_text = factors_text[:1020] + "..."
            embed.add_field(name="📋 Key Factors", value=factors_text, inline=False)
        
        # Sector Factors
        sector_factors = sector_analysis.get('sector_factors', [])
        if sector_factors:
            sector_factors_text = "\n".join([f"• {factor}" for factor in sector_factors[:3]])
            embed.add_field(name="🏭 Sector Factors", value=sector_factors_text, inline=True)
        
        return embed
        
    except Exception as e:
        print(f"Error creating stock analysis embed: {e}")
        return discord.Embed(
            title="❌ Stock Analysis Error",
            description="Unable to create analysis display",
            color=discord.Color.red()
        )

class ForexAnalysisView(discord.ui.View):
    """Enhanced view for forex analysis with comprehensive features"""
    
    def __init__(self, pair: str, timeframe: str, analysis_data: Dict, user_id: int):
        super().__init__(timeout=480)  # 8 minutes
        self.pair = pair
        self.timeframe = timeframe
        self.analysis_data = analysis_data
        self.user_id = user_id
    
    @discord.ui.button(label="🔄 Refresh Analysis", style=discord.ButtonStyle.primary)
    async def refresh_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the forex analysis"""
        await interaction.response.defer()
        
        try:
            # Re-fetch data and analysis
            from forex_stock_trading_systems import get_forex_analysis
            from ranging_trending_systems import detect_market_regime
            from main import fetch_batch_data
            
            data_result = await fetch_batch_data([self.pair], self.timeframe, 0, 200)
            if data_result and self.pair in data_result:
                df = data_result[self.pair]
                forex_analysis = get_forex_analysis(df, self.pair)
                regime_analysis = detect_market_regime(df)
                
                # Update stored data
                self.analysis_data = forex_analysis
                
                # Create new embed
                embed = await create_forex_analysis_embed(forex_analysis, self.pair, self.timeframe, regime_analysis)
                await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
            else:
                await interaction.followup.send("Failed to refresh analysis data", ephemeral=True)
                
        except Exception as e:
            print(f"Error refreshing forex analysis: {e}")
            await interaction.followup.send("Error refreshing analysis", ephemeral=True)
    
    @discord.ui.button(label="📊 More Details", style=discord.ButtonStyle.secondary)
    async def more_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed analysis breakdown"""
        try:
            embed = discord.Embed(
                title=f"📊 Detailed Analysis - {self.pair}",
                description="Comprehensive breakdown of all analysis components",
                color=discord.Color.blue()
            )
            
            # ICT/SMC Details
            ict_analysis = self.analysis_data.get('ict_analysis', {})
            if ict_analysis:
                ict_factors = ict_analysis.get('factors', [])
                if ict_factors:
                    ict_text = "\n".join([f"• {factor}" for factor in ict_factors[:3]])
                    embed.add_field(name="🏛️ ICT/SMC Details", value=ict_text, inline=False)
            
            # Liquidity Details
            liquidity_analysis = self.analysis_data.get('liquidity_analysis', {})
            if liquidity_analysis:
                liq_factors = liquidity_analysis.get('factors', [])
                if liq_factors:
                    liq_text = "\n".join([f"• {factor}" for factor in liq_factors[:3]])
                    embed.add_field(name="💧 Liquidity Details", value=liq_text, inline=False)
            
            # Institutional Flow Details
            institutional_flow = self.analysis_data.get('institutional_flow', {})
            if institutional_flow:
                inst_factors = institutional_flow.get('factors', [])
                if inst_factors:
                    inst_text = "\n".join([f"• {factor}" for factor in inst_factors[:3]])
                    embed.add_field(name="🏦 Institutional Flow", value=inst_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error showing forex details: {e}")
            await interaction.response.send_message("Error displaying details", ephemeral=True)
    
    @discord.ui.button(label="📈 Generate Chart", style=discord.ButtonStyle.success)
    async def generate_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Generate trading chart"""
        try:
            embed = discord.Embed(
                title="📈 Chart Generation",
                description=f"Chart generation for {self.pair} is being developed. This will include:\n\n• Support/Resistance levels\n• ICT/SMC markings\n• Liquidity zones\n• Entry/Exit points\n• Risk management levels",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            await interaction.response.send_message("Chart generation error", ephemeral=True)
    
    @discord.ui.button(label="💼 Trade Manager", style=discord.ButtonStyle.success)
    async def trade_manager(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open trade manager integration"""
        try:
            from trade_manager_system import TradeManagerSystem
            from trade_manager_ui_components import TradeManagerSetupView, TradeManagerActiveView, create_trade_manager_status_embed
            
            tm_system = TradeManagerSystem()
            session_status = tm_system.get_session_status(str(self.user_id))
            
            # Get signal information
            forex_signals = self.analysis_data.get('forex_signals', {})
            signal = forex_signals.get('signal', 'NEUTRAL')
            confidence = self.analysis_data.get('confidence', 0)
            
            if session_status.get('success') and session_status.get('session_active'):
                # Show existing session with forex integration
                embed = await create_trade_manager_status_embed(session_status, self.user_id)
                
                embed.add_field(
                    name="💱 Forex Signal Integration",
                    value=f"**Pair**: {self.pair}\n**Signal**: {signal}\n**Confidence**: {confidence:.1f}%\n**Timeframe**: {self.timeframe}",
                    inline=False
                )
                
                next_amount = session_status.get('next_trade_amount', 0)
                embed.add_field(
                    name="💰 Calculated Trade Amount",
                    value=f"**Next Trade**: ${next_amount:.2f}\n*Optimized for your forex signal*",
                    inline=True
                )
                
                view = TradeManagerActiveView(self.user_id)
            else:
                # Show session setup
                embed = discord.Embed(
                    title="💼 Trade Manager - Forex Integration",
                    description=f"Set up smart capital management for your {self.pair} {signal} signal",
                    color=discord.Color.green() if signal == 'BUY' else discord.Color.red() if signal == 'SELL' else discord.Color.orange()
                )
                
                embed.add_field(
                    name="💱 Current Forex Signal",
                    value=f"**Pair**: {self.pair}\n**Signal**: {signal}\n**Confidence**: {confidence:.1f}%\n**Timeframe**: {self.timeframe}",
                    inline=False
                )
                
                view = TradeManagerSetupView(self.user_id)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error opening trade manager: {e}")
            await interaction.response.send_message("Error opening trade manager", ephemeral=True)

class StockAnalysisView(discord.ui.View):
    """Enhanced view for stock analysis with comprehensive features"""
    
    def __init__(self, symbol: str, timeframe: str, analysis_data: Dict, user_id: int):
        super().__init__(timeout=480)  # 8 minutes
        self.symbol = symbol
        self.timeframe = timeframe
        self.analysis_data = analysis_data
        self.user_id = user_id
    
    @discord.ui.button(label="🔄 Refresh Analysis", style=discord.ButtonStyle.primary)
    async def refresh_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the stock analysis"""
        await interaction.response.defer()
        
        try:
            # Re-fetch data and analysis
            from forex_stock_trading_systems import get_stock_analysis
            from ranging_trending_systems import detect_market_regime
            from main import fetch_batch_data
            
            # Map timeframes
            timeframe_map = {
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1week', '1m': '1month'
            }
            api_timeframe = timeframe_map.get(self.timeframe, '1d')
            
            data_result = await fetch_batch_data([self.symbol], api_timeframe, 0, 200)
            if data_result and self.symbol in data_result:
                df = data_result[self.symbol]
                stock_analysis = get_stock_analysis(df, self.symbol)
                regime_analysis = detect_market_regime(df)
                
                # Update stored data
                self.analysis_data = stock_analysis
                
                # Create new embed
                embed = await create_stock_analysis_embed(stock_analysis, self.symbol, self.timeframe, regime_analysis)
                await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
            else:
                await interaction.followup.send("Failed to refresh analysis data", ephemeral=True)
                
        except Exception as e:
            print(f"Error refreshing stock analysis: {e}")
            await interaction.followup.send("Error refreshing analysis", ephemeral=True)
    
    @discord.ui.button(label="📊 More Details", style=discord.ButtonStyle.secondary)
    async def more_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed analysis breakdown"""
        try:
            embed = discord.Embed(
                title=f"📊 Detailed Analysis - {self.symbol}",
                description="Comprehensive breakdown of all analysis components",
                color=discord.Color.blue()
            )
            
            # Sector Analysis Details
            sector_analysis = self.analysis_data.get('sector_analysis', {})
            if sector_analysis:
                sector_factors = sector_analysis.get('sector_factors', [])
                if sector_factors:
                    sector_text = "\n".join([f"• {factor}" for factor in sector_factors[:4]])
                    embed.add_field(name="🏢 Sector Analysis", value=sector_text, inline=False)
            
            # ICT/SMC Details
            ict_analysis = self.analysis_data.get('ict_analysis', {})
            if ict_analysis:
                ict_factors = ict_analysis.get('factors', [])
                if ict_factors:
                    ict_text = "\n".join([f"• {factor}" for factor in ict_factors[:3]])
                    embed.add_field(name="🏛️ ICT/SMC Details", value=ict_text, inline=False)
            
            # Risk Management Details
            risk_management = self.analysis_data.get('risk_management', {})
            if risk_management:
                risk_text = f"**Recommended Risk**: {risk_management.get('recommended_risk_pct', 1):.1f}% per trade\n"
                risk_text += f"**Stop Loss**: {risk_management.get('stop_loss_pct', 5):.1f}% below entry\n"
                risk_text += f"**Take Profit**: {risk_management.get('take_profit_pct', 10):.1f}% above entry"
                embed.add_field(name="⚖️ Risk Management", value=risk_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error showing stock details: {e}")
            await interaction.response.send_message("Error displaying details", ephemeral=True)
    
    @discord.ui.button(label="📈 Generate Chart", style=discord.ButtonStyle.success)
    async def generate_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Generate trading chart"""
        try:
            embed = discord.Embed(
                title="📈 Chart Generation",
                description=f"Chart generation for {self.symbol} is being developed. This will include:\n\n• Support/Resistance levels\n• Sector analysis overlay\n• ICT/SMC markings\n• Volume profile\n• Entry/Exit points\n• Risk management levels",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            await interaction.response.send_message("Chart generation error", ephemeral=True)
    
    @discord.ui.button(label="💼 Trade Manager", style=discord.ButtonStyle.success)
    async def trade_manager(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open trade manager integration"""
        try:
            from trade_manager_system import TradeManagerSystem
            from trade_manager_ui_components import TradeManagerSetupView, TradeManagerActiveView, create_trade_manager_status_embed
            
            tm_system = TradeManagerSystem()
            session_status = tm_system.get_session_status(str(self.user_id))
            
            # Get signal information
            stock_signals = self.analysis_data.get('stock_signals', {})
            signal = stock_signals.get('signal', 'NEUTRAL')
            confidence = self.analysis_data.get('confidence', 0)
            
            if session_status.get('success') and session_status.get('session_active'):
                # Show existing session with stock integration
                embed = await create_trade_manager_status_embed(session_status, self.user_id)
                
                embed.add_field(
                    name="📈 Stock Signal Integration",
                    value=f"**Symbol**: {self.symbol}\n**Signal**: {signal}\n**Confidence**: {confidence:.1f}%\n**Timeframe**: {self.timeframe}",
                    inline=False
                )
                
                view = TradeManagerActiveView(self.user_id)
            else:
                # Show session setup
                embed = discord.Embed(
                    title="💼 Trade Manager - Stock Integration",
                    description=f"Set up smart capital management for your {self.symbol} {signal} signal",
                    color=discord.Color.green() if signal == 'BUY' else discord.Color.red() if signal == 'SELL' else discord.Color.orange()
                )
                
                embed.add_field(
                    name="📈 Current Stock Signal",
                    value=f"**Symbol**: {self.symbol}\n**Signal**: {signal}\n**Confidence**: {confidence:.1f}%\n**Timeframe**: {self.timeframe}",
                    inline=False
                )
                
                view = TradeManagerSetupView(self.user_id)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error opening trade manager: {e}")
            await interaction.response.send_message("Error opening trade manager", ephemeral=True)