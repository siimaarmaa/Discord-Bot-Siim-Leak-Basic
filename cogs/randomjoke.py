"""
Fun command to fetch random dad jokes.
Security features:
- Async HTTP requests (non-blocking)
- Rate limiting
- Error handling
- Response validation
"""

import discord
from discord import slash_command
from discord.ext import commands
import aiohttp
import logging

logger = logging.getLogger('SiimLeaksBot.randomjoke')


class RandomJoke(commands.Cog):
    """Fun commands for getting random jokes."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession = None
    
    async def cog_load(self):
        """Create aiohttp session when cog loads."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
    
    async def cog_unload(self):
        """Close aiohttp session when cog unloads."""
        if self.session:
            await self.session.close()
    
    @slash_command(
        name='joke',
        description='Get a random dad joke 😄'
    )
    @commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
    async def joke(self, ctx: discord.ApplicationContext):
        """
        Fetch and display a random dad joke.
        
        Uses the icanhazdadjoke API: https://icanhazdadjoke.com/
        """
        await ctx.defer()  # This might take a moment
        
        try:
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'SiimLeaksBasicBot/0.3.0'  # Good practice to identify the bot
            }
            
            async with self.session.get('https://icanhazdadjoke.com/', headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"Joke API returned status {response.status}")
                    await ctx.respond(
                        "😅 Couldn't fetch a joke right now. Try again later!",
                        ephemeral=True
                    )
                    return
                
                data = await response.json()
                
                # Validate response
                joke = data.get('joke')
                if not joke:
                    logger.warning(f"No joke in response: {data}")
                    await ctx.respond(
                        "😅 Got an empty joke. Try again!",
                        ephemeral=True
                    )
                    return
                
                # Sanitize and limit joke length
                joke = joke[:1000]  # Limit length
                joke = discord.utils.escape_markdown(joke)
                
                embed = discord.Embed(
                    title="😄 Random Dad Joke",
                    description=joke,
                    color=discord.Color.gold()
                )
                embed.set_footer(text="Powered by icanhazdadjoke.com")
                
                await ctx.respond(embed=embed)
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching joke: {e}")
            await ctx.respond(
                "😅 Network error! Couldn't fetch a joke.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Unexpected error in joke command: {e}", exc_info=True)
            await ctx.respond(
                "😅 Something went wrong. Try again later!",
                ephemeral=True
            )
    
    @joke.error
    async def joke_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for the joke command."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"😄 Slow down with the jokes! Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in joke command: {error}", exc_info=True)


def setup(bot: commands.Bot):
    bot.add_cog(RandomJoke(bot))
