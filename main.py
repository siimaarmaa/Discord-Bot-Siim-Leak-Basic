# Discord Bot: Siim Leaks Basic (Discord bot) - SECURED VERSION
# Original Author: Siim "Siim Leaks" Aarmaa - www.aarmaa.ee
# Security Audit & Fixes: Claude AI Security Analyst
# Version number: v.0.3.0 (Security Hardened)
# Last update: 2026-02-03

import discord
import os
import sys
import signal
import logging
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8', mode='a')
    ]
)
logger = logging.getLogger('SiimLeaksBot')

# =============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# =============================================================================
load_dotenv()


def get_env_var(name: str, required: bool = True, default: str = None, cast_type: type = str):
    """
    Safely retrieve and validate environment variables.
    
    Args:
        name: Environment variable name
        required: Whether the variable is required
        default: Default value if not required and not set
        cast_type: Type to cast the value to (str, int, etc.)
    
    Returns:
        The environment variable value, cast to the specified type
        
    Raises:
        SystemExit: If a required variable is missing
    """
    value = os.getenv(name)
    
    if value is None:
        if required:
            logger.critical(f"Required environment variable '{name}' is not set!")
            sys.exit(1)
        return default
    
    try:
        if cast_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        return cast_type(value)
    except (ValueError, TypeError) as e:
        logger.critical(f"Environment variable '{name}' has invalid value: {e}")
        sys.exit(1)


# Load and validate all environment variables
TOKEN = get_env_var('TOKEN', required=True)
GUILD_NAME = get_env_var('GUILD', required=False, default=None)
GUILD_ID = get_env_var('GUILD_ID', required=False, default=None, cast_type=int)

# Channel IDs (optional - features disabled if not set)
ACTIVITY_LOGS_CHANNEL_ID = get_env_var('ACTIVITY_LOGS_CHANNEL_ID', required=False, default=None, cast_type=int)
MESSAGE_DELETE_CHANNEL_ID = get_env_var('MESSAGE_DELETE_CHANNEL_ID', required=False, default=None, cast_type=int)
MESSAGE_EDIT_CHANNEL_ID = get_env_var('MESSAGE_EDIT_CHANNEL_ID', required=False, default=None, cast_type=int)

# =============================================================================
# BOT CONFIGURATION - MINIMAL INTENTS (Principle of Least Privilege)
# =============================================================================
intents = discord.Intents.default()
intents.message_content = True  # Required for message logging
intents.members = True  # Required for member events
intents.guilds = True  # Required for guild operations
intents.reactions = True  # Required for reaction roles

# Create bot instance
bot = commands.Bot(
    intents=intents,
    help_command=None  # We use a custom help command
)

# Store configuration in bot for access from cogs
bot.config = {
    'guild_name': GUILD_NAME,
    'guild_id': GUILD_ID,
    'activity_logs_channel_id': ACTIVITY_LOGS_CHANNEL_ID,
    'message_delete_channel_id': MESSAGE_DELETE_CHANNEL_ID,
    'message_edit_channel_id': MESSAGE_EDIT_CHANNEL_ID,
}

# =============================================================================
# EVENT HANDLERS
# =============================================================================

@bot.event
async def on_ready():
    """Called when the bot is ready and connected."""
    logger.info(f'{bot.user} is now online!')
    
    # Set bot presence
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help for commands"
        )
    )
    
    # Log connected guilds
    for guild in bot.guilds:
        logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')
        if bot.config['guild_name'] and guild.name == bot.config['guild_name']:
            logger.info(f'Primary guild found: {guild.name}')


