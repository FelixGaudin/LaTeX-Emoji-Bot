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

def emote_finder(s):
    pattern = re.compile("<(?:a)?:[^:]+:([0-9]+)>")
    return re.split(pattern, s)

class Converter(commands.Cog):
    @commands.max_concurrency(1, wait=True)
    @commands.command()
    async def tex(self, ctx, *message : str):

        content = " ".join(message)
        token = ctx.author.id
        path = os.path.join(current_path, f"{token}")

        text = r"\documentclass[preview, 12pt]{standalone}\nonstopmode\usepackage{amsmath}\usepackage{fancycom}\usepackage{color}\usepackage{tikz-cd}\begin{document}"
        tokenised = emote_finder(content)
        for i, e in enumerate(tokenised):
            if (i % 2 == 0):
                # normal text
                text += r"\textcolor{white}{" + e + r"}"
            else:
                # Create a folder to store emotes
                # https://appdividend.com/2021/07/03/how-to-create-directory-if-not-exist-in-python/
                if not os.path.exists(path):
                    os.makedirs(path)
                # Download the emote
                emote_path = os.path.join(path, f"{e}.png")
                if not os.path.isfile(emote_path):
                    # https://stackoverflow.com/questions/30229231/python-save-image-from-url
                    emote_data = requests.get(f"https://cdn.discordapp.com/emojis/{e}").content
                    with open(emote_path, 'wb') as handler:
                        handler.write(emote_data)

                text += r"\raisebox{-0.2\height}{\includegraphics[height=6mm]{" + emote_path + r"} }"
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

bot.add_cog(Converter())

bot.run(TOKEN)
