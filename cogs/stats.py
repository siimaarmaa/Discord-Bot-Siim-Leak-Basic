import nextcord
from nextcord.ext import commands
from nextcord.ext.tasks import loop
from nextcord.utils import get
from typing import List
import datetime
import time


class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Define the channels where the stats will be displayed
        self.channels = [1182060683014189116]

        # Create a task that will run every 60 seconds (1 minute)
        self.update_stats_task = self.bot.loop.create_task(self.update_stats())

    @commands.Cog.listener()
    async def on_ready(self):
        print('Server Stats cog is ready')

    async def update_stats(self):
        # Get the current server stats
        stats = await self.bot.fetch_server_stats()

        # Format the stats into a string
        formatted_stats = f'''
            **Server Stats**

            **Total Members:** {stats.member_count}
            **Online Members:** {stats.online_member_count}
            **Server Created:** {datetime.datetime.fromtimestamp(stats.created_at).strftime('%Y-%m-%d %H:%M:%S')}
            **Server Activity:** {stats.activity_count}
        '''

        # Send the formatted stats to all the channels
        for channel in self.channels:
            await self.bot.get_channel(channel).send(formatted_stats)

        # Delay the task by 60 seconds (1 minute)
        await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(ServerStats(bot))
