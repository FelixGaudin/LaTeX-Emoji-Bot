# LaTex Bot with emojis

## Inspiration
* For the LaTeX part : https://github.com/paradox-bot/paradox (the `fancycom.sty` file and the ideas for `convert.sh`)
* For the unicode Emoji's : https://github.com/alecjacobson/coloremoji.sty (the `coloremoji.sty` and the folder `emoji_images`)

## How to deploy

Make a private.py file that looks like :

```py
TOKEN = "Your bot token"
```

Then install the discord dependcie

```bash
pip3 install discord.py
```

Then run it !

```py
python3 converter.py
```