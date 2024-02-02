import nextcord
from nextcord.ext import commands
import aiohttp

class RandomJoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="joke", description="Random Joke")
    async def joke(self, interaction: nextcord.Interaction):
        joke_url = 'https://icanhazdadjoke.com/'
        headers = {'Accept': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(joke_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        joke = data.get('joke', 'No joke found.')
                        await interaction.send(joke)
                    else:
                        await interaction.send("Failed to fetch a joke.")
            except Exception as e:
                await interaction.send(f"An error occurred: {e}")


def setup(bot):
    bot.add_cog(RandomJoke(bot))
