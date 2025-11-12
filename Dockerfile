FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /bot

COPY requirements.txt requirements.txt

RUN apt-get update

RUN pip install -r requirements.txt

COPY . .

CMD python main.py
