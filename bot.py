import contextlib
import datetime
import io
import json
import logging
import os
import textwrap
import urllib.parse
from http import client
from pathlib import Path
from traceback import format_exception
from urllib import parse

import aiohttp
import bs4
import discord
import pyperclip
from discord.ext import commands

from utils import json_loader
from utils.png2ass import png_to_ass
from utils.util import Pagination, clean_code

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).parents[0]
cwd = str(cwd)
intents = discord.Intents.all()
bot = commands.Bot(
    case_insensitive=True,
    command_prefix="//",
    help_command=None,
    intents=intents,
    owner_id=0
)
secret_file = json_loader.read_json("secrets")
bot.config_token = secret_file["token"]
bot.default_color = 0xbe8385

bot.number = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]


@bot.event
async def on_ready():
    bot.sesi = aiohttp.ClientSession()
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name="vapoursynth"))
    print("poloreau loaded")

@bot.command(name="at")
async def te(ctx):
    async with aiohttp.ClientSession() as sesi:
        url = "https://animetosho.org/"

        async with sesi.get(url) as respon:
            data = await respon.text()

    sup = bs4.BeautifulSoup(data, "html.parser")
    content = sup.select_one("#content > div:nth-child(4)")
    final_dataset = {}

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

            size = int(i.select_one("div.size")["title"].split("Total file size: ")[1].split(" bytes")[0].replace(",", ""))
            date = i.select_one("div.date").text.split(":")
            if day_string == "Today":
                day = datetime.datetime.utcnow()
            elif day_string == "Yesterday":
                day = datetime.datetime.utcnow()
            print(date)
            day.replace(hour=int(date[0]) + 7, minute=int(date[1]))
            links_i = i.select_one("div.links")
            a_links = links_i.find_all("a", recursive=False)
            links_dataset = [{"name": i2.text, "url": i2["href"]} for i2 in a_links]
            series_link = links_i.select_one("span.serieslink > a")
            series = {
                "title": series_link.text,
                "url": series_link["href"]
            }
            misc_links = links_i.select_one("span.links_right > span > span > a")
            misc = {
                "name": misc_links.text,
                "url": misc_links["href"]
            }

            data = {
                "title": title_url.text,
                "url": title_url["href"],
                "type": _type,
                "size": size,
                "date": day.isoformat(),
                "links": links_dataset,
                "series": series,
                "misc": misc
            }

            final_dataset[day_string].append(data)

    print(final_dataset)
    pyperclip.copy(str(final_dataset))


@bot.command(name="pt")
async def powerthesaurus(ctx, *, query):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.55 Safari/537.36 "
    }
    url = "https://api.powerthesaurus.org/"
    payload = {
        "operationName": "SEARCH_QUERY",
        "query": "query SEARCH_QUERY($query: String!) {\n  search(query: $query) {\n    terms {\n      id\n      "
                 "name\n      slug\n      counters\n      __typename\n    }\n    list\n    correctedFrom\n    "
                 "__typename\n  }\n}\n",
        "variables": {
            "query": query
        }
    }
    async with aiohttp.ClientSession(headers=headers) as sesi:
        async with sesi.post(url, json=payload) as respon:
            data = await respon.text()

        data = json.loads(data)
        _id = data["data"]["search"]["terms"][0]["id"]

        payload = {
            "operationName": "THESAURUS_LIST_QUERY",
            "query": "query THESAURUS_LIST_QUERY($termID: ID!, $list1: List!, $list2: List!, $list3: List!, "
                     "$posID: Int, $posID2: ID, $sort: ThesaurusSorting!, $first: Int, $first2: Int) {\n  synonyms: "
                     "thesauruses(\n    termId: $termID\n    sort: $sort\n    list: $list1\n    first: $first\n    "
                     "partOfSpeechId: $posID\n  ) {\n    totalCount\n    edges {\n      node {\n        _type\n       "
                     " id\n        isPinned\n        targetTerm {\n          id\n          name\n          slug\n     "
                     "     __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    "
                     "__typename\n  }\n  antonyms: thesauruses(\n    termId: $termID\n    sort: $sort\n    list: "
                     "$list2\n    first: $first\n    partOfSpeechId: $posID\n  ) {\n    totalCount\n    edges {\n     "
                     " node {\n        _type\n        id\n        isPinned\n        targetTerm {\n          id\n      "
                     "    name\n          slug\n          __typename\n        }\n        __typename\n      }\n      "
                     "__typename\n    }\n    __typename\n  }\n  related: thesauruses(\n    termId: $termID\n    sort: "
                     "$sort\n    list: $list3\n    first: $first\n    partOfSpeechId: $posID\n  ) {\n    totalCount\n "
                     "   edges {\n      node {\n        _type\n        id\n        isPinned\n        targetTerm {\n   "
                     "       id\n          name\n          slug\n          __typename\n        }\n        "
                     "__typename\n      }\n      __typename\n    }\n    __typename\n  }\n  sentences(termId: $termID, "
                     "partOfSpeechId: $posID2, first: $first2) {\n    totalCount\n    edges {\n      node {\n        "
                     "_type\n        id\n        sentence\n        author {\n          id\n          link\n          "
                     "title\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n  "
                     "  __typename\n  }\n}\n",
            "variables": {
                "first": 25,
                "first2": 5,
                "list1": "SYNONYM",
                "list2": "ANTONYM",
                "list3": "RELATED",
                "sort": {
                    "direction": "DESC",
                    "field": "RATING"
                },
                "termID": _id
            }
        }

        async with sesi.post(url, json=payload) as respon:
            data = await respon.text()

        data = json.loads(data)
        sinonim = [i["node"]["targetTerm"]["name"] for i in data["data"]["synonyms"]["edges"]]
        sinonim = " ".join([f"`{i}`" for i in sinonim])
        antonim = [i["node"]["targetTerm"]["name"] for i in data["data"]["antonyms"]["edges"]]
        antonim = " ".join([f"`{i}`" for i in antonim])

        embed = discord.Embed(
            title=query,
            description=f"Synonyms: {sinonim}\n\nAntonyms: {antonim}",
            color=0x58bce2,
            url=f"https://www.powerthesaurus.org/{urllib.parse.quote(query)}"
        )
        embed.set_author(
            name=ctx.author.display_name,
            url=ctx.message.jump_url,
            icon_url=ctx.author.display_avatar
        )
        embed.set_thumbnail(
            url="https://www.radyushin.com/images/pt_logo_1200x1200.png"
        )
        embed.set_footer(
            text="power thesaurus | v1.0",
            icon_url="https://www.powerthesaurus.org/apple-touch-icon.png"
        )
        return await ctx.send(embed=embed)

@bot.event
async def on_disconnect():
    await bot.sesi.close()


@bot.command(name="image2ass")
async def image2ass(ctx):
    async with aiohttp.ClientSession() as sesi:
        async with sesi.get(ctx.message.attachments[0].url) as respon:
            data = await respon.read()

    with open("temp.png", "wb") as f:
        f.write(data)

    teks = png_to_ass("temp.png")

    with open("temp.txt", "w") as f:
        f.write(teks)

    return await ctx.send(file=discord.File("temp.txt"))


@bot.command(name="eval", description="Membuat bot menjalankan kode", aliases=["exec"], usage="<kode>")
@commands.is_owner()
async def _eval(ctx, *, code):
    code = clean_code(code)
    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message
    }
    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(f"async def func():\n{textwrap.indent(code, '    ')}", local_variables)

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pagination(bot, [result[i:i + 2000] for i in range(0, len(result), 2000)], title="Perintah Eval")

    await pager.start(ctx)


if __name__ == "__main__":
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)
