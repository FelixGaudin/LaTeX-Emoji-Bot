# %%
import requests
from bs4 import BeautifulSoup
import base64
import os

# %%
URL = "https://unicode.org/emoji/charts/full-emoji-list.html"
r = requests.get(URL)
r.status_code

# %%
soup = BeautifulSoup(r.content, 'html5lib')

# %%
folder_name = "emotes"

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# %%
for i, row in enumerate(soup.find('table', border=1).find('tbody').find_all('tr')):
    try: 
        # print(row.find('a').text)
        code = row.find('a').text
        # print(row.find_all('img', {"class": "imga"})[4]['src'])
        # https://stackoverflow.com/questions/32428950/converting-base64-to-an-image-incorrect-padding-error
        data = row.find_all('img', {"class": "imga"})[4]['src'].split(",")[1].encode()
        # print(data)
        # https://stackoverflow.com/questions/2323128/convert-string-in-base64-to-image-and-save-on-filesystem
        for c in code.split(' '):
            with open(f'{folder_name}/{c}.png', 'wb') as fh:
                fh.write(base64.decodebytes(data))
    except:
        pass # azy ça marche



