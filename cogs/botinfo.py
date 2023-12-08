import nextcord
from nextcord.ext import commands
from nextcord import slash_command
import platform


class Info(commands.Cog):
  def __init__(self, client):
    self.client = client

  @slash_command()
  async def info(self, ctx):
    pythonVersion = platform.python_version()
    nextcordVersion = nextcord.__version__
    serverCount = len(self.client.guilds)
    memberCount = len(set(self.client.get_all_members()))

    embed = nextcord.Embed(
      title=f"{self.client.user.name} Stats",
      description="\uFEFF",
      colour=ctx.author.colour,
      timestamp=ctx.message.created_at,
    )

    embed.add_field(name="Bot Version:", value="0.2.40")
    embed.add_field(name="Python Version:", value=pythonVersion)
    embed.add_field(name="Nextcord Version", value=nextcordVersion)
    embed.add_field(name="Total Guilds:", value=serverCount)
    embed.add_field(name="Total Users:", value=memberCount)
    embed.add_field(name="Bot Developers:", value="<@185089253611536384>")
    embed.set_footer(text = f"[Support Server](https://nextcord.gg/ZsZQ4SHsqs)")

    embed.set_footer(text=f"Siim Leaks Basic | {self.client.user.name}")

    await ctx.send(embed=embed)

def setup(client):
  client.add_cog(Info(client))