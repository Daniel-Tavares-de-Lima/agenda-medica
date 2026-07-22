#!/bin/sh
# Entrypoint do container web:
# 1) cria o usuario de teste no SQLite
# 2) sobe o Flask

set -e

echo "Rodando seed..."
python seed.py

echo "Subindo o app web..."
exec python run.py
