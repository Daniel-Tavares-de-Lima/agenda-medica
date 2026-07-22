# Imagem do app web (login + agenda).

FROM python:3.11-slim

WORKDIR /app

# Instala as libs primeiro 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app ./app
COPY seed.py run.py docker-entrypoint.sh ./

RUN chmod +x docker-entrypoint.sh

# Caminho do banco dentro do container 
ENV DATABASE_PATH=/app/data/agenda.db

EXPOSE 5000

# Antes de subir o Flask, roda o seed
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
