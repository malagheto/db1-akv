# arquivo: prototipo_tikevents.py
# Requisitos: pip install psycopg2-binary

import psycopg2
from typing import List, Tuple, Optional

# Configuração da conexão
DSN = "dbname=tikevents user=dev password=devpass host=localhost port=5432"

# DDL para criar tabela se não existir
DDL = """
CREATE TABLE IF NOT EXISTS Artista (
    id_artista SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    genero VARCHAR(50)
);
"""

def get_conn():
    """Retorna uma nova conexão com o banco de dados."""
    return psycopg2.connect(DSN)