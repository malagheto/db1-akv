# arquivo: crud_assento.py

from typing import List, Tuple, Optional
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_assento(id_setor: int, fileira: str, numero: str) -> int:
    """
    Insere um novo assento em um setor específico.
    Requer 'id_setor', 'fileira' e 'numero'.
    Retorna o ID do assento criado.
    
    Nota: Falhará se a combinação (id_setor, fileira, numero) já existir.
    """
    sql = "INSERT INTO Assento (id_setor, fileira, numero) VALUES (%s, %s, %s) RETURNING id_assento;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_setor, fileira, numero))
            assento_id = cur.fetchone()[0]
        conn.commit()
    return assento_id

def read_assentos_por_setor(setor_id: int) -> List[Tuple]:
    """
    Retorna todos os assentos (id, fileira, numero) de um setor específico.
    """
    sql = "SELECT id_assento, fileira, numero FROM Assento WHERE id_setor = %s ORDER BY fileira, numero;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (setor_id,))
            return cur.fetchall()

def update_assento(assento_id: int, 
                   fileira: Optional[str] = None, 
                   numero: Optional[str] = None,
                   id_setor: Optional[int] = None) -> int:
    """
    Atualiza dados de um assento (fileira, numero ou a qual setor pertence).
    Retorna o número de linhas afetadas.
    
    Nota: Falhará se a nova combinação (id_setor, fileira, numero) violar a restrição UNIQUE.
    """
    updates = []
    params = []
    
    if fileira is not None:
        updates.append("fileira = %s")
        params.append(fileira)
    
    if numero is not None:
        updates.append("numero = %s")
        params.append(numero)
        
    if id_setor is not None:
        # Permite mover o assento para outro setor
        updates.append("id_setor = %s")
        params.append(id_setor)
    
    if not updates:
        return 0
    
    params.append(assento_id)
    sql = f"UPDATE Assento SET {', '.join(updates)} WHERE id_assento = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    
    return rows

def delete_assento(assento_id: int) -> int:
    """
    Remove um assento. Retorna o número de linhas afetadas.
    
    Atenção: Se este assento estiver vinculado a um Ingresso,
    o campo 'id_assento' no Ingresso será definido como NULL
    (ON DELETE SET NULL), transformando-o em um ingresso "pista".
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Assento WHERE id_assento = %s;", (assento_id,))
            rows = cur.rowcount
        conn.commit()
    return rows