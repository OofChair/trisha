import aiohttp
import discord
import yaml
from discord.ext import commands


class Bot(commands.AutoShardedBot):
    def __init__(self):
        with open("config.yaml") as file:
            self.config = yaml.load(file)
        intents = discord.Intents.none()
        intents.messages = True
        intents.guilds = True
        super().__init__(
            allowed_mentions=discord.AllowedMentions(
            roles=False, everyone=False, users=True
            ) ,
            intents=intents,
            command_prefix=["!"],
            activity=discord.Activity(
                name=self.config["status"], type=discord.ActivityType.watching
            ),
        )
        self.loop.create_task(self.load_all_cogs())
        self.session = aiohttp.ClientSession()

    def run(self):
        super().run(self.config["token"], reconnect=True)

    async def load_all_cogs(self):
        await self.wait_until_ready()
        cogs = self.config["cogs"]
        for cog in cogs:
            try:
                self.load_extension("cogs." + cog)
            except Exception as error:
                print(f"Failed to load cog: {cog}\n{error}")
                continue
            print(f"Loaded cog: {cog}")

    async def on_ready(self):
        print(f"Connected to Discord as {self.user} ({self.user.id})")

DiscordBot = Bot()
DiscordBot.run()
