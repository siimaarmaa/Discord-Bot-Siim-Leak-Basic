from nextcord.ext import commands
import nextcord


class CreateTicket(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label='Create ticket', style=nextcord.ButtonStyle.blurple, custom_id='create_ticket:blurple'
    )
    async def create_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        msg = await interaction.response.send_message('A ticket is being created . . .', ephemeral=True)

        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(1069731597861003276): nextcord.PermissionOverwrite(read_messages=True),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)
        }

        category = interaction.guild.get_channel(1182054708999889056)

        channel = await interaction.guild.create_text_channel(f'{interaction.user.name}-ticket', category=category,
                                                              overwrites=overwrites)
        await msg.edit(f'Channel created successfully! {channel.mention}')
        embed = nextcord.Embed(title=f'Ticket created', description=f'{interaction.user.mention} '
                                                                    f'created a ticket! Click one of the buttons below '
                                                                    f'to alter the settings')
        await channel.send(embed=embed, view=TicketSettings())


class TicketSettings(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label='Close ticket', style=nextcord.ButtonStyle.red, custom_id='ticket_settings:red'
    )
    async def close_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message('Ticket is being closed.', ephemeral=True)
        await interaction.channel.delete()
        await interaction.user.send(f'Ticket **{interaction.channel.name}** successfully closed!')


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(CreateTicket())
            self.add_view(TicketSettings())
            self.persistent_views_added = True
            print('Persistent views added')

    @nextcord.slash_command(description="Ticket Setup", default_member_permissions=8)
    @commands.has_permissions(manage_guild=True)
    async def setup_ticket(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title='Create Ticket', description="'Click the 'Create Ticket' button below to create "
                                                                  "a ticket. The server's staff will be noticed and "
                                                                  "shortly aid you with your problem.")
        await interaction.send(embed=embed, view=CreateTicket())


def setup(bot):
    bot.add_cog(Bot(bot))
