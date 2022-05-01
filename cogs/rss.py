import asyncio
import datetime
import json
from functools import partial, wraps
from io import BytesIO

import bs4
import discord
import feedparser
from discord.ext import commands
from PIL import Image

anilist_query = """query ($page: Int = 1, $id: Int, $type: MediaType, $isAdult: Boolean = false, $search: String, 
$format: [MediaFormat], $status: MediaStatus, $countryOfOrigin: CountryCode, $source: MediaSource, 
$season: MediaSeason, $seasonYear: Int, $year: String, $onList: Boolean, $yearLesser: FuzzyDateInt, $yearGreater: 
FuzzyDateInt, $episodeLesser: Int, $episodeGreater: Int, $durationLesser: Int, $durationGreater: Int, $chapterLesser: 
Int, $chapterGreater: Int, $volumeLesser: Int, $volumeGreater: Int, $licensedBy: [String], $isLicensed: Boolean, 
$genres: [String], $excludedGenres: [String], $tags: [String], $excludedTags: [String], $minimumTagRank: Int, 
$sort: [MediaSort] = [POPULARITY_DESC, SCORE_DESC]) { Page(page: $page, perPage: 20) { pageInfo { total perPage 
currentPage lastPage hasNextPage } media(id: $id, type: $type, season: $season, format_in: $format, status: $status, 
countryOfOrigin: $countryOfOrigin, source: $source, search: $search, onList: $onList, seasonYear: $seasonYear, 
startDate_like: $year, startDate_lesser: $yearLesser, startDate_greater: $yearGreater, episodes_lesser: 
$episodeLesser, episodes_greater: $episodeGreater, duration_lesser: $durationLesser, duration_greater: 
$durationGreater, chapters_lesser: $chapterLesser, chapters_greater: $chapterGreater, volumes_lesser: $volumeLesser, 
volumes_greater: $volumeGreater, licensedBy_in: $licensedBy, isLicensed: $isLicensed, genre_in: $genres, 
genre_not_in: $excludedGenres, tag_in: $tags, tag_not_in: $excludedTags, minimumTagRank: $minimumTagRank, 
sort: $sort, isAdult: $isAdult) { id title { userPreferred } coverImage { extraLarge large color } startDate { year 
month day } endDate { year month day } bannerImage season description type format status(version: 2) episodes 
duration chapters volumes genres isAdult averageScore popularity nextAiringEpisode { airingAt timeUntilAiring episode 
} mediaListEntry { id status } studios(isMain: true) { edges { isMain node { id name } } } } } } """


def sync_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


async_parse = sync_wrap(feedparser.parse)


class RSS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        return print(f"{self.__class__.__name__} cog has been loaded\n-----")

    async def get_color(self, url):
        print(url)
        async with self.bot.sesi.get(url) as respon:
            data = await respon.read()

        print(respon.status)
        img = Image.open(BytesIO(data))
        img2 = img.resize((1, 1))
        color = img2.getpixel((0, 0))
        final = '{:02x}{:02x}{:02x}'.format(*color)
        sixteen_integer_hex = int(final, 16)
        readable_hex = int(hex(sixteen_integer_hex), 0)

        return readable_hex

    @commands.command(name="nyaa")
    async def nyaa_rss_check(self):
        url = "https://feed.animetosho.org/rss2"

        async with self.bot.sesi.get(url) as respon:
            data = await respon.text()
            print(data)

        parse_data = await async_parse(data)

        print(json.dumps(parse_data, indent=4))

    @commands.command(name="rss")
    @commands.has_role(843730445002473492)
    async def rss(self, ctx, tag=None, index: int = 0, edit=False):
        if tag == "none":
            tag = None
        if edit == "true":
            edit = True

        await ctx.message.delete()

        url = "https://yurasu.com/feed/"

        async with self.bot.sesi.get(url) as respon:
            data = await respon.text()

        parse_data = await async_parse(data)
        parse_data = parse_data["entries"][index]
        sup = bs4.BeautifulSoup(parse_data["content"][0]["value"], "html.parser")
        image = sup.find_all("img")[-1]["src"].split("?")[0]
        image = f"https://yurasu.com" + image.split("f=auto")[1]

        url = "https://graphql.anilist.co"
        payload = {
            "query": anilist_query,
            "variables": {
                "page": 1,
                "type": "ANIME",
                "sort": "SEARCH_MATCH",
                "search": parse_data["tags"][0]["term"]
            }
        }

        async with self.bot.sesi.post(url, json=payload) as respon:
            data = await respon.json()

        data = data["data"]["Page"]["media"][0]
        user = discord.utils.get(ctx.guild.members, name=parse_data["author"])
        published_parsed = parse_data["published_parsed"]
        date = datetime.datetime(
            year=published_parsed[0],
            month=published_parsed[1],
            day=published_parsed[2],
            hour=published_parsed[3] + 7,
            minute=published_parsed[4],
            second=published_parsed[5],
            microsecond=published_parsed[6]
        )

        async with self.bot.sesi.get("https://yurasu.com/") as respon:
            mainsite_data = await respon.text()

        sup_mainsite = bs4.BeautifulSoup(mainsite_data, "html.parser")
        title = sup_mainsite.find("title").text
        icon_url = sup_mainsite.find("link", {"rel": "icon"})["href"].split("?")[0]

        embed = discord.Embed(
            title=parse_data["title"],
            url=parse_data["link"],
            color=await self.get_color(image)
        )

        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar,
            url=f"https://yurasu.com/author/{parse_data['author']}/"
        )
        embed.set_thumbnail(
            url=data["coverImage"]["extraLarge"]
        )
        embed.set_image(
            url=image
        )
        embed.set_footer(
            text=title,
            icon_url=icon_url
        )

        embed.timestamp = date

        if tag == "everyone":
            tag = "@everyone"

        if edit:
            embed_msg = await ctx.send(embed=embed)

            return await embed_msg.edit(content=tag, embed=embed)
        else:
            await ctx.send(content=tag, embed=embed)


def setup(bot):
    bot.add_cog(RSS(bot))
