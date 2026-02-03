"""
Support ticket system.
Security features:
- Proper ownership tracking (prevents privilege escalation)
- Permission checks
- Rate limiting
- DM error handling
- Category permission inheritance
"""

import discord
from discord import slash_command
from discord.ext import commands
from discord.ui import View, Button
import os
import logging
from typing import Optional

logger = logging.getLogger('SiimLeaksBot.ticket')

# Store ticket creators - in production, use a database
# Format: {channel_id: user_id}
ticket_owners: dict[int, int] = {}


class CloseTicketButton(discord.ui.Button):
    """Button to close a support ticket."""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="🔒 Close Ticket",
            custom_id="close_ticket"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle close button click."""
        channel_id = interaction.channel_id
        
        # Get the ticket owner
        owner_id = ticket_owners.get(channel_id)
        
        # Check permissions
        can_close = (
            interaction.user.guild_permissions.administrator or
            interaction.user.guild_permissions.manage_channels or
            (owner_id and interaction.user.id == owner_id)
        )
        
        if not can_close:
            await interaction.response.send_message(
                "❌ You don't have permission to close this ticket.\n"
                "Only the ticket creator or staff can close tickets.",
                ephemeral=True
            )
            return
        
        # Acknowledge first
        await interaction.response.send_message(
            "🔒 Closing this ticket...",
            ephemeral=True
        )
        
        # Try to notify the ticket owner via DM
        if owner_id:
            try:
                user = await interaction.client.fetch_user(owner_id)
                if user:
                    embed = discord.Embed(
                        title="🎫 Ticket Closed",
                        description=(
                            f"Your support ticket in **{interaction.guild.name}** has been closed.\n\n"
                            f"If you have further questions, feel free to open a new ticket."
                        ),
                        color=discord.Color.orange()
                    )
                    await user.send(embed=embed)
            except discord.Forbidden:
                logger.info(f"Could not DM user {owner_id} about ticket closure (DMs disabled)")
            except discord.HTTPException as e:
                logger.warning(f"Failed to DM user {owner_id}: {e}")
        
        # Clean up the owner tracking
        if channel_id in ticket_owners:
            del ticket_owners[channel_id]
        
        # Log and delete the channel
        logger.info(
            f"TICKET CLOSED: #{interaction.channel.name} closed by "
            f"{interaction.user.name} ({interaction.user.id})"
        )
        
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to delete this channel.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            logger.error(f"Failed to delete ticket channel: {e}")


class TicketView(View):
    """Persistent view for ticket channels."""
    
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(CloseTicketButton())


class Ticket(commands.Cog):
    """Support ticket system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Configuration
        self.category_name = os.getenv('TICKET_CATEGORY_NAME', 'Support Tickets')
        self.staff_role_name = os.getenv('TICKET_STAFF_ROLE', None)
        
        # Register the persistent view
        self.bot.add_view(TicketView())
    
    async def _get_or_create_category(self, guild: discord.Guild) -> Optional[discord.CategoryChannel]:
        """Get or create the ticket category."""
        category = discord.utils.get(guild.categories, name=self.category_name)
        
        if category is None:
            try:
                # Create category with restricted permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_channels=True
                    )
                }
                
                # Add staff role if configured
                if self.staff_role_name:
                    staff_role = discord.utils.get(guild.roles, name=self.staff_role_name)
                    if staff_role:
                        overwrites[staff_role] = discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True
                        )
                
                category = await guild.create_category(
                    self.category_name,
                    overwrites=overwrites,
                    reason="Created for support ticket system"
                )
                logger.info(f"Created ticket category in {guild.name}")
            except discord.Forbidden:
                logger.error(f"Missing permissions to create category in {guild.name}")
                return None
            except discord.HTTPException as e:
                logger.error(f"Failed to create ticket category: {e}")
                return None
        
        return category
    
    async def _create_ticket_channel(
        self,
        guild: discord.Guild,
        user: discord.Member
    ) -> Optional[discord.TextChannel]:
        """Create a new ticket channel for a user."""
        category = await self._get_or_create_category(guild)
        
        if category is None:
            return None
        
        # Check if user already has an open ticket
        existing = discord.utils.get(
            category.text_channels,
            name=f"ticket-{user.id}"
        )
        if existing:
            return existing  # Return existing ticket
        
        # Set up permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        # Add staff role if configured
        if self.staff_role_name:
            staff_role = discord.utils.get(guild.roles, name=self.staff_role_name)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True
                )
        
        try:
            channel = await category.create_text_channel(
                f"ticket-{user.id}",
                overwrites=overwrites,
                topic=f"Support ticket for {user.name} ({user.id})",
                reason=f"Support ticket opened by {user}"
            )
            
            # Track the ticket owner
            ticket_owners[channel.id] = user.id
            
            logger.info(
                f"TICKET CREATED: #{channel.name} for {user.name} ({user.id}) "
                f"in {guild.name}"
            )
            
            return channel
            
        except discord.Forbidden:
            logger.error(f"Missing permissions to create ticket channel in {guild.name}")
            return None
        except discord.HTTPException as e:
            logger.error(f"Failed to create ticket channel: {e}")
            return None
    
    @slash_command(
        name='openticket',
        description='Open a support ticket'
    )
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 ticket per minute per user
    @commands.guild_only()
    async def open_ticket(self, ctx: discord.ApplicationContext):
        """
        Open a new support ticket.
        
        Creates a private channel where the user can communicate with staff.
        """
        await ctx.defer(ephemeral=True)
        
        # Check if user already has an open ticket
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category:
            existing = discord.utils.get(
                category.text_channels,
                name=f"ticket-{ctx.author.id}"
            )
            if existing:
                await ctx.respond(
                    f"📋 You already have an open ticket: {existing.mention}\n"
                    f"Please use that channel or close it before opening a new one.",
                    ephemeral=True
                )
                return
        
        # Create the ticket channel
        channel = await self._create_ticket_channel(ctx.guild, ctx.author)
        
        if channel is None:
            await ctx.respond(
                "❌ Failed to create a ticket. Please contact a server administrator.",
                ephemeral=True
            )
            return
        
        # Create welcome embed
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=(
                f"Hello {ctx.author.mention}!\n\n"
                f"Thank you for opening a support ticket. "
                f"Please describe your issue in detail and a staff member "
                f"will assist you as soon as possible.\n\n"
                f"**Please include:**\n"
                f"• A clear description of your issue\n"
                f"• Any relevant screenshots or information\n"
                f"• Steps to reproduce the problem (if applicable)"
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Ticket ID: {channel.id}")
        
        # Send the welcome message with close button
        view = TicketView()
        await channel.send(embed=embed, view=view)
        
        # Notify staff if role is configured
        if self.staff_role_name:
            staff_role = discord.utils.get(ctx.guild.roles, name=self.staff_role_name)
            if staff_role:
                await channel.send(
                    f"📢 {staff_role.mention} - A new ticket has been opened!",
                    allowed_mentions=discord.AllowedMentions(roles=True)
                )
        
        # Respond to the user
        await ctx.respond(
            f"✅ Your ticket has been created: {channel.mention}\n"
            f"Please describe your issue there.",
            ephemeral=True
        )
    
    @slash_command(
        name='closeticket',
        description='Close the current support ticket'
    )
    @commands.guild_only()
    async def close_ticket(self, ctx: discord.ApplicationContext):
        """
        Close the current ticket channel.
        
        Can only be used in ticket channels by the ticket owner or staff.
        """
        # Check if this is a ticket channel
        if not ctx.channel.name.startswith('ticket-'):
            await ctx.respond(
                "❌ This command can only be used in ticket channels.",
                ephemeral=True
            )
            return
        
        # Get the ticket owner
        owner_id = ticket_owners.get(ctx.channel.id)
        
        # Check permissions
        can_close = (
            ctx.author.guild_permissions.administrator or
            ctx.author.guild_permissions.manage_channels or
            (owner_id and ctx.author.id == owner_id)
        )
        
        if not can_close:
            await ctx.respond(
                "❌ You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        await ctx.respond("🔒 Closing this ticket...")
        
        # Notify owner via DM if they're not the one closing
        if owner_id and ctx.author.id != owner_id:
            try:
                user = await self.bot.fetch_user(owner_id)
                if user:
                    embed = discord.Embed(
                        title="🎫 Ticket Closed",
                        description=(
                            f"Your support ticket in **{ctx.guild.name}** has been closed "
                            f"by a staff member.\n\n"
                            f"If you have further questions, feel free to open a new ticket."
                        ),
                        color=discord.Color.orange()
                    )
                    await user.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass  # Can't DM user, that's okay
        
        # Clean up
        if ctx.channel.id in ticket_owners:
            del ticket_owners[ctx.channel.id]
        
        logger.info(
            f"TICKET CLOSED: #{ctx.channel.name} closed by "
            f"{ctx.author.name} ({ctx.author.id}) via command"
        )
        
        try:
            await ctx.channel.delete(reason=f"Ticket closed by {ctx.author}")
        except discord.Forbidden:
            await ctx.respond(
                "❌ I don't have permission to delete this channel.",
                ephemeral=True
            )
    
    @open_ticket.error
    async def ticket_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for ticket commands."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"⏱️ Please wait {error.retry_after:.0f} seconds before opening another ticket.",
                ephemeral=True
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.respond(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in ticket command: {error}", exc_info=True)
            await ctx.respond(
                "❌ An error occurred while processing your request.",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(Ticket(bot))
