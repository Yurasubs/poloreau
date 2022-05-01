import asyncio
import functools
from io import BytesIO

import aiohttp
import discord
from PIL import Image


async def get_color(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as sesi:
        async with sesi.get(url) as respon:
            data = await respon.read()

    img = Image.open(BytesIO(data))
    img2 = img.resize((1, 1))
    color = img2.getpixel((0, 0))
    final = '{:02x}{:02x}{:02x}'.format(*color)
    sixteenIntegerHex = int(final, 16)
    readableHex = int(hex(sixteenIntegerHex), 0)

    return readableHex


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


def sync_wrap(func):
    @asyncio.coroutine
    @functools.wraps(func)
    def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return loop.run_in_executor(executor, pfunc)

    return run

class Pagination:
    def __init__(self, bot, final_dataset=None, custom_embed=None, timeout=20, title=discord.embeds.EmptyEmbed, footer=discord.embeds.EmptyEmbed):
        self.bot = bot
        self.title = title
        self.footer = footer
        self.timeout = timeout
        self.custom_embed = custom_embed
        self.final_dataset = final_dataset

    async def start(self, ctx):
        async def _embed(_entry):
            embed_class = discord.Embed(title=self.title, description=_entry, color=self.bot.default_color)
            embed_class.set_footer(text=self.footer)
            return embed_class

        pos = 1
        first_run = True
        dataset_total = len(self.final_dataset)
        embed_msg = None

        while True:
            if first_run:
                entry = self.final_dataset[pos - 1]
                embed = await _embed(entry)
                embed_msg = await ctx.send(embed=embed)
                first_run = False
            if dataset_total == 1:
                break

            if pos == 1:
                to_react = ["▶️", "☑️"]
            elif dataset_total == pos:
                to_react = ["◀️", "☑️"]
            elif 1 < pos < dataset_total:
                to_react = ["◀️", "▶️", "☑️"]
            else:
                to_react = None

            for react in to_react:
                await embed_msg.add_reaction(react)

            def check_react(reaction, _user):
                if reaction.message.id != embed_msg.id:
                    return False
                if _user != ctx.message.author:
                    return False
                if str(reaction.emoji) not in to_react:
                    return False
                return True

            try:
                res, user = await self.bot.wait_for("reaction_add", timeout=self.timeout, check=check_react)
            except asyncio.TimeoutError:
                return await embed_msg.clear_reactions()
            if user != ctx.message.author:
                pass
            elif "☑️" in str(res.emoji):
                return await embed_msg.clear_reactions()
            elif "◀️" in str(res.emoji):
                await embed_msg.clear_reactions()
                pos -= 1
                entry = self.final_dataset[pos - 1]
                embed = await _embed(entry)
                await embed_msg.edit(embed=embed)
            elif "▶️" in str(res.emoji):
                await embed_msg.clear_reactions()
                pos += 1
                entry = self.final_dataset[pos - 1]
                embed = await _embed(entry)
                await embed_msg.edit(embed=embed)
