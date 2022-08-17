import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext import commands


class Moderated(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message clear channel
    # Only Owner, admin and moderator can clear
    @slash_command(name='purge', description='Delete all messages in channel', guild_ids=[])
    async def purge(self, ctx, amount: int):
        amount = amount+1
        if amount > 101:
            await ctx.send('Can not delete more than 100 messages')
        else:
            await ctx.channel.purge(limit=amount)
            await ctx.send('Cleared Messages')

    # User Unban command
    # Only Owner and Admin can unban
    @slash_command(name='unban', description='Unbans a member', guild_ids=[])
    async def unban(
            self,
            ctx: Interaction,
            member: nextcord.User = nextcord.SlashOption(
                name='member',
                description='The User ID of the person you want to unban.')
    ):
        await ctx.guild.unban(user=member)
        await ctx.response.send_message(f'I have unbanned {member}.')


def setup(bot):
    bot.add_cog(Moderated(bot))
