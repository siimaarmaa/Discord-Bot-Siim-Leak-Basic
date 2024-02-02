# Discord Bot: Siim Leaks Basic (Discord bot)
# Author: Siim "Siim Leaks" Aarmaa - www.aarmaa.ee
# Facebook: Aarmaa - https://www.facebook.com/aarmaa.ee
# Start year: 17.08.2021
# Version number: v.0.2.43
# Last update: 02.02.2024

import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

# Load environment variables
load_dotenv()
token = os.getenv('TOKEN')
guild_name = os.getenv('GUILD')  # Renamed to avoid confusion with the guild object in on_ready

# Loading channel IDs from environment variables
activity_logs_channel_id = int(os.getenv('ACTIVITY_LOGS_CHANNEL_ID'))  # Added environment variable
message_delete_channel_id = int(os.getenv('MESSAGE_DELETE_CHANNEL_ID'))  # Added environment variable
message_edit_channel_id = int(os.getenv('MESSAGE_EDIT_CHANNEL_ID'))  # Added environment variable

# Discord bot code start
# Setting up Discord bot with intents
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)


# Bot Status Message
@bot.event
async def on_ready():
    global guild_name  # Reference the global variable
    await bot.change_presence(status=nextcord.Status.online, activity=nextcord.Game('I was made in Python!!'))

    for guild in bot.guilds:
        if guild.name == guild_name:  # Compare with the correct guild name
            print(f'{bot.user} is connected to the guild: {guild.name}(id: {guild.id})')
            break


# Leaver log
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(activity_logs_channel_id)
    if channel:
        await channel.send(f"{member.name} has left. Don't say goodbye!!")


# Logs for mods and admins
@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(message_delete_channel_id)
    if channel:
        embed = nextcord.Embed(title=f'{message.author.name} has deleted a message | {message.author.id}',
                               description=f'{message.content}')
        await channel.send(embed=embed)


@bot.event
async def on_message_edit(message_before, message_after):
    channel = bot.get_channel(message_edit_channel_id)
    if channel:
        embed = nextcord.Embed(title=f'{message_before.author.name} has edited a message | {message_before.author.id}')
        embed.add_field(name='Before Message', value=message_before.content, inline=False)
        embed.add_field(name='After Message', value=message_after.content, inline=False)
        await channel.send(embed=embed)


# Cog start
# Loading cogs
cog_extensions = ['cogs.moderated', 'cogs.dogpic', 'cogs.ping', 'cogs.randomjoke', 'cogs.reactrole',
                  'cogs.support', 'cogs.help', 'cogs.report', 'cogs.ticket']

for extension in cog_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print(f"Failed to load extension {extension}: {e}")
# Cog end

# Discord bot code end
bot.run(token)