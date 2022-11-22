FROM python:3.9-alpine

RUN mkdir /app
WORKDIR /app
COPY ./app /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN adduser -D user

USER user
