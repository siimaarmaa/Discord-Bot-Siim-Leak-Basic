import nextcord
from nextcord.ext import commands


class SupportTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Ticket Setup", default_member_permissions=8)
    @commands.has_permissions(manage_guild=True)
    async def create_ticket(self, ctx):
        # Verify that the user is in a supported category
        if ctx.channel.category != 'support-tickets':
            await ctx.send('You can only create tickets in the support-tickets category.')
            return

        # Create a new channel for the ticket
        embed = nextcord.Embed(title='New Support Ticket', description='Your ticket has been created.')
        channel = await ctx.guild.create_text_channel('ticket-{}'.format(ctx.author.id))
        await channel.send(embed=embed)

        # Add the user's role to the channel
        role = nextcord.utils.get(ctx.guild.roles, name='Support Agent')
        await channel.set_permissions(ctx.author, overwrite={role: nextcord.PermissionOverwrite(read_messages=True)})

        # Send an initial message to the channel
        await channel.send('Please describe your issue in detail.')


def setup(bot):
    bot.add_cog(SupportTicketCog(bot))
