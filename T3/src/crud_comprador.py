# arquivo: crud_comprador.py

from typing import List, Tuple, Optional
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_comprador(nome: str, email: str) -> int:
    """
    Insere um novo comprador.
    Nome e email são obrigatórios.
    Retorna o ID do comprador criado.
    
    Nota: O email é UNIQUE, a função falhará se o email já existir.
    """
    sql = "INSERT INTO Comprador (nome, email) VALUES (%s, %s) RETURNING id_comprador;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (nome, email))
            comprador_id = cur.fetchone()[0]
        conn.commit()
    return comprador_id

def read_compradores() -> List[Tuple]:
    """Retorna todos os compradores cadastrados, ordenados por nome."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_comprador, nome, email FROM Comprador ORDER BY nome;")
            return cur.fetchall()

def update_comprador(comprador_id: int, 
                     nome: Optional[str] = None, 
                     email: Optional[str] = None) -> int:
    """
    Atualiza dados de um comprador. Retorna o número de linhas afetadas.
    Pelo menos um dos campos (nome, email) deve ser fornecido.
    
    Nota: A atualização falhará se o novo email já pertencer a outro comprador.
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    
    if not updates:
        # Nada a atualizar
        return 0
    
    params.append(comprador_id)
    
    sql = f"UPDATE Comprador SET {', '.join(updates)} WHERE id_comprador = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    
    return rows

def delete_comprador(comprador_id: int) -> int:
    """
    Remove um comprador. Retorna o número de linhas afetadas.
    Nota: A deleção falhará (ON DELETE RESTRICT) se o comprador
    estiver associado a alguma Venda.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Comprador WHERE id_comprador = %s;", (comprador_id,))
            rows = cur.rowcount
        conn.commit()
    return rows