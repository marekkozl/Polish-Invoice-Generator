FROM ubuntu:14.04

RUN apt-get update -y

RUN apt-get install -y python2.7-dev python-pip

RUN apt-get install -y libjpeg-dev zlib1g-dev

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

add . /app

ADD *.ttf /usr/share/fonts/truetype/ttf-dejavu/

WORKDIR /app

RUN pip install -r requirements.txt

CMD python invoice.py

