FROM python:3.13-alpine

RUN pip install --no-cache-dir rq

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
