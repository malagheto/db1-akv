# arquivo: crud_venda.py

from typing import List, Tuple, Optional
from datetime import date
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_venda(data: date, quantidade: int, id_ingresso: int, id_comprador: int) -> int:
    """
    Registra uma nova venda.
    Requer 'data' da transação, 'quantidade', 'id_ingresso' e 'id_comprador'.
    Retorna o ID da venda criada.
    
    Nota: Falhará se 'quantidade' <= 0 (CHECK constraint) ou
    se o ingresso/comprador não existir (FK constraint).
    """
    if quantidade <= 0:
        raise ValueError("Quantidade deve ser um número positivo.")
        
    sql = """
        INSERT INTO Venda (data, quantidade, id_ingresso, id_comprador) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id_venda;
    """
    params = (data, quantidade, id_ingresso, id_comprador)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            venda_id = cur.fetchone()[0]
        conn.commit()
    return venda_id

def read_vendas_por_comprador(id_comprador: int) -> List[Tuple]:
    """
    Retorna o histórico de vendas de um comprador específico.
    Junta com Ingresso para mostrar o preço e o evento.
    Junta com Evento para mostrar o nome do evento.
    (Esta é uma consulta com 3 tabelas: Venda, Ingresso, Evento)
    """
    sql = """
        SELECT 
            v.id_venda, 
            v.data, 
            e.nome AS nome_evento, 
            i.preco,
            v.quantidade,
            (i.preco * v.quantidade) AS total
        FROM Venda v
        JOIN Ingresso i ON v.id_ingresso = i.id_ingresso
        JOIN Evento e ON i.id_evento = e.id_evento
        WHERE v.id_comprador = %s
        ORDER BY v.data DESC;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_comprador,))
            return cur.fetchall()

def read_vendas_por_evento(id_evento: int) -> List[Tuple]:
    """
    Retorna todas as vendas de um evento específico.
    Junta com Ingresso e Comprador para mostrar detalhes.
    (Esta é uma consulta com 3 tabelas: Venda, Ingresso, Comprador)
    """
    sql = """
        SELECT 
            v.id_venda, 
            v.data, 
            c.nome AS nome_comprador, 
            c.email AS email_comprador,
            i.id_ingresso,
            i.preco,
            v.quantidade
        FROM Venda v
        JOIN Ingresso i ON v.id_ingresso = i.id_ingresso
        JOIN Comprador c ON v.id_comprador = c.id_comprador
        WHERE i.id_evento = %s
        ORDER BY v.data;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_evento,))
            return cur.fetchall()

def update_venda(id_venda: int, 
                 data: Optional[date] = None, 
                 quantidade: Optional[int] = None,
                 id_ingresso: Optional[int] = None,
                 id_comprador: Optional[int] = None) -> int:
    """
    Atualiza dados de uma venda (ex: corrigir quantidade ou data).
    Retorna o número de linhas afetadas.
    """
    updates = []
    params = []
    
    if data is not None:
        updates.append("data = %s")
        params.append(data)
    if quantidade is not None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser um número positivo.")
        updates.append("quantidade = %s")
        params.append(quantidade)
    if id_ingresso is not None:
        updates.append("id_ingresso = %s")
        params.append(id_ingresso)
    if id_comprador is not None:
        updates.append("id_comprador = %s")
        params.append(id_comprador)
    
    if not updates:
        return 0
    
    params.append(id_venda)
    sql = f"UPDATE Venda SET {', '.join(updates)} WHERE id_venda = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    return rows

def delete_venda(id_venda: int) -> int:
    """
    Remove um registro de venda (ex: cancelamento).
    Retorna o número de linhas afetadas.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Venda WHERE id_venda = %s;", (id_venda,))
            rows = cur.rowcount
        conn.commit()
    return rows