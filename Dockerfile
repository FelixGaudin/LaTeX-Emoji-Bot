FROM ubuntu:22.04

WORKDIR /usr/src/app

# https://askubuntu.com/questions/909277/avoiding-user-interaction-with-tzdata-when-installing-certbot-in-a-docker-contai
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt-get update
RUN apt-get -y install texlive-latex-base 
# RUN apt-get -y install texlive-fonts-recommended
# RUN apt-get -y install texlive-fonts-extra
RUN apt-get -y install texlive-latex-extra

RUN apt-get -y install imagemagick
RUN apt-get -y install python3-pip


COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

ENV TZ="Europe/Amsterdam"

COPY . .

RUN cp IM-policy.xml /etc/ImageMagick-6/policy.xml

RUN python3 emoji_scraper.py

CMD ["python3", "converter.py"]