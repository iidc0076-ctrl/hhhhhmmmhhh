"""
Discord Interaction Timeout Handler
Provides strategies to handle long-running operations beyond Discord's 15-minute limit
"""

import discord
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class InteractionTimeoutHandler:
    """Handles long-running interactions that may exceed Discord's timeout"""
    
    def __init__(self):
        self.active_operations = {}  # Track ongoing operations
        self.followup_tokens = {}    # Store followup tokens for extended responses
    
    async def start_long_operation(self, interaction: discord.Interaction, operation_name: str, 
                                 initial_message: str = "Processing your request..."):
        """Start a long-running operation with proper timeout handling"""
        
        # Store operation details
        operation_id = f"{interaction.user.id}_{int(datetime.now().timestamp())}"
        self.active_operations[operation_id] = {
            'user_id': interaction.user.id,
            'channel_id': interaction.channel.id,
            'started_at': datetime.now(),
            'operation_name': operation_name,
            'status': 'running'
        }
        
        # Send initial response
        await interaction.response.send_message(initial_message, ephemeral=True)
        
        # Store the followup webhook for later use
        self.followup_tokens[operation_id] = interaction.followup
        
        return operation_id
    
    async def update_operation_status(self, operation_id: str, message: str, 
                                    embed: Optional[discord.Embed] = None):
        """Send status updates during long operations"""
        if operation_id in self.followup_tokens:
            try:
                followup = self.followup_tokens[operation_id]
                if embed:
                    await followup.send(embed=embed, ephemeral=True)
                else:
                    await followup.send(message, ephemeral=True)
            except discord.HTTPException:
                # Interaction expired, switch to direct message
                await self._send_direct_message(operation_id, message, embed)
    
    async def complete_operation(self, operation_id: str, final_message: str,
                               embed: Optional[discord.Embed] = None):
        """Complete the operation and send final results"""
        if operation_id in self.active_operations:
            try:
                followup = self.followup_tokens[operation_id]
                if embed:
                    await followup.send(embed=embed, ephemeral=True)
                else:
                    await followup.send(final_message, ephemeral=True)
            except discord.HTTPException:
                # Interaction expired, send DM
                await self._send_direct_message(operation_id, final_message, embed)
            finally:
                # Clean up
                self.active_operations.pop(operation_id, None)
                self.followup_tokens.pop(operation_id, None)
    
    async def _send_direct_message(self, operation_id: str, message: str, 
                                 embed: Optional[discord.Embed] = None):
        """Send direct message when interaction expires"""
        operation = self.active_operations.get(operation_id)
        if operation:
            try:
                user = await bot.fetch_user(operation['user_id'])
                if embed:
                    await user.send(embed=embed)
                else:
                    await user.send(f"**{operation['operation_name']} Complete**\n{message}")
            except discord.Forbidden:
                print(f"Cannot send DM to user {operation['user_id']}")
    
    async def create_persistent_task(self, operation_id: str, coro):
        """Create a task that continues running even after interaction expires"""
        async def task_wrapper():
            try:
                result = await coro
                await self.complete_operation(operation_id, "Operation completed successfully!", result)
            except Exception as e:
                error_embed = discord.Embed(
                    title="Operation Failed",
                    description=f"An error occurred: {str(e)}",
                    color=discord.Color.red()
                )
                await self.complete_operation(operation_id, "Operation failed.", error_embed)
        
        # Create background task
        task = asyncio.create_task(task_wrapper())
        return task

# Global instance
timeout_handler = InteractionTimeoutHandler()

