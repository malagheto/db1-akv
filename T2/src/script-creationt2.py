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

def init_schema():
    """Inicializa o esquema do banco."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

def create_artista(nome: str, genero: Optional[str] = None) -> int:
    """Insere um novo artista. Retorna o ID criado."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Artista (nome, genero) VALUES (%s, %s) RETURNING id_artista;",
                (nome, genero)
            )
            artista_id = cur.fetchone()[0]
        conn.commit()
    return artista_id

def read_artistas() -> List[Tuple]:
    """Retorna todos os artistas cadastrados."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_artista, nome, genero FROM Artista ORDER BY nome;")
            return cur.fetchall()

def update_artista(artista_id: int, novo_nome: Optional[str] = None, 
                  novo_genero: Optional[str] = None) -> int:
    """Atualiza dados de um artista. Retorna linhas afetadas."""
    updates = []
    params = []
    
    if novo_nome is not None:
        updates.append("nome = %s")
        params.append(novo_nome)
    
    if novo_genero is not None:
        updates.append("genero = %s")
        params.append(novo_genero)
    
    if not updates:
        return 0
    
    params.append(artista_id)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE Artista SET {', '.join(updates)} WHERE id_artista = %s;",
                params
            )
            rows = cur.rowcount
        conn.commit()
    
    return rows

def delete_artista(artista_id: int) -> int:
    """Remove um artista. Retorna linhas afetadas."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Artista WHERE id_artista = %s;", (artista_id,))
            rows = cur.rowcount
        conn.commit()
    return rows

# Programa de teste
if __name__ == '__main__':
    init_schema()
    
    # CREATE - Inserir artistas
    a1 = create_artista('Radiohead', 'Rock Alternativo')
    a2 = create_artista('Björk', 'Art Pop')
    print(f'Artistas criados: {a1}, {a2}')
    
    # READ - Listar todos
    artistas = read_artistas()
    print(f'Lista de artistas: {artistas}')
    
    # UPDATE - Atualizar gênero
    update_artista(a2, novo_genero='Experimental')
    print('Gênero atualizado')
    
    # DELETE - Remover artista
    delete_artista(a1)
    print(f'Artista {a1} removido')
    
    # Verificar resultado final
    artistas_final = read_artistas()
    print(f'Lista final: {artistas_final}')