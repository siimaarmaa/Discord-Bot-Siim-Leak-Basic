from nextcord.ext import commands
import os
from dotenv import load_dotenv
import requests
import json

# Secret API
load_dotenv()
rapid_key = os.getenv('rapid_key')


class CoinFlip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='coin')
    async def coin(self, ctx: commands.Context):
        coin_var = 'https://coin-flip1.p.rapidapi.com/headstails'
        headers = {
            'x-rapidapi-host': 'coin-flip1.p.rapidapi.com',
            'x-rapidapi-key': rapid_key
        }
        coin_chat = requests.request('get', coin_var, headers=headers)
        await ctx.send(json.loads(coin_chat.text)['outcome'])


def setup(bot: commands.Bot):
    bot.add_cog(CoinFlip(bot))
