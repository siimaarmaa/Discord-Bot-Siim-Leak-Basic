import requests
import json
import nextcord
from nextcord.ext import commands


class RandomJoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="joke", description="Random Joke")
    async def joke(self, interaction: nextcord.Interaction):
        joke_url = 'https://icanhazdadjoke.com/'
        headers = {
            'Accept': 'application/json'
        }
        joke_chat = requests.request('get', joke_url, headers=headers)
        await interaction.send(json.loads(joke_chat.text)['joke'])


def setup(bot):
    bot.add_cog(RandomJoke(bot))
