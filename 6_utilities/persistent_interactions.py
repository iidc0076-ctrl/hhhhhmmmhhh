"""
Persistent Discord Interactions System
Creates interactions and components that effectively never expire through automatic renewal
"""

import discord
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import weakref

class PersistentView(discord.ui.View):
    """Base view that automatically renews itself to prevent expiration"""
    
    def __init__(self, timeout_minutes: int = 14, auto_renew: bool = True):
        # Set timeout just under Discord's limit
        super().__init__(timeout=timeout_minutes * 60)
        self.auto_renew = auto_renew
        self.renewal_task = None
        self.original_interaction = None
        self.persistent_data = {}
        self.renewal_count = 0
        
    async def on_timeout(self):
        """Handle timeout by renewing the view if auto_renew is enabled"""
        if self.auto_renew and self.original_interaction:
            await self.renew_view()
        else:
            await self.cleanup()
    
    async def renew_view(self):
        """Create a new identical view to replace the expired one"""
        try:
            # Create new view with same state - pass timeout_minutes and auto_renew properly
            new_view = self.__class__(timeout_minutes=14, auto_renew=self.auto_renew)
            new_view.persistent_data = self.persistent_data.copy()
            new_view.renewal_count = self.renewal_count + 1
            new_view.original_interaction = self.original_interaction
            
            # Update the message with renewed view
            embed = discord.Embed(
                title="🔄 Interface Renewed",
                description=f"Interface automatically renewed (#{new_view.renewal_count})\nAll functions remain active.",
                color=discord.Color.blue()
            )
            
            if hasattr(self.original_interaction, 'edit_original_response'):
                await self.original_interaction.edit_original_response(embed=embed, view=new_view)
            else:
                # Fallback to followup if original response expired
                await self.original_interaction.followup.send(embed=embed, view=new_view, ephemeral=True)
            
            # Register the new view in the global tracker
            PersistentInteractionManager.register_view(new_view)
            
        except Exception as e:
            print(f"Error renewing view: {e}")
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources when view truly expires"""
        if self.renewal_task and not self.renewal_task.done():
            self.renewal_task.cancel()
        
        # Remove from global tracker
        PersistentInteractionManager.unregister_view(self)

class PersistentTradingControlPanel(PersistentView):
    """Persistent trading control panel that never expires"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_pair = "EURUSD"
        self.selected_timeframe = "1min"
        self.analysis_mode = "comprehensive"
    
    @discord.ui.select(
        placeholder="📈 Select Trading Pair",
        options=[
            discord.SelectOption(label="EURUSD", description="Euro vs US Dollar", emoji="🇪🇺"),
            discord.SelectOption(label="GBPUSD", description="British Pound vs US Dollar", emoji="🇬🇧"),
            discord.SelectOption(label="USDJPY", description="US Dollar vs Japanese Yen", emoji="🇯🇵"),
            discord.SelectOption(label="AUDUSD", description="Australian Dollar vs US Dollar", emoji="🇦🇺"),
            discord.SelectOption(label="USDCAD", description="US Dollar vs Canadian Dollar", emoji="🇨🇦"),
        ]
    )
    async def select_pair(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_pair = select.values[0]
        self.persistent_data['selected_pair'] = self.selected_pair
        
        embed = discord.Embed(
            title=f"📈 Trading Pair: {self.selected_pair}",
            description=f"Selected {self.selected_pair} for analysis",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.select(
        placeholder="⏰ Select Timeframe",
        options=[
            discord.SelectOption(label="1min", description="1 Minute Chart", emoji="⚡"),
            discord.SelectOption(label="5min", description="5 Minute Chart", emoji="🔥"),
            discord.SelectOption(label="15min", description="15 Minute Chart", emoji="📊"),
            discord.SelectOption(label="1hour", description="1 Hour Chart", emoji="⏳"),
            discord.SelectOption(label="1day", description="Daily Chart", emoji="📅"),
        ]
    )
    async def select_timeframe(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_timeframe = select.values[0]
        self.persistent_data['selected_timeframe'] = self.selected_timeframe
        
        embed = discord.Embed(
            title=f"⏰ Timeframe: {self.selected_timeframe}",
            description=f"Selected {self.selected_timeframe} timeframe for analysis",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎯 Generate Signal", style=discord.ButtonStyle.primary)
    async def generate_signal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # Your existing signal generation logic here
        embed = discord.Embed(
            title=f"🎯 Signal Generated - {self.selected_pair}",
            description=f"Analysis complete for {self.selected_pair} on {self.selected_timeframe}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Signal", value="BUY", inline=True)
        embed.add_field(name="Confidence", value="85%", inline=True)
        embed.add_field(name="Entry", value="1.1050", inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Advanced Analysis", style=discord.ButtonStyle.secondary)
    async def advanced_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # Trigger your advanced analysis system
        embed = discord.Embed(
            title=f"📊 Advanced Analysis - {self.selected_pair}",
            description="Running comprehensive market analysis...",
            color=discord.Color.purple()
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Refresh Interface", style=discord.ButtonStyle.success)
    async def manual_refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Manual refresh button for immediate renewal"""
        await self.renew_view()
        
        embed = discord.Embed(
            title="✅ Interface Refreshed",
            description="Interface manually refreshed and renewed for continued use.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PersistentInteractionManager:
    """Global manager for persistent interactions"""
    
    active_views = weakref.WeakSet()
    renewal_tasks = {}
    
    @classmethod
    def register_view(cls, view: PersistentView):
        """Register a view for automatic management"""
        cls.active_views.add(view)
        
        # Create renewal task
        if view.auto_renew:
            task = asyncio.create_task(cls._auto_renewal_loop(view))
            cls.renewal_tasks[id(view)] = task
    
    @classmethod
    def unregister_view(cls, view: PersistentView):
        """Remove view from management"""
        view_id = id(view)
        if view_id in cls.renewal_tasks:
            task = cls.renewal_tasks[view_id]
            if not task.done():
                task.cancel()
            del cls.renewal_tasks[view_id]
    
    @classmethod
    async def _auto_renewal_loop(cls, view: PersistentView):
        """Background task that periodically renews views"""
        try:
            while view.auto_renew:
                # Wait for renewal time (13 minutes to be safe)
                await asyncio.sleep(13 * 60)
                
                # Check if view still exists and needs renewal
                if view in cls.active_views:
                    await view.renew_view()
                else:
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in auto-renewal loop: {e}")
    
    @classmethod
    async def renew_all_views(cls):
        """Manually renew all active views"""
        for view in list(cls.active_views):
            try:
                await view.renew_view()
            except Exception as e:
                print(f"Error renewing view: {e}")
    
    @classmethod
    def get_active_count(cls) -> int:
        """Get count of active persistent views"""
        return len(cls.active_views)

class PersistentModal(discord.ui.Modal):
    """Modal that can be re-triggered to maintain persistence"""
    
    def __init__(self, title: str, callback_func=None):
        super().__init__(title=title)
        self.callback_func = callback_func
        self.persistent_data = {}
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission and optionally re-trigger"""
        if self.callback_func:
            await self.callback_func(interaction, self)
        
        # Optionally create a new modal for continued use
        await self.create_followup_modal(interaction)
    
    async def create_followup_modal(self, interaction: discord.Interaction):
        """Create a followup interaction to maintain modal availability"""
        embed = discord.Embed(
            title="✅ Submission Received",
            description="Your input has been processed. Use the button below to access the form again.",
            color=discord.Color.green()
        )
        
        class ModalTriggerView(discord.ui.View):
            def __init__(self, modal_class, **modal_kwargs):
                super().__init__(timeout=None)  # Never timeout
                self.modal_class = modal_class
                self.modal_kwargs = modal_kwargs
            
            @discord.ui.button(label="📝 Open Form Again", style=discord.ButtonStyle.primary)
            async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
                modal = self.modal_class(**self.modal_kwargs)
                await interaction.response.send_modal(modal)
        
        view = ModalTriggerView(self.__class__, callback_func=self.callback_func)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

# Integration with your existing bot commands
async def create_persistent_trading_panel(interaction: discord.Interaction):
    """Create a persistent trading control panel"""
    view = PersistentTradingControlPanel()
    view.original_interaction = interaction
    
    embed = discord.Embed(
        title="🎯 Persistent Trading Control Panel",
        description="This interface will automatically renew itself and never expire.\nSelect your trading preferences and generate signals.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔄 Auto-Renewal",
        value="Interface renews every 13 minutes automatically",
        inline=False
    )
    embed.add_field(
        name="📱 Persistent State",
        value="Your selections are maintained across renewals",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # Register with the manager
    PersistentInteractionManager.register_view(view)

# Bot command to create persistent interfaces
async def setup_persistent_commands(bot):
    """Add persistent interaction commands to your bot"""
    
    @bot.tree.command(name="persistent_panel", description="Create a persistent trading control panel")
    async def persistent_panel(interaction: discord.Interaction):
        await create_persistent_trading_panel(interaction)
    
    @bot.tree.command(name="persistent_status", description="Check status of persistent interactions")
    async def persistent_status(interaction: discord.Interaction):
        count = PersistentInteractionManager.get_active_count()
        embed = discord.Embed(
            title="📊 Persistent Interactions Status",
            description=f"Currently managing {count} persistent interface(s)",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="refresh_all", description="Manually refresh all persistent interfaces")
    async def refresh_all(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await PersistentInteractionManager.renew_all_views()
        
        embed = discord.Embed(
            title="✅ All Interfaces Refreshed",
            description="All persistent interfaces have been renewed",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)