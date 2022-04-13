import nextcord
from nextcord.ext import commands


class Moderated(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Message clear channel
    # Only Owner, admin and moderator can clear
    @commands.command(name='clear')
    @commands.has_any_role(896109567384113182, 905913356827918406, 905914143226351646)
    async def clear(self, ctx: commands.Context, amount=5):
        await ctx.channel.purge(limit=amount + 1)

    @clear.error
    async def clear_error(self, ctx: commands.Context, clear_error):
        if isinstance(clear_error, commands.CommandError):
            await ctx.send('You do not have permission to delete messages!')
        print(clear_error)

    # User Kick command
    # Only Owner and Admin
    @commands.command(name='kick')
    @commands.has_any_role(896109567384113182, 905913356827918406, 905914143226351646)
    async def kick(self, ctx: commands.Context, member: nextcord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}')

    @kick.error
    async def kick_error(self, ctx: commands.Context, kick_error):
        if isinstance(kick_error, commands.CommandError):
            await ctx.send('You do not have permission to kick member!')
        print(kick_error)

    # User Ban command
    # Only Owner and Admin
    @commands.command(name='ban')
    @commands.has_any_role(896109567384113182, 905913356827918406, 905914143226351646)
    async def ban(self, ctx: commands.Context, member: nextcord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @ban.error
    async def ban_error(self, ctx: commands.Context, ban_error):
        if isinstance(ban_error, commands.CommandError):
            await ctx.send('You do not have permission to ban member!')
        print(ban_error)

    # User Unban command
    # Only Owner and Admin can unban
    @commands.command(name='unban')
    @commands.has_any_role(896109567384113182, 905913356827918406, 905914143226351646)
    async def unban(self, ctx: commands.Context, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @unban.error
    async def unban_error(self, ctx: commands.Context, unban_error):
        if isinstance(unban_error, commands.CommandError):
            await ctx.send('You do not have permission to unban member')
        print(unban_error)


def setup(bot: commands.Bot):
    bot.add_cog(Moderated(bot))
