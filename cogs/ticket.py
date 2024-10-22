import discord
from discord.ext import commands
from discord.ui import View

class CloseButton(discord.ui.Button):
    def __init__(self, user_id, bot):
        super().__init__(style=discord.ButtonStyle.red, label="Close Ticket")
        self.user_id = user_id
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # Acknowledge the interaction
        await interaction.response.defer()
        # Check if the user who clicked is the ticket owner or has admin permissions
        if interaction.user.id == self.user_id or interaction.user.guild_permissions.administrator:
            await interaction.channel.delete()
            user = await self.bot.fetch_user(self.user_id)
            if user:
                await user.send("Your support ticket has been closed. If you have further questions, "
                                "feel free to open a new ticket.")
        else:
            await interaction.response.send_message("You don't have permission to close this ticket.", ephemeral=True)


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def create_ticket_channel(guild, user):
        category_name = "Support Tickets"
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel = await category.create_text_channel(f"ticket-{user.id}", overwrites=overwrites)
        return channel

    @discord.slash_command(name="openticket", description="Open a support ticket.")
    async def open_ticket(self, interaction: discord.Interaction):
        channel = await Ticket.create_ticket_channel(interaction.guild, interaction.user)
        embed = discord.Embed(
            title="Support Ticket",
            description=f"Hello {interaction.user.mention}, please describe your issue.",
            color=discord.Color.blue(),
        )

        # Create the view with the CloseButton
        view = View()
        view.add_item(CloseButton(interaction.user.id, self.bot))

        # Send the initial message with the CloseButton in this view
        await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.TextChannel):
            if message.channel.name.startswith("ticket-"):
                view = View()
                view.add_item(CloseButton(message.author.id, self.bot))
                await message.reply(view=view)


def setup(bot):
    bot.add_cog(Ticket(bot))
