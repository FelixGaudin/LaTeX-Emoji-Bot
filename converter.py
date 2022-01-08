import subprocess
import os
import pathlib
import re
import requests
import discord
from discord.ext import commands
from private import TOKEN

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="??", intents=intents)

# get the path to the bash script converter
current_path = pathlib.Path().resolve()
converter = os.path.join(current_path, 'convert.sh')

def texit_compatibility(content):

    content = content.replace('€', '$')   # normal math

    # centered math : \[ shitty maths \]
    content = content.replace(r'\{', r'\[')  # support with textit
    content = content.replace(r'\}', r'\]')  # support with textit

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

class Converter(commands.Cog):
    @commands.max_concurrency(1, wait=True)
    @commands.command()
    async def tex(self, ctx, *message : str):

        content = " ".join(message)
        content = texit_compatibility(content)

        token = ctx.author.id
        path = os.path.join(current_path, f"{token}")

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
        try:
            # Convert LaTex to PNG image
            try:
                rc = subprocess.check_call([converter, f'{token}'])
            except:
                # ¯\_(ツ)_/¯ Maybe it works
                pass
            finally:
                image = f"{token}.png"
                await ctx.send(file=discord.File(image))
                os.remove(image)
        except Exception as e:
            print(e)
            await ctx.send("Aled ça a pas marché : ¯\_(ツ)_/¯")

    @commands.command()
    async def tex_help(self, ctx, *message):
        embed=discord.Embed(title="LaTeX Bot", url="https://github.com/FelixGaudin/LaTeX-Emoji-Bot", description="A bot to have some beautifull LaTeX in discord", color=0xfce94f)
        embed.set_author(name="Félix#9897", url="https://github.com/FelixGaudin", icon_url="https://avatars.githubusercontent.com/u/44848675?v=4")
        embed.add_field(name="Inspiration", value="The TeXiT bot (https://top.gg/fr/bot/510789298321096704)", inline=False)
        embed.add_field(name="Change compared to TeXiT", value=r"To deal with a TeXiT bot on the same server, the '$' became a '€' and the '\[ \]' became a '\{ \}'", inline=False)
        embed.add_field(name="Emojis", value="The unicode emoji's are webscrapped from https://unicode.org/emoji/charts/full-emoji-list.html", inline=False)
        embed.set_footer(text="If you get any troubles with the bot don't hesitate to contact me (Félix#9897) or post an issue on GitHub : https://github.com/FelixGaudin/LaTeX-Emoji-Bot")
        await ctx.send(embed=embed)

bot.add_cog(Converter())

bot.run(TOKEN)
