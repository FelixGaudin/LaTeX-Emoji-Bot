import re

s = "😁 COUCOU 😊🤭"

for i, e in enumerate(re.split(r'([^\x00-\xFF])', s)):
    if (i % 2) == 0:
        print(i, e)
    else:
        print(i, f'U+{ord(e):X}')
