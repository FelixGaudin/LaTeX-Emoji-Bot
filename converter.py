import asyncio
import subprocess
import os
import pathlib
import re
import requests
import discord
from discord.ext import commands
from private import TOKEN

intents = discord.Intents().all()
PREFIX = "??"

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# get the path to the bash script converter
current_path = pathlib.Path().resolve()
converter = os.path.join(current_path, 'convert.sh')

saving_folder_path = os.path.join(current_path, "sources")

reactions = {
    '❌' : 'remove', 
    '📕' : 'remove_source' , 
    '📋' : 'get_source'
}

if not os.path.exists(saving_folder_path):
    os.makedirs(saving_folder_path)

def texit_compatibility(content):

    if content.startswith(f"{PREFIX}tex"):
        content = content.replace(f"{PREFIX}tex", "")

    content = content.replace('€', '$')   # normal math

    # centered math : \[ shitty maths \]
    content = content.replace(r'/{', r'\[')  # support with textit
    content = content.replace(r'/}', r'\]')  # support with textit

    return content

def make_text(s):
    return r"\textcolor{white}{" + s + r"}"

def discord_emote_finder(s):
    pattern = re.compile("<(?:a)?:[^:]+:([0-9]+)>")
    return re.split(pattern, s)

def unicode_emote_finder(s):
    return re.split(r'([^\x00-\xFF])', s)

def format_text_part(e):
    resp = ''
    # no discord emoji here
    for ii, ee in enumerate(unicode_emote_finder(e)):
        if (ii % 2) == 0:
                resp += make_text(ee)
        else:
            # unicode emoji
            unicode_emote = f'U+{ord(ee):X}'
            emote_path = os.path.join(
                current_path, f"emotes/{unicode_emote}.png")
            if os.path.isfile(emote_path):
                resp += r"\raisebox{-0.2\height}{\includegraphics[height=6mm]{" + emote_path + r"} }"
            else:
                resp += make_text(f" [{unicode_emote}] ")
    return resp

def format_emote_part(e, path):
    # Create a folder to store emotes if not exists
    # https://appdividend.com/2021/07/03/how-to-create-directory-if-not-exist-in-python/
    if not os.path.exists(path):
        os.makedirs(path)
    # Download the emote if not done yet
    emote_path = os.path.join(path, f"{e}.png")
    if not os.path.isfile(emote_path):
        # https://stackoverflow.com/questions/30229231/python-save-image-from-url
        emote_data = requests.get(
            f"https://cdn.discordapp.com/emojis/{e}").content
        with open(emote_path, 'wb') as handler:
            handler.write(emote_data)

    return r"\raisebox{-0.2\height}{\includegraphics[height=6mm]{" + emote_path + r"} }"


def get_source_path(token):

    return os.path.join(saving_folder_path, f"{token}.tex")

def save_source(content, token):
    
    with open(get_source_path(token), "w") as file:
        file.write(content)


def get_source(token):

    with open(get_source_path(token)) as file:
        return file.read()


def remove_source(token):

    os.remove(get_source_path(token))


def make_img(content, path, token):
    text = r"\documentclass[preview, 12pt]{standalone}\nonstopmode\usepackage{amsmath}\usepackage{fancycom}\usepackage{color}\usepackage{tikz-cd}\begin{document}"

    for i, e in enumerate(discord_emote_finder(content)):
        if (i % 2 == 0):
            # normal text
            text += format_text_part(e)
        else:
            text += format_emote_part(e, path)

    text += r"\end{document}"

    # write the LaTeX file
    with open(f"{token}.tex", 'w') as file:

        file.write(text)

    # output is maybe written as {token}.png
    rc = subprocess.check_call([converter, f'{token}'])

async def send_img(ctx, content, path, token, old_msg=None):
    author_pseudo = ctx.author.display_name
    author_name = f"{ctx.author.name}#{ctx.author.discriminator}"

    save_source(content, token)
    try:
        try:
            make_img(content, path, token)
        except:
            # ¯\_(ツ)_/¯ Maybe it works
            pass
        finally:
            image = f"{token}.png"
            if old_msg != None: await old_msg.delete()
            msg = await ctx.send(f"**{author_pseudo}** ({author_name})", file=discord.File(image))

            for emoji in reactions.keys():
                await msg.add_reaction(emoji)

            os.remove(image)
            return msg

    except Exception as e:
        print(e)
        if old_msg != None: await old_msg.delete()
        msg = await ctx.send("Aled ça a pas marché : ¯\_(ツ)_/¯")
        return msg


class Converter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.max_concurrency(1, wait=True)
    @commands.command()
    async def tex(self, ctx, *message : str):

        content = " ".join(message)

        token = f"{ctx.author.id}_{ctx.message.id}"
        path = os.path.join(current_path, f"{token}")

        try:
            msg = await ctx.send("Loading") 

            while True:

                msg = await send_img(ctx, texit_compatibility(content), path, token, msg)
                _, new = await bot.wait_for('message_edit', timeout=42, check = lambda x, n : n.id == ctx.message.id)
                content = new.content

        except asyncio.TimeoutError:
            
            for emoji in reactions.keys():
                await msg.clear_reaction(emoji)

            remove_source(token)

    @commands.command()
    async def tex_help(self, ctx, *message):

        embed=discord.Embed(title="LaTeX Bot", url="https://github.com/FelixGaudin/LaTeX-Emoji-Bot", description="A bot to have some beautifull LaTeX in discord", color=0xfce94f)
        embed.set_author(name="Félix#9897", url="https://github.com/FelixGaudin", icon_url="https://avatars.githubusercontent.com/u/44848675?v=4")
        embed.add_field(name="Inspiration", value="The TeXiT bot (https://top.gg/fr/bot/510789298321096704)", inline=False)
        embed.add_field(name="Change compared to TeXiT", value=r"To deal with a TeXiT bot on the same server, the '$' became a '€' and the '\\[ \\]' became a '/{ /}'", inline=False)
        embed.add_field(name="Emojis", value="The unicode emoji's are webscrapped from https://unicode.org/emoji/charts/full-emoji-list.html", inline=False)
        embed.set_footer(text="If you get any troubles with the bot don't hesitate to contact me (Félix#9897) or post an issue on GitHub : https://github.com/FelixGaudin/LaTeX-Emoji-Bot")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):

        channel = await self.bot.fetch_channel(ctx.channel_id)
        message = await channel.fetch_message(ctx.message_id)
        user = await self.bot.fetch_user(ctx.user_id)
        emoji = ctx.emoji

        attachements = message.attachments

        if len(attachements) > 0:
            try:

                first_attachement = attachements[0]

                author_id, old_message_id = [int(e) for e in first_attachement.filename.strip('.png').split('_')]
                
                if (author_id == user.id and user.id != message.id):
                    
                    action = reactions.get(str(emoji))

                    if action == "remove":

                        await message.delete()

                    elif action == "remove_source":

                        original_message = await channel.fetch_message(old_message_id)
                        await original_message.delete()

                    elif action == "get_source":

                        source = get_source(f"{author_id}_{old_message_id}")
                        await message.edit(content = f"```tex\n{source}\n```")

            except:
                pass


bot.add_cog(Converter(bot))

bot.run(TOKEN)
