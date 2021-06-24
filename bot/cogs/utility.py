import discord
from discord.ext import commands


class Utility(commands.Cog):
    """Utilities Cog"""

    def __init__(self, bot):
        self.bot = bot

    async def get_avatar(self, link):
        try:
            async with self.session.get(link) as file:
                return await file.read()
        except Exception:
            return

    async def change_avatar(self, ctx, avatar):
        try:
            await self.bot.user.edit(avatar=avatar)
        except discord.HTTPException:
            await ctx.send("Something went wrong, possibly a ratelimit.")
            return
        except discord.InvalidArgument:
            await ctx.send("The image you provided was in a format not supported.")
            return
        await ctx.send("Done.")

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def setavatar(self, ctx, link: str = None):
        """
        Change my avatar.
        """
        attachments = ctx.message.attachments
        if attachments:
            avatar = await attachments[0].read()
        else:
            if link is None:
                await ctx.send("You need to provide a photo or attach a link.")
                return
            avatar = await self.get_avatar(link)
            if avatar is None:
                await ctx.send(
                    "Something went wrong. It's likely the image you provided isn't in a supported format."
                )
                return
        await self.change_avatar(ctx, avatar)

    @commands.command(name="invite")
    async def invite(self, ctx):
        """
        Invite me!
        """
        channel_perms = ctx.channel.permissions_for(ctx.guild.me)
        embed = discord.Embed(
            title="Click here to invite me!",
            url=self.bot.invite,
            color=ctx.author.color,
        )
        if channel_perms.send_messages and channel_perms.embed_links:
            await ctx.send(embed=embed)
            return
        if channel_perms.send_messages:
            await ctx.send(self.bot.invite)
            return
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            pass

def setup(bot):
    bot.add_cog(Utility(bot))
