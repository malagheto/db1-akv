# arquivo: crud_local.py

from typing import List, Tuple, Optional
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_local(nome: str, capacidade: int, endereco: Optional[str] = None) -> int:
    """
    Insere um novo local.
    Requer nome e capacidade. Endereço é opcional.
    Retorna o ID do local criado.
    """
    # Validação de capacidade conforme a regra CHECK(capacidade > 0)
    if capacidade <= 0:
        raise ValueError("Capacidade deve ser um número positivo.")
        
    sql = "INSERT INTO Local (nome, endereco, capacidade) VALUES (%s, %s, %s) RETURNING id_local;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (nome, endereco, capacidade))
            local_id = cur.fetchone()[0]
        conn.commit()
    return local_id

def read_locais() -> List[Tuple]:
    """Retorna todos os locais cadastrados, ordenados por nome."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_local, nome, endereco, capacidade FROM Local ORDER BY nome;")
            return cur.fetchall()

def update_local(local_id: int, 
                 nome: Optional[str] = None, 
                 endereco: Optional[str] = None, 
                 capacidade: Optional[int] = None) -> int:
    """
    Atualiza dados de um local. Retorna o número de linhas afetadas.
    Pelo menos um dos campos opcionais (nome, endereco, capacidade) deve ser fornecido.
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    
    if endereco is not None:
        updates.append("endereco = %s")
        params.append(endereco)

    if capacidade is not None:
        if capacidade <= 0:
            raise ValueError("Capacidade deve ser um número positivo.")
        updates.append("capacidade = %s")
        params.append(capacidade)
    
    if not updates:
        # Nada a atualizar
        return 0
    
    params.append(local_id)
    
    sql = f"UPDATE Local SET {', '.join(updates)} WHERE id_local = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    
    return rows

def delete_local(local_id: int) -> int:
    """
    Remove um local. Retorna o número de linhas afetadas.
    Nota: A deleção falhará (ON DELETE RESTRICT) se o local
    estiver sendo usado por algum Evento. [cite: 292]
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Local WHERE id_local = %s;", (local_id,))
            rows = cur.rowcount
        conn.commit()
    return rows