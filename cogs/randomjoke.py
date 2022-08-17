import requests
import json
from nextcord import Interaction, slash_command
from nextcord.ext import commands


class RandomJoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='joke', description='Random Joke', guild_ids=[])
    async def joke(
            self,
            ctx: Interaction
    ):
        joke_url = 'https://icanhazdadjoke.com/'
        headers = {
            'Accept': 'application/json'
        }
        joke_chat = requests.request('get', joke_url, headers=headers)
        await ctx.response.send_message(json.loads(joke_chat.text)['joke'])


def setup(bot):
    bot.add_cog(RandomJoke(bot))
