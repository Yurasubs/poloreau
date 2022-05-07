import json

import discord
from discord.ext import commands
from datetime import datetime

anilist_id_query = """query media($id:Int,$type:MediaType,$isAdult:Boolean){Media(id:$id,type:$type,isAdult:$isAdult){id title{userPreferred romaji english native}coverImage{extraLarge large}bannerImage startDate{year month day}endDate{year month day}description season seasonYear type format status(version:2)episodes duration chapters volumes genres synonyms source(version:3)isAdult isLocked meanScore averageScore popularity favourites hashtag countryOfOrigin isLicensed isFavourite isRecommendationBlocked nextAiringEpisode{airingAt timeUntilAiring episode}relations{edges{id relationType(version:2)node{id title{userPreferred}format type status(version:2)bannerImage coverImage{large}}}}characterPreview:characters(perPage:6,sort:[ROLE,RELEVANCE,ID]){edges{id role name voiceActors(language:JAPANESE,sort:[RELEVANCE,ID]){id name{userPreferred}language:languageV2 image{large}}node{id name{userPreferred}image{large}}}}staffPreview:staff(perPage:8,sort:[RELEVANCE,ID]){edges{id role node{id name{userPreferred}language:languageV2 image{large}}}}studios{edges{isMain node{id name}}}reviewPreview:reviews(perPage:2,sort:[RATING_DESC,ID]){pageInfo{total}nodes{id summary rating ratingAmount user{id name avatar{large}}}}recommendations(perPage:7,sort:[RATING_DESC,ID]){pageInfo{total}nodes{id rating userRating mediaRecommendation{id title{userPreferred}format type status(version:2)bannerImage coverImage{large}}user{id name avatar{large}}}}externalLinks{site url}streamingEpisodes{site title thumbnail url}trailer{id site}rankings{id rank type format year season allTime context}tags{id name description rank isMediaSpoiler isGeneralSpoiler userId}mediaListEntry{id status score}stats{statusDistribution{status amount}scoreDistribution{score amount}}}}"""


class FSDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filename = "database/fsdb.json"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(name="rilis")
    async def rilis(self, ctx, *, judul):
        with open(self.filename, "r") as f:
            db_data = json.load(f)

        projects = db_data["projects"]

    @commands.command(name="tambahutang")
    async def tambahutang(self, ctx, anilist_id, *, staffs):
        with open(self.filename, "r") as f:
            db_data = json.load(f)

        if "projects" not in db_data:
            db_data["projects"] = {}

        projects = db_data["projects"]

        if anilist_id in projects:
            message_author = ctx.message.author
            embed = discord.Embed(
                title="Tambah Hutang",
                description="Hutang sudah ada di database.",
                url=ctx.message.jump_url,
                color=self.bot.default_color
            )

            embed.set_author(
                name=message_author.display_name,
                icon_url=message_author.display_avatar.url
            )
            embed.set_footer(
                text="Tambah Admin | v0.1",
                icon_url=self.bot.user.display_avatar.url
            )

            return await ctx.send(embed=embed)

        staffs = staffs.split(" ")
        url = "https://graphql.anilist.co"
        payload = {
            "query": anilist_id_query,
            "variables": {
                "id": anilist_id,
                "type": "ANIME"
            }
        }
        async with self.bot.sesi.post(url, json=payload) as respon:
            data = await respon.json()

        data = data["data"]
        Media = data["Media"]

        # print(json.dumps(data, indent=4))
        title = Media["title"]["romaji"]
        cover = Media["coverImage"]["extraLarge"]
        start_date = Media["startDate"]
        now = datetime.now()
        start_date = datetime(year=start_date["year"], month=start_date["month"] if start_date["month"] else now.month, day=start_date["day"] if start_date["day"] else now.day)
        roles = ["tm", "tl", "tlc", "ts", "ed", "kfx", "enc", "qc"]
        staff = {}
        user_dataset = []

        for n, v in enumerate(staffs):
            try:
                user = await ctx.guild.fetch_member(v)
            except discord.errors.NotFound:
                user = None
                staff[roles[n]] = None
            else:
                staff[roles[n]] = user.id

            user_dataset.append(user)

        episode_1 = {}
        for i in roles:
            episode_1[i] = False

        progress = {}
        progress["1"] = episode_1

        data = {
            "staff": staff,
            "progress": progress
        }

        db_data["projects"][anilist_id] = data

        with open(self.filename, "w") as f:
            json.dump(db_data, f, indent=4)

        message_author = ctx.message.author
        embed = discord.Embed(
            title=title,
            description="Hutang Berhasil ditambahkan.",
            url=ctx.message.jump_url,
            color=self.bot.default_color
        )
        embed.add_field(
            name="Staff",
            value="\n".join([f"**{roles[n].upper()}**: {v if v else '[Rahasia]'}" for n, v in enumerate(user_dataset)])
        )
        embed.set_author(
            name=message_author.display_name,
            icon_url=message_author.display_avatar.url
        )
        embed.set_thumbnail(
            url=cover
        )
        embed.set_footer(
            text="Tambah Hutang | v0.1",
            icon_url=self.bot.user.display_avatar.url
        )

        return await ctx.send(embed=embed)





    @commands.command(name="tambahadmin")
    async def tambahadmin(self, ctx, *, admin_ids):
        admin_ids = admin_ids.split(" ")
        user_dataset = []

        for i in admin_ids:
            user = await ctx.guild.fetch_member(i)

            user_dataset.append(user)

        with open(self.filename, "r") as f:
            data = json.load(f)

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            data[guild_id] = {
                "admins": []
            }

        if "admins" not in data[guild_id]:
            data[guild_id]["admins"] = []

        guild_admins = data[guild_id]["admins"]

        for i in user_dataset:
            if i not in guild_admins:
                guild_admins.append(i.id)

        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title="Tambah Admin",
            description="{}\nBerhasil ditambahkan sebagai admin guild di FSDB.".format("\n".join([f"{i.display_name}#{i.discriminator}" for i in user_dataset])),
            url=ctx.message.jump_url,
            color=self.bot.default_color
        )
        message_author = ctx.message.author

        embed.set_author(
            name=message_author.display_name,
            icon_url=message_author.display_avatar.url
        )
        embed.set_footer(
            text="Tambah Admin | v0.1",
            icon_url=self.bot.user.display_avatar.url
        )

        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FSDB(bot))
