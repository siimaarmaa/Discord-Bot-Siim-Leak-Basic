import discord
from discord.ext import commands


class ReactRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # React role itself - add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 1202605345915011122:  # react-role
            guild_id = payload.guild_id
            guild_react_add = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            role = discord.utils.get(guild_react_add.roles, name=payload.emoji.name)

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild_react_add.members)
                if member is not None:
                    await member.add_roles(role)

    # React role itself - remove
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == 1202605345915011122:  # react-role
            guild_id = payload.guild_id
            guild_react_rem = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            role = discord.utils.get(guild_react_rem.roles, name=payload.emoji.name)

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild_react_rem.members)
                if member is not None:
                    await member.remove_roles(role)


def setup(bot: commands.Bot):
    bot.add_cog(ReactRole(bot))
