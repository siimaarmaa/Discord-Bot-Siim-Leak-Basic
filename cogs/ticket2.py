import nextcord
from nextcord.ext import commands


class SupportTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def open_ticket(self, ctx, category):
        # Check if the category is valid
        if category not in valid_categories:
            await ctx.send(f"Invalid category: {category}")
            return

        # Create a new ticket and send it to the support channel
        ticket_id = generate_ticket_id()
        ticket_message = f"New support ticket opened: {ticket_id}"
        await support_channel.send(ticket_message)

    @nextcord.slash_command()
    async def close_ticket(self, ctx, ticket_id):
        # Check if the ticket exists
        if ticket_id not in active_tickets:
            await ctx.send(f"Ticket with ID {ticket_id} does not exist")
            return

        # Remove the ticket from the list of active tickets
        del active_tickets[ticket_id]

    @nextcord.slash_command()
    async def view_ticket(self, ctx, ticket_id):
        # Check if the ticket exists
        if ticket_id not in active_tickets:
            await ctx.send(f"Ticket with ID {ticket_id} does not exist")
            return

        # Retrieve the ticket information
        ticket = active_tickets[ticket_id]

        # Format the ticket information into a message
        ticket_message = f"Ticket ID: {ticket_id}\n\nCategory: {ticket.category}\n\nMessage: {ticket.message}"

        # Send the ticket message to the user
        await ctx.send(ticket_message)


def setup(bot):
    bot.add_cog(SupportTicketCog(bot))
