# arquivo: crud_evento_artista.py

from typing import List, Tuple
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def associar_artista_evento(id_evento: int, id_artista: int) -> int:
    """
    Associa um artista a um evento (insere um registro na tabela N:N).
    Retorna o número de linhas afetadas (1 se sucesso).
    
    Nota: Falhará se a associação já existir (PK violation) 
    ou se o evento/artista não existir (FK violation).
    """
    sql = "INSERT INTO Evento_Artista (id_evento, id_artista) VALUES (%s, %s);"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Em caso de erro (ex: duplicado), a exceção será 
            # propagada e deve ser tratada pelo 'main.py'
            cur.execute(sql, (id_evento, id_artista))
            rows = cur.rowcount
        conn.commit()
    return rows

def desassociar_artista_evento(id_evento: int, id_artista: int) -> int:
    """
    Desassocia um artista de um evento (remove o registro da tabela N:N).
    Retorna o número de linhas afetadas.
    """
    sql = "DELETE FROM Evento_Artista WHERE id_evento = %s AND id_artista = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_evento, id_artista))
            rows = cur.rowcount
        conn.commit()
    return rows

def read_artistas_por_evento(id_evento: int) -> List[Tuple]:
    """
    Retorna todos os artistas (id, nome, genero) associados a um evento específico.
    Isso requer um JOIN com a tabela Artista.
    """
    sql = """
        SELECT a.id_artista, a.nome, a.genero 
        FROM Artista a
        JOIN Evento_Artista ea ON a.id_artista = ea.id_artista
        WHERE ea.id_evento = %s
        ORDER BY a.nome;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_evento,))
            return cur.fetchall()

def read_eventos_por_artista(id_artista: int) -> List[Tuple]:
    """
    Retorna todos os eventos (id, nome, data) aos quais um artista específico
    está associado.
    Isso requer um JOIN com a tabela Evento.
    """
    sql = """
        SELECT e.id_evento, e.nome, e.data 
        FROM Evento e
        JOIN Evento_Artista ea ON e.id_evento = ea.id_evento
        WHERE ea.id_artista = %s
        ORDER BY e.data;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_artista,))
            return cur.fetchall()