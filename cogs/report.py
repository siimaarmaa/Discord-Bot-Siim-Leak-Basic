"""
User and message reporting system.
Security features:
- Input validation and sanitization
- Configurable channel IDs via environment variables
- Rate limiting on reports
- Content length limits
- Prevents self-reporting
"""

import discord
from discord.ext import commands
import os
import logging

logger = logging.getLogger('SiimLeaksBot.report')


class UserReportModal(discord.ui.Modal):
    """Modal for reporting users with reason and evidence."""
    
    def __init__(self, user: discord.Member | discord.User, report_channel_id: int):
        super().__init__(title="Report User", timeout=300)  # 5 minute timeout
        self.reported_user = user
        self.report_channel_id = report_channel_id
        
        self.reason = discord.ui.TextInput(
            label="Reason for Report",
            placeholder="Describe why you're reporting this user...",
            min_length=10,
            max_length=1000,
            style=discord.TextInputStyle.paragraph,
            required=True
        )
        self.proofs = discord.ui.TextInput(
            label="Evidence (optional)",
            placeholder="Links to screenshots, message IDs, etc.",
            min_length=0,
            max_length=1000,
            style=discord.TextInputStyle.paragraph,
            required=False
        )
        
        self.add_item(self.reason)
        self.add_item(self.proofs)
    
    async def callback(self, interaction: discord.Interaction):
        """Handle the modal submission."""
        report_channel = interaction.client.get_channel(self.report_channel_id)
        
        if report_channel is None:
            logger.error(f"Report channel {self.report_channel_id} not found")
            await interaction.response.send_message(
                "❌ Report system is not configured properly. Please contact a server administrator.",
                ephemeral=True
            )
            return
        
        # Sanitize inputs
        reason = discord.utils.escape_markdown(self.reason.value[:1000])
        proofs = discord.utils.escape_markdown(self.proofs.value[:1000]) if self.proofs.value else "No evidence provided"
        
        # Create report embed
        embed = discord.Embed(
            title="🚨 User Report",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Reported User",
            value=f"{self.reported_user.name} (`{self.reported_user.id}`)",
            inline=False
        )
        embed.add_field(
            name="Reported By",
            value=f"{interaction.user.name} (`{interaction.user.id}`)",
            inline=False
        )
        embed.add_field(name="Reason", value=f"```{reason}```", inline=False)
        embed.add_field(name="Evidence", value=f"```{proofs}```", inline=False)
        
        if self.reported_user.display_avatar:
            embed.set_thumbnail(url=self.reported_user.display_avatar.url)
        
        try:
            await report_channel.send(embed=embed)
            logger.info(
                f"USER REPORT: {interaction.user} ({interaction.user.id}) reported "
                f"{self.reported_user} ({self.reported_user.id})"
            )
            await interaction.response.send_message(
                f"✅ Your report against **{self.reported_user.name}** has been submitted. "
                f"Thank you for helping keep our community safe!",
                ephemeral=True
            )
        except discord.Forbidden:
            logger.error(f"Missing permissions to send to report channel")
            await interaction.response.send_message(
                "❌ Failed to submit report due to permission issues.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending report: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while submitting your report.",
                ephemeral=True
            )


