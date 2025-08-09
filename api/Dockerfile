FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8026

ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python3", "/app/api/run.py"]