@bot.event
async def on_member_remove(member: discord.Member):
    """Log when a member leaves the server."""
    if ACTIVITY_LOGS_CHANNEL_ID is None:
        return
    
    channel = bot.get_channel(ACTIVITY_LOGS_CHANNEL_ID)
    if channel is None:
        logger.warning(f"Activity logs channel {ACTIVITY_LOGS_CHANNEL_ID} not found")
        return
    
    try:
        embed = discord.Embed(
            title="Member Left",
            description=f"**{member.name}** has left the server.",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        embed.add_field(name="User ID", value=str(member.id), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        
        await channel.send(embed=embed)
    except discord.Forbidden:
        logger.warning(f"Missing permissions to send to activity logs channel")
    except Exception as e:
        logger.error(f"Error sending member leave log: {e}")


@bot.event
async def on_message_delete(message: discord.Message):
    """Log deleted messages for moderation purposes."""
    # Ignore bot messages
    if message.author.bot:
        return
    
    if MESSAGE_DELETE_CHANNEL_ID is None:
        return
    
    channel = bot.get_channel(MESSAGE_DELETE_CHANNEL_ID)
    if channel is None:
        logger.warning(f"Message delete log channel {MESSAGE_DELETE_CHANNEL_ID} not found")
        return
    
    # Sanitize content to prevent embed injection
    content = message.content[:1000] if message.content else "*No text content*"
    content = discord.utils.escape_markdown(content)
    content = discord.utils.escape_mentions(content)
    
    try:
        embed = discord.Embed(
            title="Message Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Author", value=f"{message.author.name} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=True)
        embed.add_field(name="Content", value=content, inline=False)
        
        await channel.send(embed=embed)
    except discord.Forbidden:
        logger.warning(f"Missing permissions to send to message delete log channel")
    except Exception as e:
        logger.error(f"Error sending message delete log: {e}")


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    """Log edited messages for moderation purposes."""
    # Ignore bot messages
    if before.author.bot:
        return
    
    # Ignore if content hasn't changed (e.g., embed updates)
    if before.content == after.content:
        return
    
    if MESSAGE_EDIT_CHANNEL_ID is None:
        return
    
    channel = bot.get_channel(MESSAGE_EDIT_CHANNEL_ID)
    if channel is None:
        logger.warning(f"Message edit log channel {MESSAGE_EDIT_CHANNEL_ID} not found")
        return
    
    # Sanitize content
    before_content = before.content[:500] if before.content else "*Empty*"
    after_content = after.content[:500] if after.content else "*Empty*"
    before_content = discord.utils.escape_markdown(before_content)
    after_content = discord.utils.escape_markdown(after_content)
    
    try:
        embed = discord.Embed(
            title="Message Edited",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Author", value=f"{before.author.name} ({before.author.id})", inline=False)
        embed.add_field(name="Channel", value=f"{before.channel.mention}", inline=True)
        embed.add_field(name="Before", value=before_content, inline=False)
        embed.add_field(name="After", value=after_content, inline=False)
        embed.add_field(name="Jump to Message", value=f"[Click here]({after.jump_url})", inline=False)
        
        await channel.send(embed=embed)
    except discord.Forbidden:
        logger.warning(f"Missing permissions to send to message edit log channel")
    except Exception as e:
        logger.error(f"Error sending message edit log: {e}")


# =============================================================================
# GLOBAL ERROR HANDLER
# =============================================================================

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    """Global error handler for application commands."""
    
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(
            f"⏱️ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(
            "🚫 You don't have permission to use this command.",
            ephemeral=True
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.respond(
            f"⚠️ I'm missing required permissions: {', '.join(error.missing_permissions)}",
            ephemeral=True
        )
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.respond(
            "📍 This command can only be used in a server.",
            ephemeral=True
        )
    else:
        # Log unexpected errors
        logger.error(f"Unhandled error in command {ctx.command}: {error}", exc_info=True)
        await ctx.respond(
            "❌ An unexpected error occurred. This has been logged.",
            ephemeral=True
        )


# =============================================================================
# COG LOADING
# =============================================================================

cog_extensions = [
    'cogs.moderated',
    'cogs.dogpic',
    'cogs.ping',
    'cogs.randomjoke',
    'cogs.reactrole',
    'cogs.support',
    'cogs.help',
    'cogs.report',
    'cogs.ticket'
]


@bot.event
async def on_connect():
    """Load cogs when bot connects."""
    for extension in cog_extensions:
        try:
            bot.load_extension(extension)
            logger.info(f"✅ Loaded extension: {extension}")
        except Exception as e:
            logger.error(f"❌ Failed to load extension {extension}: {e}")


# =============================================================================
# GRACEFUL SHUTDOWN
# =============================================================================

async def shutdown():
    """Gracefully shut down the bot."""
    logger.info("Shutting down bot...")
    await bot.close()


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    asyncio.create_task(shutdown())


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# =============================================================================
# BOT STARTUP
# =============================================================================

if __name__ == "__main__":
    logger.info("Starting Siim Leaks Basic Bot (Secured Version)...")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.critical("Invalid bot token! Please check your .env file.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)
