import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext import commands
from nextcord.ui import Button, View


class Moderated(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message clear channel
    # Only Owner, admin and moderator can clear
    @slash_command(name='purge', description='Delete all messages in channel', guild_ids=[])  # Add actual guild IDs
    async def purge(self, ctx: Interaction, amount: int):
        # Check for manage_messages permission
        if not ctx.user.guild_permissions.manage_messages:
            await ctx.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Limit the amount to 100 messages
        if amount > 100:
            await ctx.response.send_message('Cannot delete more than 100 messages', ephemeral=True)
            return

        # Defer the response if the operation might take time
        await ctx.response.defer(ephemeral=True)

        # Define buttons for confirmation
        view = View()
        confirm_button = Button(label='Confirm', style=nextcord.ButtonStyle.green)
        cancel_button = Button(label='Cancel', style=nextcord.ButtonStyle.red)
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        # Send a confirmation message with buttons
        followup_message = await ctx.followup.send(
            f'Are you sure you want to delete {amount} messages?',
            view=view,
            ephemeral=True
        )

        async def confirm_callback(_):
            # Purge messages if confirmed
            await ctx.channel.purge(limit=amount + 1)  # Including the command message itself
            await followup_message.edit(content='Cleared Messages', view=None)

        async def cancel_callback(_):
            await followup_message.edit(content='Purge cancelled.', view=None)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback

        await view.wait()

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
