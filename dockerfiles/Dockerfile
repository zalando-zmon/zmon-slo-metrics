FROM registry.opensource.zalan.do/stups/python:latest

# libpq-dev is needed for PostgreSQL driver
RUN apt-get update && apt-get install -y libpq-dev

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY app /app

COPY swagger.yaml /

ENV FLASK_APP /app/main.py

CMD python -m app
