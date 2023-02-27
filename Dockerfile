FROM python:3.9-alpine

RUN mkdir /app
WORKDIR /app
COPY ./app /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache postgis 
RUN apk add --no-cache geos gdal gettext gcc tcl-dev binutils
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN adduser -D user

USER user
