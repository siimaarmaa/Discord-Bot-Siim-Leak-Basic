"""
Moderation commands for server management.
Security features:
- Permission checks on all commands
- Input validation
- Rate limiting
- Confirmation dialogs
- Audit logging
"""

import discord
from discord import slash_command, Option
from discord.ext import commands
from discord.ui import Button, View
import logging

logger = logging.getLogger('SiimLeaksBot.moderated')


class ConfirmationView(View):
    """A view with confirm/cancel buttons for dangerous operations."""
    
    def __init__(self, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.value = None
        self.interaction = None
    
    @discord.ui.button(label='✅ Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        self.value = True
        self.interaction = interaction
        self.stop()
    
    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        self.value = False
        self.interaction = interaction
        self.stop()
    
    async def on_timeout(self):
        self.value = None


class Moderated(commands.Cog):
    """Moderation commands for server administrators."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @slash_command(
        name='purge',
        description='Delete messages from the current channel'
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.cooldown(1, 10, commands.BucketType.channel)  # 1 use per 10 seconds per channel
    async def purge(
        self,
        ctx: discord.ApplicationContext,
        amount: Option(
            int,
            description="Number of messages to delete (1-100)",
            min_value=1,
            max_value=100,
            required=True
        )
    ):
        """
        Delete a specified number of messages from the channel.
        
        Security:
        - Requires manage_messages permission
        - Limited to 100 messages per operation
        - Requires confirmation for large deletions
        - Logs all purge operations
        """
        # Additional validation (belt and suspenders)
        if not 1 <= amount <= 100:
            await ctx.respond(
                "❌ Amount must be between 1 and 100 messages.",
                ephemeral=True
            )
            return
        
        # For larger deletions, require confirmation
        if amount >= 10:
            view = ConfirmationView(timeout=30.0)
            await ctx.respond(
                f"⚠️ **Warning:** You are about to delete **{amount}** messages.\n"
                f"This action cannot be undone.\n\n"
                f"Are you sure you want to continue?",
                view=view,
                ephemeral=True
            )
            
            await view.wait()
            
            if view.value is None:
                await ctx.edit(content="⏱️ Confirmation timed out. No messages were deleted.", view=None)
                return
            elif not view.value:
                await ctx.edit(content="❌ Purge cancelled.", view=None)
                return
            
            # Update the original message
            await ctx.edit(content="🗑️ Deleting messages...", view=None)
        else:
            await ctx.respond("🗑️ Deleting messages...", ephemeral=True)
        
        try:
            # Purge messages
            deleted = await ctx.channel.purge(limit=amount)
            
            # Log the action
            logger.info(
                f"PURGE: {ctx.author} ({ctx.author.id}) deleted {len(deleted)} messages "
                f"in #{ctx.channel.name} ({ctx.channel.id})"
            )
            
            await ctx.edit(content=f"✅ Successfully deleted **{len(deleted)}** messages.")
            
        except discord.Forbidden:
            await ctx.edit(content="❌ I don't have permission to delete messages in this channel.")
        except discord.HTTPException as e:
            logger.error(f"HTTP error during purge: {e}")
            await ctx.edit(content="❌ An error occurred while deleting messages.")
    
    @slash_command(
        name='unban',
        description='Unban a user from the server'
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
    async def unban(
        self,
        ctx: discord.ApplicationContext,
        user_id: Option(
            str,
            description="The User ID of the person to unban",
            required=True
        ),
        reason: Option(
            str,
            description="Reason for unbanning",
            required=False,
            default="No reason provided"
        )
    ):
        """
        Unban a user from the server.
        
        Security:
        - Requires ban_members permission
        - Validates user ID format
        - Logs all unban operations
        """
        # Validate user ID format
        try:
            user_id_int = int(user_id.strip())
        except ValueError:
            await ctx.respond(
                "❌ Invalid user ID. Please provide a valid numeric Discord user ID.",
                ephemeral=True
            )
            return
        
        # Check if user ID is reasonable
        if user_id_int < 10000000000000000 or user_id_int > 9999999999999999999:
            await ctx.respond(
                "❌ Invalid user ID format.",
                ephemeral=True
            )
            return
        
        await ctx.defer(ephemeral=True)
        
        try:
            # Fetch user
            user = await self.bot.fetch_user(user_id_int)
            
            # Attempt to unban
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}: {reason}")
            
            # Log the action
            logger.info(
                f"UNBAN: {ctx.author} ({ctx.author.id}) unbanned {user} ({user.id}) "
                f"in {ctx.guild.name}. Reason: {reason}"
            )
            
            embed = discord.Embed(
                title="✅ User Unbanned",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="User", value=f"{user.name} ({user.id})", inline=False)
            embed.add_field(name="Unbanned by", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.respond(embed=embed)
            
        except discord.NotFound:
            await ctx.respond(
                "❌ User not found or not banned.",
                ephemeral=True
            )
        except discord.Forbidden:
            await ctx.respond(
                "❌ I don't have permission to unban users.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            logger.error(f"HTTP error during unban: {e}")
            await ctx.respond(
                "❌ An error occurred while unbanning the user.",
                ephemeral=True
            )
    
    @slash_command(
        name='kick',
        description='Kick a member from the server'
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            description="The member to kick",
            required=True
        ),
        reason: Option(
            str,
            description="Reason for kicking",
            required=False,
            default="No reason provided"
        )
    ):
        """
        Kick a member from the server.
        
        Security:
        - Requires kick_members permission
        - Cannot kick self, bots with higher roles, or server owner
        - Logs all kick operations
        """
        # Prevent kicking self
        if member.id == ctx.author.id:
            await ctx.respond("❌ You cannot kick yourself.", ephemeral=True)
            return
        
        # Prevent kicking the bot
        if member.id == self.bot.user.id:
            await ctx.respond("❌ I cannot kick myself.", ephemeral=True)
            return
        
        # Prevent kicking server owner
        if member.id == ctx.guild.owner_id:
            await ctx.respond("❌ You cannot kick the server owner.", ephemeral=True)
            return
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.respond(
                "❌ You cannot kick someone with an equal or higher role than you.",
                ephemeral=True
            )
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.respond(
                "❌ I cannot kick someone with an equal or higher role than me.",
                ephemeral=True
            )
            return
        
        try:
            await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
            
            logger.info(
                f"KICK: {ctx.author} ({ctx.author.id}) kicked {member} ({member.id}) "
                f"from {ctx.guild.name}. Reason: {reason}"
            )
            
            embed = discord.Embed(
                title="👢 Member Kicked",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Member", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name="Kicked by", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.respond(embed=embed)
            
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to kick this member.", ephemeral=True)
        except discord.HTTPException as e:
            logger.error(f"HTTP error during kick: {e}")
            await ctx.respond("❌ An error occurred while kicking the member.", ephemeral=True)
    
    @slash_command(
        name='ban',
        description='Ban a member from the server'
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            description="The member to ban",
            required=True
        ),
        reason: Option(
            str,
            description="Reason for banning",
            required=False,
            default="No reason provided"
        ),
        delete_messages: Option(
            int,
            description="Days of messages to delete (0-7)",
            min_value=0,
            max_value=7,
            required=False,
            default=0
        )
    ):
        """
        Ban a member from the server.
        
        Security:
        - Requires ban_members permission
        - Cannot ban self, bots with higher roles, or server owner
        - Requires confirmation
        - Logs all ban operations
        """
        # Prevent banning self
        if member.id == ctx.author.id:
            await ctx.respond("❌ You cannot ban yourself.", ephemeral=True)
            return
        
        # Prevent banning the bot
        if member.id == self.bot.user.id:
            await ctx.respond("❌ I cannot ban myself.", ephemeral=True)
            return
        
        # Prevent banning server owner
        if member.id == ctx.guild.owner_id:
            await ctx.respond("❌ You cannot ban the server owner.", ephemeral=True)
            return
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.respond(
                "❌ You cannot ban someone with an equal or higher role than you.",
                ephemeral=True
            )
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.respond(
                "❌ I cannot ban someone with an equal or higher role than me.",
                ephemeral=True
            )
            return
        
        # Require confirmation for bans
        view = ConfirmationView(timeout=30.0)
        await ctx.respond(
            f"⚠️ **Warning:** You are about to ban **{member.name}**.\n"
            f"Reason: {reason}\n"
            f"Delete messages: {delete_messages} days\n\n"
            f"Are you sure?",
            view=view,
            ephemeral=True
        )
        
        await view.wait()
        
        if view.value is None:
            await ctx.edit(content="⏱️ Confirmation timed out. No action taken.", view=None)
            return
        elif not view.value:
            await ctx.edit(content="❌ Ban cancelled.", view=None)
            return
        
        try:
            await member.ban(
                reason=f"Banned by {ctx.author}: {reason}",
                delete_message_days=delete_messages
            )
            
            logger.info(
                f"BAN: {ctx.author} ({ctx.author.id}) banned {member} ({member.id}) "
                f"from {ctx.guild.name}. Reason: {reason}"
            )
            
            embed = discord.Embed(
                title="🔨 Member Banned",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Member", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name="Banned by", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.edit(content=None, embed=embed, view=None)
            
        except discord.Forbidden:
            await ctx.edit(content="❌ I don't have permission to ban this member.", view=None)
        except discord.HTTPException as e:
            logger.error(f"HTTP error during ban: {e}")
            await ctx.edit(content="❌ An error occurred while banning the member.", view=None)
    
    # Error handlers for this cog
    @purge.error
    @unban.error
    @kick.error
    @ban.error
    async def moderation_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for moderation commands."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond(
                "🚫 You don't have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.respond(
                f"⚠️ I'm missing required permissions: {', '.join(error.missing_permissions)}",
                ephemeral=True
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in moderation command: {error}", exc_info=True)
            await ctx.respond(
                "❌ An unexpected error occurred.",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(Moderated(bot))
