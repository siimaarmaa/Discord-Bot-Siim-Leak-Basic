import nextcord
from nextcord.ext import commands
from nextcord import slash_command


class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='serverstats', description='ServerStats', guild_ids=[])
    async def server_stats(self, ctx):
        guild = ctx.guild

        # Get general server statistics
        total_members = guild.member_count
        online_members = sum(member.status != nextcord.Status.offline for member in guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)

        # Get voice chat information
        voice_channels_info = []
        for voice_channel in guild.voice_channels:
            members_in_channel = len(voice_channel.members)
            voice_channels_info.append(f"{voice_channel.name}: {members_in_channel} members")

        # Send the information to the channel
        await ctx.send(f"Server Statistics for {guild.name}:\n"
                       f"Total Members: {total_members}\n"
                       f"Online Members: {online_members}\n"
                       f"Text Channels: {text_channels}\n"
                       f"Voice Channels: {voice_channels}\n\n"
                       f"Voice Channel Information:\n" + "\n".join(voice_channels_info))


def setup(bot):
    bot.add_cog(ServerStats(bot))