async def handle_long_running_analysis(interaction: discord.Interaction, symbol: str, 
                                     analysis_type: str = "comprehensive"):
    """Example: Handle long-running market analysis that may exceed 15 minutes"""
    
    # Start the operation
    operation_id = await timeout_handler.start_long_operation(
        interaction, 
        f"Market Analysis - {symbol}",
        f"Starting comprehensive analysis for {symbol}. This may take several minutes..."
    )
    
    # Create the long-running task
    async def perform_analysis():
        # Send periodic updates
        await asyncio.sleep(5)
        await timeout_handler.update_operation_status(
            operation_id, 
            "Fetching market data and calculating indicators..."
        )
        
        # Simulate long analysis process
        await asyncio.sleep(10)
        await timeout_handler.update_operation_status(
            operation_id,
            "Running advanced signal validation systems..."
        )
        
        # More processing...
        await asyncio.sleep(15)
        
        # Create final result embed
        result_embed = discord.Embed(
            title=f"Analysis Complete - {symbol}",
            description="Comprehensive market analysis finished",
            color=discord.Color.green()
        )
        result_embed.add_field(name="Signal", value="BUY", inline=True)
        result_embed.add_field(name="Confidence", value="85%", inline=True)
        result_embed.add_field(name="Entry", value="1.1050", inline=True)
        
        return result_embed
    
    # Create persistent task
    await timeout_handler.create_persistent_task(operation_id, perform_analysis())

# Strategies for different timeout scenarios

class TimeoutStrategy:
    """Different strategies for handling interaction timeouts"""
    
    @staticmethod
    async def immediate_response_with_updates(interaction: discord.Interaction):
        """Send immediate response, then send updates via followup messages"""
        await interaction.response.send_message("Analysis started...", ephemeral=True)
        
        # Send updates every few minutes
        for i in range(5):
            await asyncio.sleep(180)  # 3 minutes
            try:
                await interaction.followup.send(f"Update {i+1}: Still processing...", ephemeral=True)
            except discord.HTTPException:
                break  # Interaction expired
    
    @staticmethod
    async def deferred_response(interaction: discord.Interaction):
        """Use deferred response for operations up to 15 minutes"""
        await interaction.response.defer(ephemeral=True)
        
        # Do work here (up to 15 minutes)
        await asyncio.sleep(10)  # Simulate work
        
        # Send final response
        await interaction.followup.send("Analysis complete!", ephemeral=True)
    
    @staticmethod
    async def background_task_with_dm(interaction: discord.Interaction, user_operation):
        """Start background task and notify via DM when complete"""
        await interaction.response.send_message(
            "Analysis started in background. You'll receive a DM when complete.", 
            ephemeral=True
        )
        
        # Create background task
        async def background_work():
            await asyncio.sleep(1800)  # 30 minutes of work
            
            # Send DM with results
            try:
                await interaction.user.send("Your analysis is complete!")
            except discord.Forbidden:
                print(f"Cannot send DM to {interaction.user.id}")
        
        asyncio.create_task(background_work())

# Enhanced command wrapper for automatic timeout handling
def handle_timeouts(max_duration_minutes: int = 14):
    """Decorator to automatically handle interaction timeouts"""
    def decorator(func):
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            # Calculate if operation might timeout
            start_time = datetime.now()
            
            # For operations that might take longer than Discord allows
            if max_duration_minutes > 14:
                # Use background task approach
                operation_id = await timeout_handler.start_long_operation(
                    interaction,
                    func.__name__,
                    "Starting operation in background..."
                )
                
                async def background_operation():
                    return await func(interaction, *args, **kwargs)
                
                await timeout_handler.create_persistent_task(operation_id, background_operation())
            else:
                # Use deferred response for shorter operations
                await interaction.response.defer(ephemeral=True)
                result = await func(interaction, *args, **kwargs)
                
                if isinstance(result, discord.Embed):
                    await interaction.followup.send(embed=result, ephemeral=True)
                elif isinstance(result, str):
                    await interaction.followup.send(result, ephemeral=True)
        
        return wrapper
    return decorator

# Example usage in your trading bot commands
@handle_timeouts(max_duration_minutes=30)
async def comprehensive_market_analysis(interaction: discord.Interaction, symbol: str):
    """Example command that might take longer than 15 minutes"""
    # This will automatically use background task approach
    # Your existing analysis code here
    pass