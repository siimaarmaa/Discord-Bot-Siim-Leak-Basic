"""
Fun command to fetch random dog pictures.
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

logger = logging.getLogger('SiimLeaksBot.dogpic')


class DogPic(commands.Cog):
    """Fun commands for getting random dog pictures."""
    
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
        name='dog',
        description='Get a random dog picture 🐕'
    )
    @commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
    async def dog(self, ctx: discord.ApplicationContext):
        """
        Fetch and display a random dog picture.
        
        Uses the Dog CEO API: https://dog.ceo/dog-api/
        """
        await ctx.defer()  # This might take a moment
        
        try:
            async with self.session.get('https://dog.ceo/api/breeds/image/random') as response:
                if response.status != 200:
                    logger.warning(f"Dog API returned status {response.status}")
                    await ctx.respond(
                        "🐕 Couldn't fetch a dog picture right now. Try again later!",
                        ephemeral=True
                    )
                    return
                
                data = await response.json()
                
                # Validate response structure
                if data.get('status') != 'success' or 'message' not in data:
                    logger.warning(f"Unexpected API response: {data}")
                    await ctx.respond(
                        "🐕 Got an unexpected response. Try again!",
                        ephemeral=True
                    )
                    return
                
                image_url = data['message']
                
                # Validate URL format (basic check)
                if not image_url.startswith('https://'):
                    logger.warning(f"Invalid image URL: {image_url}")
                    await ctx.respond(
                        "🐕 Got an invalid image URL. Try again!",
                        ephemeral=True
                    )
                    return
                
                # Create a nice embed
                embed = discord.Embed(
                    title="🐕 Random Dog Picture",
                    color=discord.Color.from_rgb(139, 90, 43)  # Brown color
                )
                embed.set_image(url=image_url)
                embed.set_footer(text="Powered by Dog CEO API")
                
                await ctx.respond(embed=embed)
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching dog picture: {e}")
            await ctx.respond(
                "🐕 Network error! Couldn't fetch a dog picture.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Unexpected error in dog command: {e}", exc_info=True)
            await ctx.respond(
                "🐕 Something went wrong. Try again later!",
                ephemeral=True
            )
    
    @dog.error
    async def dog_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Handle errors for the dog command."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"🐕 Slow down! Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in dog command: {error}", exc_info=True)


def setup(bot: commands.Bot):
    bot.add_cog(DogPic(bot))
