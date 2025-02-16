FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python3", "/app/calendar_worker/app/main.py"]
