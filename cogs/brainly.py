import asyncio
import binascii
import json
import os
from datetime import datetime, date

import aiohttp
import bs4
import discord
from discord.embeds import EmptyEmbed
from discord.ext import commands, tasks

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class Brainly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bucket = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @staticmethod
    def generate_id():
        return binascii.b2a_hex(os.urandom(4)).decode()

    @tasks.loop(minutes=1)
    async def create_brainly_account(self):
        filename = "database/brainly_bucket.json"

        with open(filename, "r") as f:
            data = json.load(f)

        if data["last_requests"] == "":
            return

        if data["requests_queue"] == []:
            return

        requests_queue = data["requests_queue"]
        url = ""
        payload = requests_queue.pop(0)
        response_queue = data["response_queue"]

        async with aiohttp.ClientSession() as sesi:
            async with sesi.post(url, json=payload["data"]) as respon:
                data = await respon.json()

        response_queue.append(data)

        payload = {
            "last_requests": datetime.now(),
            "requests_queue": requests_queue,
            "response_queue": response_queue
        }

        with open(filename, "w") as f:
            return json.dump(payload, f, indent=4, cls=DateTimeEncoder)

    async def add_account_requests(self, payload):
        filename = "database/brainly_bucket.json"

        with open(filename, "r") as f:
            data = json.load(f)

        _id = self.generate_id()
        data = {
            "id": _id,
            "data": data
        }

        data["requests_queue"].append(data)

        while True:
            with open(filename, "r") as f:
                data = json.load(f)

            for i in data["requests_queue"]:
                if i["id"] == "_id":
                    return i["data"]

    async def http_request(self, url, _method, _type, **kwargs):
        async with aiohttp.ClientSession() as sesi:
            async with getattr(sesi, _method)(url, **kwargs) as respon:
                data = await getattr(respon, _type)()

        return data

    async def start_brainly_ask_session(self, ctx):
        author = ctx.author

        def _embed(entri=None, url=None, author_name=None, author_avatar=None, image=None):
            e = discord.Embed(title="Brainly", description=entri if entri else EmptyEmbed, url="https://brainly.co.id/" if not url else url, color=0xd9f0ff)

            e.set_author(name=author.display_name if not author_name else author_name, url=ctx.message.jump_url, icon_url=author.display_avatar.url if not author_avatar else author_avatar)
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/836054125338034240/892286043200577546/brainly_logo.png")
            e.set_image(url="https://cdn.discordapp.com/attachments/836054125338034240/893464115333451836/test.png" if not image else image)
            e.set_footer(text="Brainly | Jaringan Pembelajaran Sosial | v0.1", icon_url="https://styleguide.brainly.com/images/favicons/brainly/favicon-hd-0865c7f19f.png")

            return e

        embed1 = _embed("Menyiapkan sesi...")
        embed_msg = await ctx.send(embed=embed1)

        def msg_check1(message):
            return message.channel == ctx.message.channel and message.author == ctx.message.author and message.content.isdigit()

        def interaction_check(interaction):
            return interaction.channel == ctx.message.channel and interaction.user == ctx.message.author and interaction.message == embed_msg

        async def timeout():
            embed3 = _embed("Batas waktu telah habis. Sesi ditutup.")

            return await embed_msg.edit(embed=embed3, view=None)

        while True:
            embed5 = _embed("Masukkan pertanyaan yang ingin anda tanyakan.")
            view2 = discord.ui.View()

            view2.add_item(
                discord.ui.Button(
                    custom_id=self.generate_id(),
                    emoji="🇽",
                    label="Keluar",
                    style=discord.ButtonStyle.danger
                )
            )

            await embed_msg.edit(embed=embed5, view=view2)

            def msg_check2(message):
                return message.channel == ctx.message.channel and message.author == ctx.message.author

            msg = asyncio.create_task(self.bot.wait_for("message", timeout=20, check=msg_check2))
            interaction2 = asyncio.create_task(self.bot.wait_for("interaction", timeout=20,check=interaction_check))
            done, pending = await asyncio.wait(
                [
                    msg,
                    interaction2
                ],
                return_when=asyncio.FIRST_COMPLETED
            )

            try:
                if msg in done:
                    msg = done.pop().result()
                    pertanyaan = msg.content

                    await msg.delete()
                elif interaction2 in done:
                    interaction2 = done.pop().result()
                    button2 = [i3 for i3 in view2.children if i3.custom_id == interaction2.data["custom_id"]][0]

                    if button2.label == "Keluar":
                        embed6 = _embed("Sesi ditutup.")

                        return await embed_msg.edit(embed=embed6, view=None)

            except asyncio.TimeoutError:
                return await timeout()

            for future in done:
                future.exception()

            for future in pending:
                future.cancel()

            mata_pelajaran = [
                {
                    "name": "SBMPTN",
                    "value": "24"
                },
                {
                    "name": "Ujian Nasional",
                    "value": "25"
                },
                {
                    "name": "Matematika",
                    "value": "2"
                },
                {
                    "name": "B. Indonesia",
                    "value": "1"
                },
                {
                    "name": "PPKn",
                    "value": "9"
                },
                {
                    "name": "IPS",
                    "value": "10"
                },
                {
                    "name": "Biologi",
                    "value": "4"
                },
                {
                    "name": "Fisika",
                    "value": "6"
                },
                {
                    "name": "Sejarah",
                    "value": "3"
                },
                {
                    "name": "B. inggris",
                    "value": "5"
                },
                {
                    "name": "Seni",
                    "value": "19"
                },
                {
                    "name": "Kimia",
                    "value": "7"
                },
                {
                    "name": "Geografi",
                    "value": "8"
                },
                {
                    "name": "TI",
                    "value": "11"
                },
                {
                    "name": "Ekonomi",
                    "value": "12"
                },
                {
                    "name": "B. Arab",
                    "value": "14"
                },
                {
                    "name": "B. Daerah",
                    "value": "13"
                },
                {
                    "name": "Penjaskes",
                    "value": "22"
                },
                {
                    "name": "Sosiologi",
                    "value": "20"
                },
                {
                    "name": "Bahasa lain",
                    "value": "18"
                },
                {
                    "name": "Wirausaha",
                    "value": "23"
                },
                {
                    "name": "Akuntansi",
                    "value": "21"
                },
                {
                    "name": "B. jepang",
                    "value": "15"
                },
                {
                    "name": "B. mandarin",
                    "value": "16"
                },
                {
                    "name": "B. perancis",
                    "value": "17"
                }
            ]
            option = []

            for i4 in mata_pelajaran:
                _selectOption = discord.SelectOption(
                    label=i4["name"]
                )
                option.append(_selectOption)

            embed3 = _embed(f"```{pertanyaan}```\nSilahkan pilih mata pelajaran atau ganti pertanyaan.")
            view2 = discord.ui.View()
            view2.add_item(
                discord.ui.Button(
                    custom_id=self.generate_id(),
                    emoji="🇽",
                    label="Keluar",
                    style=discord.ButtonStyle.danger
                )
            )
            view2.add_item(
                discord.ui.Button(
                    custom_id=self.generate_id(),
                    emoji="❔",
                    label="Ganti pertanyaan."
                )
            )
            view2.add_item(
                discord.ui.Select(
                    placeholder="Pilih mata pelajaran.",
                    min_values=1,
                    max_values=1,
                    options=option,
                    custom_id=self.generate_id()
                )
            )
            await embed_msg.edit(embed=embed3, view=view2)

            try:
                interaction3 = await self.bot.wait_for("interaction", timeout=20, check=interaction_check)
            except asyncio.TimeoutError:
                return await timeout()

            button3 = [i for i in view2.children if i.custom_id == interaction3.data["custom_id"]][0]

            if len(pertanyaan) > 19:
                if isinstance(button3, discord.ui.Button):
                    if button3.label == "Keluar":
                        return await embed_msg.edit(embed=_embed("Sesi ditutup."), view=None)
                    elif button3.label == "Ganti pertanyaan.":
                        pass
                elif isinstance(button3, discord.ui.Select):
                    subject_id = int([i["value"] for i in mata_pelajaran if interaction3.data["values"][0] == i["name"]][0])
                    break

        embed2 = _embed("Ketik umur anda.")
        view1 = discord.ui.View()

        view1.add_item(
            discord.ui.Button(
                custom_id=self.generate_id(),
                emoji="🇽",
                label="Keluar",
                style=discord.ButtonStyle.danger
            )
        )

        await embed_msg.edit(embed=embed2, view=view1)

        while True:
            msg1_bool = False
            interaction1_bool = False
            msg1 = asyncio.create_task(self.bot.wait_for("message", timeout=20, check=msg_check1))
            interaction1 = asyncio.create_task(self.bot.wait_for("interaction", timeout=20, check=interaction_check))
            done, pending = await asyncio.wait(
                [
                    msg1,
                    interaction1
                ],
                return_when=asyncio.FIRST_COMPLETED
            )

            try:
                if msg1 in done:
                    msg1 = done.pop().result()
                    msg1_bool = True
                elif interaction1 in done:
                    interaction1 = done.pop().result()
                    interaction1_bool = True
            except asyncio.TimeoutError:
                return await timeout()

            for future in done:
                future.exception()

            for future in pending:
                future.cancel()

            if msg1_bool:
                await msg1.delete()

                content = int(msg1.content)

                if content > 2 and content < 99:
                    umur = content

                    break

                teks = f"Umur {content} terlalu "
                if content < 3:
                    teks += "kecil"
                elif content > 98:
                    teks += "besar"

                teks += ". Masukkan umur anda."
                embed4 = _embed(teks)
                await embed_msg.edit(embed=embed4)

            elif interaction1_bool:
                button1 = [i2 for i2 in view1.children if i2.custom_id == interaction1.data["custom_id"]][0]

                if button1.label == "Keluar":
                    return await embed_msg.edit(embed=_embed("Sesi ditutup."), view=None)

        url = "https://www.fakenamegenerator.com/"
        data1 = await self.http_request(url, "get", "text")
        dateOfBirth = datetime.strptime(data1.split("ay</dt>\n    <dd>")[1].split("<")[0], "%B %d, %Y").strftime(
            "%m-%d")
        email = data1.split("         <dd>")[1].split(" ")[0]
        nick = data1.split("me</dt>\n    <dd>")[1].split("<")[0]
        password = data1.split("ord</dt>\n    <dd>")[1].split("<")[0]
        brainly_query = """mutation registerUser(
          $nick: String!
          $dateOfBirth: String!
          $country: String!
          $email: String
          $password: String
          $parentEmail: String
          $acceptedTermsOfService: Boolean
          $referrer: String
          $entry: String,
          $accountType: AccountType,
        ) {
          register(
            input: {
              nick: $nick
              dateOfBirth: $dateOfBirth
              country: $country
              email: $email
              password: $password
              parentEmail: $parentEmail
              acceptedTermsOfService: $acceptedTermsOfService
              referrer: $referrer
              entry: $entry,
              accountType: $accountType,
            }
          ) {
            token
            pendingToken
            validationErrors {
              type
              error
              path
            }
          }
        }"""
        payload = {
            "query": brainly_query,
            "operationName": "registerUser",
            "variables": {
                "acceptedTermsOfService": True,
                "accountType": None,
                "country": "ID",
                "dateOfBirth": f"{datetime.now().year - umur}-{dateOfBirth}",
                "email": email,
                "entry": "1",
                "nick": nick,
                "password": password
            }
        }

        print(json.dumps(payload, indent=4))

        url = "https://brainly.co.id/graphql/id"
        # data2_raw = await self.http_request(url, "post", "text", json=payload)
        data2_raw = await self.add_account_requests()
        data2 = data2_raw["data"]
        register = data2["register"]

        if not register:
            embed = _embed(json.dumps(data2_raw, idennt=4))

            return await embed_msg.edit(embed=embed, view=None)

            print(json.dumps(data2, indent=4))

        self.headers = {
            "Cookie": f"Zadanepl_cookie[Token][Long]={data2['data']['register']['token']}"
        }
        payload = {
            "attachments": [],
            "content": pertanyaan,
            "points": 50,
            "subject_id": subject_id
        }

        print(payload)

        url = "https://brainly.co.id/api/28/api_tasks/add"
        data3 = await self.http_request(url, "post", "json", headers=self.headers, json=payload)

        print(data3)
        if not data3["success"]:
            embed = _embed(data3["validation_errors"]["content"])
            return await embed_msg.edit(embed=embed, view=view)

        jawaban = []
        terjawab = []
        jawab_temp = []

        while len(terjawab) != 2:
            quest_url = f"https://brainly.co.id/tugas/{data3['data']['task']['id']}"
            headers = {
                "Cookie": f"Zadanepl_cookie[Token][Long]={data2['data']['register']['token']}"
            }
            # sesi = aiohttp.ClientSession(headers=headers)

            data = await self.http_request(quest_url, "get", "text", headers=headeers)
            # async with sesi.get(quest_url) as respon:
            #     data = await respon.text()

            sup = bs4.BeautifulSoup(data, "html.parser")
            elements1 = sup.select(
                "#question-sg-layout-container > div.brn-qpage-layout.js-main-container.js-ads-screening-content > div.brn-qpage-layout__main.empty\:sg-space-y-m.md\:empty\:sg-space-y-l > div.js-react-answers.js-question-answers.empty\:sg-space-y-m.md\:empty\:sg-space-y-l > div")

            if not elements1:
                teks = "Menunggu jawaban..."
            else:
                teks = f"{len(elements1)} jawaban tersedia."

            for element1 in elements1:
                avatar = element1.select_one("div.brn-qpage-next-answer-box__author > div > div.brn-qpage-next-answer-box-author__avatar > div > div > span > img")

                if avatar:
                    avatar = avatar["src"]
                else:
                    avatar = None

                element2 = element1.select_one(
                    "div.brn-qpage-next-answer-box__author > div > div.brn-qpage-next-answer-box-author__description > div.sg-flex > a > span.sg-hide-for-medium-up.sg-text--xsmall.sg-text.sg-text--link.sg-text--bold.sg-text--black").text.strip()
                elements3 = element1.select_one(
                    "div.brn-qpage-next-answer-box__content.js-answer-content-section > div > div > div")

                if not elements3 in jawab_temp:
                    jawab_temp.append(elements3)

                    teks_jawaban = ""

                    for element3 in elements3.children:
                        element4 = str(element3).replace("<p>", "").replace("</p>", "")
                        element5 = element4.replace("<strong>", "**").replace("</strong>", "**")
                        element6 = element5.replace("<em>", "*").replace("</em>", "*")
                        element7 = element6.replace("<u>", "__").replace("</u>", "__")
                        element8 = element7.replace("****", "")
                        element9 = element8.replace("____", "")
                        teks_jawaban += element9 + "\n"

                    data5 = {
                        "name": element2,
                        "value": teks_jawaban,
                        "avatar": avatar
                    }

                    jawaban.append(data5)

            embed6 = _embed(f"```{pertanyaan}```\n{teks}", url=quest_url)

            if jawaban != []:
                for i5 in jawaban:
                    if not i5 in terjawab:
                        if len(i5["value"]) > 1024:
                            value = f"...{i5['value'][-1021:]}"
                        else:
                            value = i5['value']

                        embed7 = _embed(entri=value, author_name=i5["name"], author_avatar=i5["avatar"] if avatar else None, url=quest_url)

                        terjawab.append(i5)

                        await ctx.send(content=f"<@{author.id}>", embed=embed7)

            await embed_msg.edit(embed=embed6, view=None)
            await asyncio.sleep(5)
            await sesi.close()

        print("Pertanyaan sudah menerima 2 jawaban")
        return

    @commands.group(name="brainly", description="Perintah Brainly", invoke_without_command=True)
    async def brainly(self, ctx):
        return await ctx.invoke(self.bot.get_command("help"), entity="brainly")

    @brainly.command(name="tanya", description="Menambah pertanyaan")
    async def tanya(self, ctx):
        return await self.start_brainly_ask_session(ctx)

    @commands.command(name="websocket")
    @commands.is_owner()
    async def test(self, ctx, _id):
        url = "https://brainly.co.id/"
        headers = {
            "Cookie": "Zadanepl_cookie[Token][Long]=VsotsXQGQUUER9Qs5Wf_GlkVlVYFozvCM_Ju8ozV4OU%3D"
        }

        async with self.sesi.get(url, headers=headers) as respon:
            data = respon.headers

        return await ctx.send(data)
        async with self.sesi.get("https://id-comet.z-dn.net:7879/socket.io/1/") as respon:
            data = await respon.text()

        async with self.sesi.ws_connect(f"wss://id-comet.z-dn.net:7879/socket.io/1/websocket/{data.split(':35:50:')[0]}") as respon:
            await ctx.send("Websocket terkoneksi.")

            payload = """"5:::{"args": [{"auth_hash": "5c75dacd59f0eac8271590d206dd178c", "avatar": "", "client": "desktop", "gender": 2, "nick": "raficanggih", "uid": 2056591, "version": "2.1"}], "name": "auth"}"""
            await respon.send_json(data=payload)

            while True:
                data = await respon.receive_str()

                print(data)

        return
        with open("test.html", "r") as f:
            data = f.read()

        sup = bs4.BeautifulSoup(data, "html.parser")
        elements1 = sup.select("#question-sg-layout-container > div.brn-qpage-layout.js-main-container.js-ads-screening-content > div.brn-qpage-layout__main.empty\:sg-space-y-m.md\:empty\:sg-space-y-l > div.js-react-answers.js-question-answers.empty\:sg-space-y-m.md\:empty\:sg-space-y-l > div")

        for element1 in elements1:
            element2 = element1.select_one("div.brn-qpage-next-answer-box__author > div > div.brn-qpage-next-answer-box-author__description > div.sg-flex > a > span.sg-hide-for-medium-up.sg-text--xsmall.sg-text.sg-text--link.sg-text--bold.sg-text--black")
            elements3 = element1.select_one("div.brn-qpage-next-answer-box__content.js-answer-content-section > div > div > div")
            teks = ""

            for element3 in elements3.findChildren(recursive=False):
                element4 = str(element3).replace("<p>", "").replace("</p>", "")

                element5 = element4.replace("<strong>", "**").replace("</strong>", "**")
                element6 = element5.replace("<em>", "*").replace("</em>", "*")
                element7 = element6.replace("<u>", "__").replace("</u>", "__")
                teks += element7 + "\n"


            # print(teks.encode())
            await ctx.send(teks)

def setup(bot):
    bot.add_cog(Brainly(bot))
