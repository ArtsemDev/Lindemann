FROM python:3.11.7-alpine3.19

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt