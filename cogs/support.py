"""
Support command for community links.
Security features:
- View timeout
- Rate limiting
- Configurable links via environment variables
"""

import discord
from discord import slash_command
from discord.ui import Button, View
from discord.ext import commands
import os
import logging

logger = logging.getLogger('SiimLeaksBot.support')


class Support(commands.Cog):
    """Support and community link commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Load URLs from environment (with defaults)
        self.invite_url = os.getenv('SUPPORT_INVITE_URL', 'https://discord.gg/UmbXvj69Zn')
        self.website_url = os.getenv('SUPPORT_WEBSITE_URL', 'https://aarmaa.ee')
        self.community_name = os.getenv('COMMUNITY_NAME', "Leaks's Community")
    
    @slash_command(
        name='support',
        description='Get community support links'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)  # 1 use per 10 seconds per user
    async def support(self, ctx: discord.ApplicationContext):
        """
        Display support links and community information.
        """
        # Create the view with a timeout
        view = View(timeout=180)  # 3 minute timeout
        
        # Invite button - opens a modal or sends link
        invite_button = Button(
            label=f"{self.community_name} Invite",
            style=discord.ButtonStyle.primary,
            emoji="🔗"
        )
        
        async def invite_callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                f"📨 Join our community: {self.invite_url}",
                ephemeral=True
            )
        
        invite_button.callback = invite_callback
        view.add_item(invite_button)
        
        # Website link button
        website_button = Button(
            label="Website",
            style=discord.ButtonStyle.link,
            url=self.website_url,
            emoji="🌐"
        )
        view.add_item(website_button)
        
        # Create embed
        embed = discord.Embed(
            title=f"💬 {self.community_name} Support",
            description="Need help? Here are some useful links!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Community Discord",
            value="Click the invite button to get the invite link",
            inline=False
        )
        embed.add_field(
            name="Website",
            value=f"Visit our website for more information",
            inline=False
        )
        embed.set_footer(text="We're here to help!")
        
        await ctx.respond(embed=embed, view=view)
        
        # Handle timeout
        async def on_timeout():
            try:
                # Disable all buttons on timeout
                for item in view.children:
                    if isinstance(item, Button) and not item.url:  # Don't disable link buttons
                        item.disabled = True
            except Exception:
                pass
        
        view.on_timeout = on_timeout
    
    @support.error
    async def support_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for the support command."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ Please wait {error.retry_after:.1f} seconds before using this command again.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in support command: {error}", exc_info=True)


def setup(bot: commands.Bot):
    bot.add_cog(Support(bot))
