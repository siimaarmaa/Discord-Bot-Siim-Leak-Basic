import nextcord
from nextcord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup

class Epicgamesfree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_free_games.start()  # Start the task when the cog is loaded

    def cog_unload(self):
        self.daily_free_games.cancel()  # Cancel task when the cog is unloaded

    @staticmethod
    def scrape_epic_games():
        url = "https://www.epicgames.com/store/en-US/free-games"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Example of parsing the HTML:
        games_list = soup.find_all("div", class_="game-element-class")  # Replace with actual class name
        free_games = []
        for game in games_list:
            title = game.find("h3", class_="title-class").text  # Replace with actual class name
            game_url = game.find("a", class_="link-class")['href']  # Replace with actual class name
            free_games.append(f"{title}: {game_url}")

        return "\n".join(free_games)

    @tasks.loop(hours=24)
    async def daily_free_games(self):
        channel_id = 1202604833442373743
        channel = self.bot.get_channel(channel_id)
        games = FreeGames.scrape_epic_games()
        await channel.send(games)

def setup(bot):
    bot.add_cog(Epicgamesfree(bot))
