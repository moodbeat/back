FROM python:3.11.1-slim

WORKDIR /app

COPY . /app/

RUN pip3 install -r ./requirements.txt --no-cache-dir

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]
