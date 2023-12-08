import nextcord
from nextcord.ext import commands, tasks


class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=5)  # Adjust the interval as needed
    async def update_stats(self):
        for guild in self.bot.guilds:
            channel_id = 1182060683014189116  # Replace with your channel ID
            channel = guild.get_channel(channel_id)

            if channel:
                total_members = len(guild.members)
                online_members = sum(member.status == nextcord.Status.online for member in guild.members)

                await channel.edit(name=f"Server Stats: {online_members}/{total_members} online")


def setup(bot):
    bot.add_cog(ServerStats(bot))
