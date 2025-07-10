# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos de requirements
COPY requirements.txt .

# Instala dependências de compilação e bibliotecas necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    # Remove os pacotes de build para deixar a imagem leve
    apt-get purge -y --auto-remove gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copia o restante da aplicação
COPY . .

# Expõe a porta do Flask (padrão 5000)
EXPOSE 5000

# Comando padrão
CMD ["python", "app.py"]
