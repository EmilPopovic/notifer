FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src
COPY ./templates /app/templates
COPY ./static /app/static

EXPOSE 8026

ARG PYTHONPATH
ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python3", "/app/src/run.py"]
