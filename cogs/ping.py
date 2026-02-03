"""
Simple ping command to check bot latency.
Security features:
- Rate limiting
"""

import discord
from discord import slash_command
from discord.ext import commands


class Ping(commands.Cog):
    """Utility commands for checking bot status."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @slash_command(
        name='ping',
        description='Check the bot\'s latency'
    )
    @commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Display the bot's current latency.
        
        Shows the WebSocket latency between the bot and Discord's servers.
        """
        latency_ms = round(self.bot.latency * 1000)
        
        # Color based on latency
        if latency_ms < 100:
            color = discord.Color.green()
            status = "🟢 Excellent"
        elif latency_ms < 200:
            color = discord.Color.gold()
            status = "🟡 Good"
        else:
            color = discord.Color.red()
            status = "🔴 Slow"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=color
        )
        embed.add_field(name="Latency", value=f"`{latency_ms}ms`", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        
        await ctx.respond(embed=embed)
    
    @ping.error
    async def ping_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for the ping command."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(Ping(bot))
