# posts_service/Dockerfile
FROM python:3.11

COPY ./ /app

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
