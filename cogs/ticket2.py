import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Select
from nextcord import slash_command, ButtonStyle


# Define a cog to handle support tickets
class SupportTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a slash command for creating a support ticket
    @slash_command(description="Create a new support ticket")
    async def create_ticket(self, ctx, category: str):
        # Check if the user has the required permissions
        if not ctx.author.permissions_in(ctx.channel).administrator:
            await ctx.respond(
                embed=nextcord.Embed(
                    title="Insufficient Permissions",
                    description="Only administrators can create support tickets.",
                    color=nextcord.Color.red
                )
            )
            return

        # Create a new support ticket message
        ticket_message = await ctx.send(f"Creating support ticket for category: {category}")

        # Create a form to gather additional details from the user
        select = Select(
            placeholder="Please select your issue type:",
            choices=[
                ("Bug Report", "bug_report"),
                ("Feature Request", "feature_request"),
                ("Other", "other")
            ]
        )
        # Create a cancel button
        cancel_button = Button(
            label="Cancel",
            style=ButtonStyle.danger,
            emoji="❌"
        )

        # Create a view to embed the form and buttons
        view = View(select, cancel_button)
        await ticket_message.edit(embed=nextcord.Embed(
            title="Support Ticket Form",
            color=nextcord.Color.yellow
        ), view=view)

        # Listen for button clicks
        def check_button(interaction):
            return interaction.message.id == ticket_message.id and interaction.view == view

        # Handle form submission
        try:
            interaction = await self.bot.wait_for('button_click', check=check_button)

            chosen_issue_type = interaction.values['select']
            if chosen_issue_type == "bug_report":
                issue_type = "Bug Report"
            elif chosen_issue_type == "feature_request":
                issue_type = "Feature Request"
            else:
                issue_type = "Other"

            # Gather additional details from the user
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Provide additional details for your support ticket:",
                    description="Please provide a brief description of your issue or request.",
                    color=nextcord.Color.magenta
                )
            )
            additional_details = await interaction.response.fetch_message()

            # Check for the existence of the 'author' attribute
            try:
                interaction_author = interaction.author
            except AttributeError:
                interaction_author = None

            # Add the ticket information to a database or store it elsewhere
            if interaction_author is not None:
                print(f"Ticket created: {issue_type} - {additional_details.content}")
                await interaction_author.send(
                    embed=nextcord.Embed(
                        title="Support Ticket Submitted",
                        description=f"Your support ticket has been submitted for category '{category}'. We will review it and get back to you shortly.",
                        color=nextcord.Color.green
                    )
                )
                await ticket_message.delete()
            else:
                print(f"Ticket created: {issue_type} - {additional_details.content}")
                await ticket_message.delete()
        except Exception as e:
            print(f"Error handling support ticket form: {e}")

            # Delete the support ticket message
            await ticket_message.delete()


def setup(bot):
    bot.add_cog(SupportTicketCog(bot))
