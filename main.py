# Discord Bot: Siim Leaks Basic (Discord bot)
# Author: Siim "Siim Leaks" Aarmaa - www.aarmaa.ee
# Start year: 17.08.2021
# Version number: v.0.2.10
# Last update: 16.08.2022

import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands
# import logging

# Secrets set up
load_dotenv()
token = os.getenv('token')
guild = os.getenv('guild')

# Discord bot code start
# Command prefix
intents = nextcord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)


# Bot Status Message
@bot.event
async def on_ready():
    global guild
    await bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Game('I was made in Python!!'))

    for guild in bot.guilds:
        if guild.name == guild:
            break

    print(
        f'{bot.user} is connected to following guild: \n'
        f'{guild.name}(id: {guild.id})'
    )


# Add auto role new member
@bot.event
async def on_member_join(member):
    role = nextcord.utils.get(member.guild.roles, name="Viewer")
    await member.add_roles(role)


# Leaver log
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(933020912700231721)
    await channel.send(f"{member.name} is leaver. Don't say goodbye!!")


# Cog start
bot.load_extension('moderated')  # Moderator commands in bot
bot.load_extension('reactrole')  # React role in bot
bot.load_extension('ping')  # Ping command in bot
bot.load_extension('coinflip')  # Coin Flip command in bot
bot.load_extension('randomjoke')  # Random Joke command in bot

# Cog end
# Only for debug
# logging.basicConfig(level=logging.DEBUG)

# Discord bot code end
bot.run(token)
