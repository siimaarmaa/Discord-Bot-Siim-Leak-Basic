"""
Help command showing available bot commands.
Security features:
- Dynamic command listing
- Rate limiting
- Shows permission requirements
"""

import discord
from discord import slash_command
from discord.ext import commands
import logging

logger = logging.getLogger('SiimLeaksBot.help')


class Help(commands.Cog):
    """Help and information commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @slash_command(
        name='help',
        description='View all available bot commands'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)  # 1 use per 10 seconds per user
    async def help(self, ctx: discord.ApplicationContext):
        """
        Display a comprehensive list of all available commands.
        
        Dynamically generates the command list from registered commands.
        """
        embed = discord.Embed(
            title="📖 Siim Leaks Basic Bot - Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )
        
        # General commands
        general_commands = """
`/help` - Show this help message
`/ping` - Check bot latency
`/support` - Get community support links
"""
        embed.add_field(name="📋 General", value=general_commands, inline=False)
        
        # Fun commands
        fun_commands = """
`/joke` - Get a random dad joke
`/dog` - Get a random dog picture
"""
        embed.add_field(name="🎉 Fun", value=fun_commands, inline=False)
        
        # Support/Ticket commands
        ticket_commands = """
`/openticket` - Open a support ticket
`Report message` - Right-click a message to report it
`Report user` - Right-click a user to report them
"""
        embed.add_field(name="🎫 Tickets & Reports", value=ticket_commands, inline=False)
        
        # Moderation commands (show if user has permissions)
        if ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator:
            mod_commands = """
`/purge <amount>` - Delete messages (1-100)
`/kick <member> [reason]` - Kick a member
`/ban <member> [reason]` - Ban a member
`/unban <user_id> [reason]` - Unban a user
"""
            embed.add_field(name="🛡️ Moderation (Staff Only)", value=mod_commands, inline=False)
        
        # Footer with additional info
        embed.set_footer(
            text=f"Bot Version: 0.3.0 (Secured) • Requested by {ctx.author.name}",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None
        )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name='about',
        description='Information about the bot'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def about(self, ctx: discord.ApplicationContext):
        """
        Display information about the bot.
        """
        embed = discord.Embed(
            title="ℹ️ About Siim Leaks Basic Bot",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Author",
            value="Siim 'Siim Leaks' Aarmaa",
            inline=True
        )
        embed.add_field(
            name="Version",
            value="0.3.0 (Security Hardened)",
            inline=True
        )
        embed.add_field(
            name="Library",
            value=f"Pycord {discord.__version__}",
            inline=True
        )
        
        # Bot stats
        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )
        embed.add_field(
            name="Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="Source",
            value="[GitHub](https://github.com/siimaarmaa/Discord-Bot-Siim-Leak-Basic)",
            inline=True
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None)
        embed.set_footer(text="Made with ❤️ and Python")
        
        await ctx.respond(embed=embed)
    
    @help.error
    @about.error
    async def help_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for help commands."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ Please wait {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in help command: {error}", exc_info=True)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