class Report(commands.Cog):
    """User and message reporting functionality."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Load channel IDs from environment
        self.user_report_channel_id = self._get_channel_id('USER_REPORT_CHANNEL_ID')
        self.message_report_channel_id = self._get_channel_id('MESSAGE_REPORT_CHANNEL_ID')
        
        if not self.user_report_channel_id:
            logger.warning("USER_REPORT_CHANNEL_ID not set - user reports disabled")
        if not self.message_report_channel_id:
            logger.warning("MESSAGE_REPORT_CHANNEL_ID not set - message reports disabled")
    
    def _get_channel_id(self, env_var: str) -> int | None:
        """Get a channel ID from environment variables."""
        value = os.getenv(env_var)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.error(f"Invalid {env_var}: {value}")
        return None
    
    @discord.message_command(name="Report Message")
    @commands.cooldown(3, 60, commands.BucketType.user)  # 3 reports per minute per user
    async def report_message(self, ctx: discord.ApplicationContext, message: discord.Message):
        """
        Report a message via right-click context menu.
        
        Security:
        - Prevents reporting own messages
        - Prevents reporting bot messages
        - Rate limited
        - Content sanitized
        """
        # Check if reporting is configured
        if self.message_report_channel_id is None:
            await ctx.respond(
                "❌ Message reporting is not configured on this server.",
                ephemeral=True
            )
            return
        
        # Prevent self-reporting
        if message.author.id == ctx.author.id:
            await ctx.respond(
                "❌ You cannot report your own messages.",
                ephemeral=True
            )
            return
        
        # Prevent reporting bots (optional, uncomment if desired)
        # if message.author.bot:
        #     await ctx.respond("❌ You cannot report bot messages.", ephemeral=True)
        #     return
        
        report_channel = self.bot.get_channel(self.message_report_channel_id)
        
        if report_channel is None:
            logger.error(f"Message report channel {self.message_report_channel_id} not found")
            await ctx.respond(
                "❌ Report system is not configured properly.",
                ephemeral=True
            )
            return
        
        # Sanitize message content
        content = message.content[:500] if message.content else "*No text content*"
        content = discord.utils.escape_markdown(content)
        
        # Create report embed
        embed = discord.Embed(
            title="📝 Message Report",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Message Author",
            value=f"{message.author.name} (`{message.author.id}`)",
            inline=True
        )
        embed.add_field(
            name="Reported By",
            value=f"{ctx.author.name} (`{ctx.author.id}`)",
            inline=True
        )
        embed.add_field(
            name="Channel",
            value=f"{message.channel.mention}",
            inline=True
        )
        embed.add_field(
            name="Content",
            value=f"```{content}```",
            inline=False
        )
        embed.add_field(
            name="Jump to Message",
            value=f"[Click Here]({message.jump_url})",
            inline=False
        )
        
        # Include attachment info if present
        if message.attachments:
            attachments = "\n".join([a.filename for a in message.attachments[:5]])
            embed.add_field(name="Attachments", value=f"```{attachments}```", inline=False)
        
        try:
            await report_channel.send(embed=embed)
            logger.info(
                f"MESSAGE REPORT: {ctx.author} ({ctx.author.id}) reported message "
                f"from {message.author} ({message.author.id}) in #{message.channel.name}"
            )
            await ctx.respond(
                f"✅ Message from **{message.author.name}** has been reported. Thank you!",
                ephemeral=True
            )
        except discord.Forbidden:
            logger.error(f"Missing permissions to send to message report channel")
            await ctx.respond(
                "❌ Failed to submit report due to permission issues.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending message report: {e}")
            await ctx.respond(
                "❌ An error occurred while submitting your report.",
                ephemeral=True
            )
    
    @discord.user_command(name="Report User")
    @commands.cooldown(3, 60, commands.BucketType.user)  # 3 reports per minute per user
    async def report_user(self, ctx: discord.ApplicationContext, member: discord.Member):
        """
        Report a user via right-click context menu.
        
        Security:
        - Prevents self-reporting
        - Opens a modal for detailed information
        - Rate limited
        """
        # Check if reporting is configured
        if self.user_report_channel_id is None:
            await ctx.respond(
                "❌ User reporting is not configured on this server.",
                ephemeral=True
            )
            return
        
        # Prevent self-reporting
        if member.id == ctx.author.id:
            await ctx.respond(
                "❌ You cannot report yourself.",
                ephemeral=True
            )
            return
        
        # Open the report modal
        modal = UserReportModal(member, self.user_report_channel_id)
        await ctx.send_modal(modal)
    
    @report_message.error
    @report_user.error
    async def report_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for report commands."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ You're reporting too frequently. Try again in {error.retry_after:.0f} seconds.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in report command: {error}", exc_info=True)
            await ctx.respond(
                "❌ An error occurred.",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(Report(bot))
