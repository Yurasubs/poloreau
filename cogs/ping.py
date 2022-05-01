from datetime import datetime

import aiohttp
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.test = "A"
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command()
    async def test(self, ctx):
        return await ctx.send(self.test)

    @commands.command(name="ping")
    async def ping(self, ctx):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        }
        async with aiohttp.ClientSession(headers=headers) as sesi:

            start = datetime.now()
            async with sesi.get("https://www.google.com/") as respon:
                end = datetime.now()
                result = end - start
                google = int(result.total_seconds() * 1000)

            start = datetime.now()
            async with sesi.get("https://brainly.co.id/") as respon:
                end = datetime.now()
                result = end - start
                brainly = int(result.total_seconds() * 1000)

            start = datetime.now()
            async with sesi.get("https://yurasu.com/") as respon:
                end = datetime.now()
                result = end - start
                yurasubs = int(result.total_seconds() * 1000)
            start = datetime.now()
            async with sesi.get("https://web.whatsapp.com/") as respon:
                end = datetime.now()
                result = end - start
                whatsapp = int(result.total_seconds() * 1000)
            start = datetime.now()
            async with sesi.get("https://facebook.com/") as respon:
                end = datetime.now()
                result = end - start
                facebook = int(result.total_seconds() * 1000)
            start = datetime.now()
            async with sesi.get("https://1.1.1.1/") as respon:
                end = datetime.now()
                result = end - start
                cloudflare = int(result.total_seconds() * 1000)

        teks = f"<:lcNyanPasu:831944812592103475> Hasil Ping <:lcNyanPasu:831944812592103475>\nGoogle `{google}ms`\nBrainly `{brainly}ms`\nYurasubs `{yurasubs}ms`\nWhatsApp `{whatsapp}`ms\n1.1.1.1 `{cloudflare}`ms\nFacebook `{facebook}`ms"
        return await ctx.send(teks)


def setup(bot):
    bot.add_cog(Ping(bot))
