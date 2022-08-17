import requests
from nextcord import Interaction, slash_command
from nextcord.ext import commands


class DogPic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='dog', description='Random dog picture', guild_ids=[])
    async def dog(self, ctx: Interaction):
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        image_link = response.json()['message']
        await ctx.response.send_message(image_link)


def setup(bot):
    bot.add_cog(DogPic(bot))
