import nextcord
from nextcord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv


# Secrets set up
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="ChatGPT")
    async def chatgpt(self, ctx: nextcord.Interaction, *, prompt: str):
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "text-davinci-003",
                "prompt": prompt,
                "max_tokens": 7,
                "temperature": 0
            }
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Accept': 'application/json'
                }
            async with session.post('https://api.openai.com/v1/completions', json=payload, headers=headers) as resp:
                response = await resp.json()
                print(response)  # Print the response for debugging
                completion = response["choices"][0]["text"]
                embed = nextcord.Embed(title="ChatGPT's Response:", description=completion)
                await ctx.response.send_message(embed=embed)


#    @nextcord.slash_command(description="Rolls a number between 1 and 6.")
#    async def dice(self, ctx: nextcord.Interaction):
#        dice = random.randint(1, 6)
#        await ctx.response.send_message(f"You rolled a {dice}!", ephemeral=True)

#    @nextcord.slash_command(description="Have the bot toss a coin.")
 #   async def coin(self, ctx: nextcord.Interaction, pick: str = SlashOption(description="Choose heads or tails",
  #                                                                          required=True, choices=["Head", "Tails"])):
   #     coin = random.choice(["Head", "Tails"])
    #    if pick.lower() == coin.lower():
     #       await ctx.response.send_message(f"You chose {pick} and {coin} was flipped! 🤔", ephemeral=True)
      #  else:
       #     await ctx.response.send_message(f"You chose {pick} and {coin} was flipped! 🤔", ephemeral=True)


def setup(bot):
    bot.add_cog(AI(bot))
