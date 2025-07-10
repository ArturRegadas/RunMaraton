FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Instala build-essential (gcc, g++ e outras ferramentas) + libpq-dev para psycopg2
RUN apt-get update && apt-get install -y gcc g++ libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
