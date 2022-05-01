import discord
from discord.ext import commands


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        return print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command()
    @commands.is_owner()
    async def clean(self, ctx, limit: int, mode, user: discord.Member):
        if mode == "user":
            def check(message):
                return message.author.id == user.id

            try:
                await ctx.channel.purge(limit=limit, check=check)
            except discord.errors.DiscordServerError:
                pass


def setup(bot):
    return bot.add_cog(Purge(bot))
