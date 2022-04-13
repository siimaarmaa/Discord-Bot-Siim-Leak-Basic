import nextcord
from nextcord.ext import commands


class ReactRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # React role itself - add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 879824245339856948:
            guild_id = payload.guild_id
            guild_react_add = nextcord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            role = nextcord.utils.get(guild_react_add.roles, name=payload.emoji.name)

            if role is not None:
                member = nextcord.utils.find(lambda m: m.id == payload.user_id, guild_react_add.members)
                if member is not None:
                    await member.add_roles(role)

    # React role itself - remove
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == 879824245339856948:
            guild_id = payload.guild_id
            guild_react_rem = nextcord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            role = nextcord.utils.get(guild_react_rem.roles, name=payload.emoji.name)

            if role is not None:
                member = nextcord.utils.find(lambda m: m.id == payload.user_id, guild_react_rem.members)
                if member is not None:
                    await member.remove_roles(role)


def setup(bot: commands.Bot):
    bot.add_cog(ReactRole(bot))
