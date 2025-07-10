# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos de requirements
COPY requirements.txt .


# Instala dependências (usando build tools pra psycopg2)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc

# Copia o restante da aplicação
COPY . .

# Expõe a porta do Flask (por padrão 5000)
EXPOSE 5000

# Comando padrão (pode mudar dependendo de como roda seu app)
CMD ["python", "app.py"]
