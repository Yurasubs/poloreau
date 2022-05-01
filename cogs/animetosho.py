from datetime import datetime, timedelta

import aiohttp
import bs4
import discord
import pyperclip
from discord.ext import commands


class Animetosho(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    async def animetosho_frontend(self, ctx, final_dataset):
        teks = ""
        for i in final_dataset:
            teks += f"**{i}**\n"

            for i2 in final_dataset[i]:
                teks += ""

        embed = discord.Embed(
            title="Latest Release",
            description=teks,
            color=0x3a2600,
            url="https://animetosho.org/"
        )
        embed.set_author(
            name=ctx.author.display_name,
            url=ctx.message.jump_url,
            icon_url=ctx.author.display_avatar
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/896733176427319296/911921829998915604/animetosho.org__1_1.png"
        )
        embed.set_image(
            url="https://animetosho.org/inc/sideimg_214.jpg"
        )
        embed.set_footer(
            text="Anime Tosho | v1.0",
            icon_url="https://cdn.discordapp.com/attachments/896733176427319296/911920540757921862/favicon.png"
        )
        return await ctx.send(embed=embed)

    @commands.command(name="animetosho")
    async def animetosho(self, ctx):
        url = "https://animetosho.org/"

        async with aiohttp.ClientSession() as sesi:
            async with sesi.get(url) as respon:
                data = await respon.text()

        sup = bs4.BeautifulSoup(data, "html.parser")
        content = sup.select_one("#content > div:nth-child(4)")

        final_dataset = {}
        day_string = ""

        for i in content.children:
            if "home_list_datesep" in i["class"]:
                day_string = i.text
                final_dataset[day_string] = []
            else:
                title_url = i.select_one("div.link > a")
                _type = i.select_one("div.size_icon > span")

                if "icon_filesize" in _type["class"]:
                    _type = "file"
                else:
                    _type = "folder"

                size = i.select_one("div.size")["title"].split("Total file size: ")[1].split(" bytes")[0]
                size = size.replace(",", "")
                size = int(size)
                date = i.select_one("div.date").text.split(":")
                now = datetime.now()
                year = now.year
                month = now.month
                day = now.day
                if day_string == "Today":
                    _datetime = datetime(year, month, day)
                elif day_string == "Yesterday":
                    _datetime = datetime(year, month, day - 1)
                else:
                    _datetime = ""

                date = _datetime.replace(hour=int(date[0]), minute=int(date[1])) + timedelta(hours=7)
                links_i = i.select_one("div.links")
                a_links = links_i.find_all("a", recursive=False)
                links_dataset = [{"name": i2.text, "url": i2["href"]} for i2 in a_links]
                series_link = links_i.select_one("span.serieslink > a")
                if series_link:
                    series = {
                        "title": series_link.text,
                        "url": series_link["href"]
                    }
                else:
                    series = None
                misc_links = links_i.select_one("span.links_right > span > span > a")
                misc = {
                    "name": misc_links.text,
                    "url": misc_links["href"]
                }
                file_string = [
                    "file",
                    "files"
                ]
                file_count = links_i.select_one("em")

                if file_count:
                    file_count = file_count.text.split("(")[1]

                    for i2 in file_string:
                        file_count = file_count.replace(i2 + ")", "")

                    file_count = int(file_count)

                if series:
                    seed_leech = links_i.select_one(f"span:nth-child(5)")
                else:
                    seed_leech = links_i.select_one(f"span:nth-child(4)")

                seeders = None
                leechers = None
                if seed_leech:
                    seed_leech = seed_leech["title"]
                    seeders = int(seed_leech.split("Seeders: ")[1].split(" ")[0])
                    leechers = int(seed_leech.split("Leechers: ")[1])

                data = {
                    "title": title_url.text,
                    "url": title_url["href"],
                    "type": _type,
                    "size": size,
                    "date": date.isoformat(),
                    "links": links_dataset,
                    "series": series,
                    "misc": misc,
                    "file_count": file_count,
                    "seeders": seeders,
                    "leechers": leechers
                }

                final_dataset[day_string].append(data)

        print(final_dataset)
        pyperclip.copy(str(final_dataset))
        return await self.animetosho_frontend(ctx, final_dataset)


def setup(bot):
    bot.add_cog(Animetosho(bot))
