FROM python:3.13-slim

EXPOSE 8000

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]