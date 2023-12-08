import nextcord
from nextcord.ext import commands


class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore messages from bots

        if "show stats" in message.content.lower():
            await self.send_server_stats(message.channel)

    async def send_server_stats(self, channel):
        guild = channel.guild

        # Get general server statistics
        total_members = guild.member_count
        online_members = sum(member.status != nextcord.Status.offline for member in guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        bot_members = sum(member.bot for member in guild.members)

        # Get voice chat information
        voice_channels_info = {}

        for voice_channel in guild.voice_channels:
            category_name = voice_channel.category.name if voice_channel.category else "Uncategorized"

            if category_name not in voice_channels_info:
                voice_channels_info[category_name] = []

            members_in_channel = len(voice_channel.members)
            bots_in_channel = sum(member.bot for member in voice_channel.members)
            voice_channels_info[category_name].append(
                f"{voice_channel.name}: {members_in_channel} members ({bots_in_channel} bots)"
            )

        # Send the information to the channel
        info_message = f"Server Statistics for {guild.name} (All-time):\n" \
                       f"Total Members: {total_members}\n" \
                       f"Online Members: {online_members}\n" \
                       f"Total Bots: {bot_members}\n" \
                       f"Text Channels: {text_channels}\n" \
                       f"Voice Channels: {voice_channels}\n\n" \
                       "Voice Channel Information:\n"

        for category_name, channels_info in voice_channels_info.items():
            info_message += f"\nCategory: {category_name}\n"
            info_message += "\n".join(channels_info)
            info_message += "\n"

        await channel.send(info_message)


def setup(bot):
    bot.add_cog(ServerStats(bot))
