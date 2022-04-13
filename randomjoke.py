from nextcord.ext import commands
import os
from dotenv import load_dotenv
import requests
import json

# Secret API
load_dotenv()
rapid_key = os.getenv('rapid_key')


class RandomJoke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='joke')
    async def joke(self, ctx: commands.Context):
        joke_url = 'https://jokeapi-v2.p.rapidapi.com/joke/Any'
        querystring = {'type': 'single', 'format': 'json'}
        headers = {
            'x-rapidapi-host': 'jokeapi-v2.p.rapidapi.com',
            'x-rapidapi-key': rapid_key
        }
        joke_chat = requests.request('get', joke_url, headers=headers, params=querystring)
        await ctx.send(json.loads(joke_chat.text)['joke'])


def setup(bot: commands.Bot):
    bot.add_cog(RandomJoke(bot))
