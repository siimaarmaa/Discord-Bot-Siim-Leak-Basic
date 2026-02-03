"""
Reaction role assignment system.
Security features:
- Role whitelist to prevent privilege escalation
- Configurable channel ID via environment variable
- Bot self-check
- Role hierarchy validation
- Logging
"""

import discord
from discord.ext import commands
import os
import logging

logger = logging.getLogger('SiimLeaksBot.reactrole')


class ReactRole(commands.Cog):
    """
    Reaction-based role assignment.
    
    Users can react to a specific message with emoji to receive/remove roles.
    Only roles in the whitelist can be assigned to prevent privilege escalation.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Load configuration from environment
        self.react_role_channel_id = self._get_channel_id()
        self.react_role_message_id = self._get_message_id()
        
        # Role whitelist: maps emoji names to role names
        # SECURITY: Only roles in this whitelist can be assigned via reactions
        # Configure this via environment variable as JSON or comma-separated
        self.role_whitelist = self._load_role_whitelist()
        
        if self.react_role_channel_id:
            logger.info(f"ReactRole configured for channel: {self.react_role_channel_id}")
        else:
            logger.warning("ReactRole: No channel configured (REACT_ROLE_CHANNEL_ID not set)")
    
    def _get_channel_id(self) -> int | None:
        """Get reaction role channel ID from environment."""
        channel_id = os.getenv('REACT_ROLE_CHANNEL_ID')
        if channel_id:
            try:
                return int(channel_id)
            except ValueError:
                logger.error(f"Invalid REACT_ROLE_CHANNEL_ID: {channel_id}")
        return None
    
    def _get_message_id(self) -> int | None:
        """Get reaction role message ID from environment (optional)."""
        message_id = os.getenv('REACT_ROLE_MESSAGE_ID')
        if message_id:
            try:
                return int(message_id)
            except ValueError:
                logger.error(f"Invalid REACT_ROLE_MESSAGE_ID: {message_id}")
        return None
    
    def _load_role_whitelist(self) -> dict[str, str]:
        """
        Load the emoji-to-role whitelist from environment.
        
        Format: REACT_ROLE_WHITELIST="emoji1:RoleName1,emoji2:RoleName2"
        Example: REACT_ROLE_WHITELIST="🎮:Gamer,🎵:Music,📚:Reader"
        """
        whitelist_str = os.getenv('REACT_ROLE_WHITELIST', '')
        whitelist = {}
        
        if whitelist_str:
            for pair in whitelist_str.split(','):
                pair = pair.strip()
                if ':' in pair:
                    emoji, role_name = pair.split(':', 1)
                    whitelist[emoji.strip()] = role_name.strip()
        
        if whitelist:
            logger.info(f"ReactRole whitelist loaded: {list(whitelist.keys())}")
        else:
            logger.warning("ReactRole: No role whitelist configured (REACT_ROLE_WHITELIST not set)")
        
        return whitelist
    
    def _is_valid_channel(self, channel_id: int) -> bool:
        """Check if the reaction is in the configured channel."""
        if self.react_role_channel_id is None:
            return False
        return channel_id == self.react_role_channel_id
    
    def _is_valid_message(self, message_id: int) -> bool:
        """Check if the reaction is on the configured message (if set)."""
        if self.react_role_message_id is None:
            return True  # If no specific message configured, allow any in channel
        return message_id == self.react_role_message_id
    
    def _get_emoji_name(self, emoji: discord.PartialEmoji) -> str:
        """Get the emoji name/character for lookup."""
        # For custom emoji, use the name; for Unicode emoji, use the string
        return emoji.name if emoji.is_custom_emoji() else str(emoji)
    
    async def _get_role_for_emoji(self, guild: discord.Guild, emoji: discord.PartialEmoji) -> discord.Role | None:
        """
        Get the role corresponding to an emoji, if it's in the whitelist.
        
        SECURITY: This is the main protection against privilege escalation.
        """
        emoji_key = self._get_emoji_name(emoji)
        
        # Check if emoji is in whitelist
        if emoji_key not in self.role_whitelist:
            logger.debug(f"Emoji '{emoji_key}' not in whitelist")
            return None
        
        role_name = self.role_whitelist[emoji_key]
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role is None:
            logger.warning(f"Whitelisted role '{role_name}' not found in guild '{guild.name}'")
            return None
        
        # SECURITY: Don't allow assignment of high-privilege roles
        # even if someone misconfigures the whitelist
        dangerous_permissions = [
            'administrator',
            'manage_guild',
            'manage_roles',
            'manage_channels',
            'ban_members',
            'kick_members',
            'manage_webhooks',
            'manage_messages',
        ]
        
        for perm in dangerous_permissions:
            if getattr(role.permissions, perm, False):
                logger.warning(
                    f"SECURITY: Blocked assignment of privileged role '{role.name}' via reaction"
                )
                return None
        
        return role
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle reaction additions for role assignment."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is the right channel/message
        if not self._is_valid_channel(payload.channel_id):
            return
        
        if not self._is_valid_message(payload.message_id):
            return
        
        # Get the guild
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        # Get the role (with security checks)
        role = await self._get_role_for_emoji(guild, payload.emoji)
        if role is None:
            return
        
        # Get the member
        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return
        
        # Check if bot can assign this role (role hierarchy)
        if role >= guild.me.top_role:
            logger.warning(f"Cannot assign role '{role.name}' - higher than bot's role")
            return
        
        # Assign the role
        try:
            if role not in member.roles:
                await member.add_roles(role, reason="Reaction role assignment")
                logger.info(f"Assigned role '{role.name}' to {member.name} ({member.id})")
        except discord.Forbidden:
            logger.error(f"Missing permissions to assign role '{role.name}'")
        except discord.HTTPException as e:
            logger.error(f"HTTP error assigning role: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle reaction removals for role removal."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is the right channel/message
        if not self._is_valid_channel(payload.channel_id):
            return
        
        if not self._is_valid_message(payload.message_id):
            return
        
        # Get the guild
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        # Get the role (with security checks)
        role = await self._get_role_for_emoji(guild, payload.emoji)
        if role is None:
            return
        
        # Get the member
        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return
        
        # Check if bot can remove this role (role hierarchy)
        if role >= guild.me.top_role:
            logger.warning(f"Cannot remove role '{role.name}' - higher than bot's role")
            return
        
        # Remove the role
        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Reaction role removal")
                logger.info(f"Removed role '{role.name}' from {member.name} ({member.id})")
        except discord.Forbidden:
            logger.error(f"Missing permissions to remove role '{role.name}'")
        except discord.HTTPException as e:
            logger.error(f"HTTP error removing role: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(ReactRole(bot))
