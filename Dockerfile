FROM python:3.8
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

# PIP
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt

# DJANGO
ADD . /app/
