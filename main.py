# Discord Bot: Siim Leaks Basic (Discord bot)
# Author: Siim "Siim Leaks" Aarmaa - www.aarmaa.ee
# Facebook: Aarmaa - https://www.facebook.com/aarmaa.ee
# Start year: 17.08.2021
# Version number: v.0.2.39
# Last update: 07.12.2023

import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

# Secrets set up
load_dotenv()
token = os.getenv('token')
guild = os.getenv('guild')

# Discord bot code start
# Command prefix
# Gateway intents
intents = nextcord.Intents().all()
bot = commands.Bot(intents=intents)


# Bot Status Message
@bot.event
async def on_ready():
    global guild
    await bot.change_presence(status=nextcord.Status.do_not_disturb, activity=nextcord.Game('I was made in Python!!'))

    for guild in bot.guilds:
        if guild.name == guild:
            break

    print(
        f'{bot.user} is connected to following guild: \n'
        f'{guild.name}(id: {guild.id})'
    )


# Leaver log
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1182057463147679754)
    await channel.send(f"{member.name} is leaver. Don't say goodbye!!")


# Logs for mods and admins
@bot.event
async def on_message_delete(message):
    embed = nextcord.Embed(title=f'{message.author.name} has deleted a message | {message.author.id}',
                           description=f'{message.content}')
    channel = bot.get_channel(1182057463147679754)
    await channel.send(embed=embed)


@bot.event
async def on_message_edit(message_before, message_after):
    embed = nextcord.Embed(title=f'{message_before.author.name} has edited a message | {message_before.author.id}')
    embed.add_field(name='Before Message', value=f'{message_before.content}', inline=False)
    embed.add_field(name='After Message', value=f'{message_after.content}', inline=False)
    channel = bot.get_channel(1182057463147679754)
    await channel.send(embed=embed)


# Cog start
bot.load_extension('cogs.moderated')  # Admins and Moderators commands
bot.load_extension('cogs.dogpic')  # Random Dog picture
bot.load_extension('cogs.ping')  # Test bot ping
bot.load_extension('cogs.randomjoke')  # Random Joke
bot.load_extension('cogs.reactrole')  # Self role react for fun
bot.load_extension('cogs.support')  # Siim Leaks Basic Support
bot.load_extension('cogs.help')  # Bot commands help menu
bot.load_extension('cogs.report')  # Report user and message
#bot.load_extension('cogs.ticket')  # Create bug ticket or problem ticket
bot.load_extension('cogs.ticket2')  # Create bug ticket or problem ticket
# Cog end

# Discord bot code end
bot.run(token)
