# arquivo: crud_setor.py

from typing import List, Tuple, Optional
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_setor(nome: str, id_local: int) -> int:
    """
    Insere um novo setor para um local específico.
    Requer 'nome' e o 'id_local' ao qual pertence.
    Retorna o ID do setor criado.
    
    Nota: Falhará se o 'nome' já existir para esse 'id_local' (restrição UNIQUE).
    """
    sql = "INSERT INTO Setor (nome, id_local) VALUES (%s, %s) RETURNING id_setor;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (nome, id_local))
            setor_id = cur.fetchone()[0]
        conn.commit()
    return setor_id

def read_setores_por_local(local_id: int) -> List[Tuple]:
    """
    Retorna todos os setores (id_setor, nome) de um local específico.
    Esta será a função mais comum para listar setores.
    """
    sql = "SELECT id_setor, nome FROM Setor WHERE id_local = %s ORDER BY nome;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (local_id,))
            return cur.fetchall()

def read_todos_setores() -> List[Tuple]:
    """Retorna TODOS os setores de TODOS os locais."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Inclui o id_local para saber a qual local o setor pertence
            cur.execute("SELECT id_setor, nome, id_local FROM Setor ORDER BY id_local, nome;")
            return cur.fetchall()

def update_setor(setor_id: int, 
                 nome: Optional[str] = None, 
                 id_local: Optional[int] = None) -> int:
    """
    Atualiza dados de um setor (nome ou a qual local ele pertence).
    Retorna o número de linhas afetadas.
    
    Nota: Falhará se a nova combinação (nome, id_local) violar a restrição UNIQUE.
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    
    if id_local is not None:
        # Permite mover o setor para outro local
        updates.append("id_local = %s")
        params.append(id_local)
    
    if not updates:
        return 0
    
    params.append(setor_id)
    sql = f"UPDATE Setor SET {', '.join(updates)} WHERE id_setor = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    
    return rows

def delete_setor(setor_id: int) -> int:
    """
    Remove um setor. Retorna o número de linhas afetadas.
    Atenção: Deletar um setor irá apagar (CASCADE) todos os Assentos
    associados a ele.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Setor WHERE id_setor = %s;", (setor_id,))
            rows = cur.rowcount
        conn.commit()
    return rows