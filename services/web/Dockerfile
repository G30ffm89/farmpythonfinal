FROM python:3.9-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/src/app/farm_web_app

RUN apt-get update && apt-get install -y libglib2.0-0 libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
COPY . /usr/src/app/
#RUN groupadd -r farm_web_server && useradd -r -g farm_web_server farm_web_user
RUN groupadd -r --gid 1000 farm_web_server && useradd -r --uid 1000 -g farm_web_server farm_web_user
RUN chown -R farm_web_user:farm_web_server /usr/src/app/
USER farm_web_user
