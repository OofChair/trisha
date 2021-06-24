import discord
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from discord.ext import commands, tasks
from typing import List


class ChatterBot(commands.Cog):
    """ChatterBot cog."""

    def __init__(self, bot):
        self.bot = bot
        self.chatterbot = ChatBot(
            self.bot.user.name,
            storage_adapter="chatterbot.storage.SQLStorageAdapter",
            database_uri="sqlite:///chatterbot.sqlite3",
            logic_adapters=[
                "chatterbot.logic.BestMatch",
                "chatterbot.logic.MathematicalEvaluation",
                "chatterbot.logic.TimeLogicAdapter",
            ],
        )
        self.messages = {}
        self.train.start()

    @tasks.loop(minutes=5)
    async def train(self):
        """
        This trains the ChatterBot on the cached messages
        """
        local_messages = self.messages.copy()
        self.messages.clear()
        for channel in local_messages:
            if len(local_messages[channel]) <= 5:
                continue
            print(
                f"Training on {len(local_messages[channel])} messages in channel with ID {channel}"
            )
            await self.train_chatbot(local_messages[channel])
        del local_messages

    async def get_response(self, text):
        """
        This gets a response for the given text
        It is currently blocking and something that needs to be worked on in the future
        """

        response = self.chatterbot.get_response(text)
        return str(response)

    async def train_chatbot(self, texts: list):
        """
        This trains the ChatterBot with the given list
        It is currently blocking and something that needs to be worked on in the future
        """
        trainer = ListTrainer(self.chatterbot)
        trainer.train(texts)

    @commands.command(aliases=["ai", "chat"])
    @commands.bot_has_permissions(send_messages=True)
    async def talk(self, ctx, *, text):
        """
        Talk to a custom AI robot!
        """
        await ctx.trigger_typing()
        response = await self.get_response(text)
        try:
            await ctx.send(response, reference=ctx.message)
        except discord.errors.HTTPException:
            await ctx.send(response)

    @commands.group()
    async def train(self, ctx):
        """
        Train the AI on previous messages.
        """
        pass

    @train.command()
    async def server(self, ctx):
        """
        Train the AI on messages from your entire server.
        """
        pass

    @train.command()
    async def channel(self, ctx, channels: List[discord.TextChannel]):
        """
        Train the AI on messages from specific channels.
        """
        pass

    @commands.group()
    async def optout(self, ctx):
        """
        Opt out you or your entire server's message
        """
        pass

    @optout.command()
    async def me(self, ctx):
        """
        Opt out yourself from being used to train the AI.
        """
        pass

    @optout.command()
    async def server(self, ctx):
        """
        Opt out your server from being used to train the AI.

        Using the train command will bypass this.
        """
        pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This will respond to users when they ping the bot.
        """
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        normal = f"<@{message.guild.me.id}>"
        nickname = f"<@!{message.guild.me.id}>"
        if message.content.startswith(normal):
            text = message.content.replace(normal, "", 1).strip()
        elif message.content.startswith(nickname):
            text = message.content.replace(nickname, "", 1).strip()
        else:
            return
        if text == "":
            return
        await message.channel.trigger_typing()
        response = await self.get_response(text)
        if len(response) > 1500:
            return
        await message.channel.send(response, reference=message)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This will respond to users when they DM the bot.
        """
        if message.author.bot:
            return
        if message.guild:
            return
        await message.channel.trigger_typing()
        response = await self.get_response(message, message.clean_content)
        try:
            await message.channel.send(response, reference=message)
        except discord.errors.HTTPException:
            await message.channel.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This will respond to users when they respond to the bot.
        It will not work in DMs, as the other listener handles that
        """
        if message.author.bot:
            return
        if message.reference is None:
            return
        if message.guild.me is None:
            return
        if message.reference.resolved.author.id != message.guild.me.id:
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        await message.channel.trigger_typing()
        response = await self.get_response(message, message.clean_content)
        if len(response) > 1500:
            return
        try:
            await message.channel.send(response, reference=message)
        except discord.errors.HTTPException:
            await message.channel.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This collects messages to train on.
        It will ignore DM messages
        """
        if message.guild is None:
            return
        if message.content is None:
            return
        if len(message.content) > 500:
            return
        if message.channel.id in self.messages:
            self.messages[message.channel.id].append(message.clean_content)
        else:
            self.messages[message.channel.id] = [message.clean_content]


def setup(bot):
    bot.add_cog(ChatterBot(bot))
