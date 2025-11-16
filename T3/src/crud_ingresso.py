# arquivo: crud_ingresso.py

from typing import List, Tuple, Optional
# Importa o tipo Decimal para lidar com o preco (NUMERIC)
from decimal import Decimal
# Importa a função de conexão do arquivo db.py
from db import get_conn 

# --- Funções de Criação (Transacionais) ---

def create_ingresso_vip(id_evento: int, preco: Decimal, 
                      id_assento: Optional[int], 
                      beneficios: Optional[str]) -> int:
    """
    Cria um INGRESSO VIP.
    Insere na superclasse 'Ingresso' e na subclasse 'Ingresso_VIP'
    dentro de uma única transação.
    Retorna o ID do novo ingresso criado.
    """
    # A
    sql_ingresso = """
        INSERT INTO Ingresso (id_evento, preco, id_assento) 
        VALUES (%s, %s, %s) 
        RETURNING id_ingresso;
    """
    sql_vip = "INSERT INTO Ingresso_VIP (id_ingresso, beneficios) VALUES (%s, %s);"
    
    # O bloco 'with get_conn() as conn' gerencia a transação.
    # Se qualquer comando falhar, o rollback é automático.
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. Insere na tabela 'Ingresso' (superclasse)
            cur.execute(sql_ingresso, (id_evento, preco, id_assento))
            # 2. Obtém o ID do ingresso recém-criado
            id_ingresso = cur.fetchone()[0]
            
            # 3. Insere na tabela 'Ingresso_VIP' (subclasse)
            cur.execute(sql_vip, (id_ingresso, beneficios))
            
        conn.commit() # Comita a transação
    return id_ingresso

def create_ingresso_padrao(id_evento: int, preco: Decimal, 
                         id_assento: Optional[int]) -> int:
    """
    Cria um INGRESSO PADRÃO.
    Insere na superclasse 'Ingresso' e na subclasse 'Ingresso_Padrao'
    dentro de uma única transação.
    Retorna o ID do novo ingresso criado.
    """
    sql_ingresso = """
        INSERT INTO Ingresso (id_evento, preco, id_assento) 
        VALUES (%s, %s, %s) 
        RETURNING id_ingresso;
    """
    sql_padrao = "INSERT INTO Ingresso_Padrao (id_ingresso) VALUES (%s);"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. Insere na tabela 'Ingresso'
            cur.execute(sql_ingresso, (id_evento, preco, id_assento))
            id_ingresso = cur.fetchone()[0]
            
            # 2. Insere na tabela 'Ingresso_Padrao'
            cur.execute(sql_padrao, (id_ingresso,))
            
        conn.commit() # Comita a transação
    return id_ingresso

# --- Funções de Leitura ---

def read_ingressos_por_evento(id_evento: int) -> List[Tuple]:
    """
    Retorna todos os ingressos de um evento, com detalhes de 
    VIP (beneficios) ou Padrão (id_ingresso_padrao).
    Usa LEFT JOIN para buscar os dados das subclasses.
    """
    sql = """
        SELECT 
            i.id_ingresso, 
            i.preco, 
            i.id_assento,
            vip.beneficios,         -- Será NULL se não for VIP
            padrao.id_ingresso     -- Será NULL se não for Padrão
        FROM Ingresso i
        LEFT JOIN Ingresso_VIP vip ON i.id_ingresso = vip.id_ingresso
        LEFT JOIN Ingresso_Padrao padrao ON i.id_ingresso = padrao.id_ingresso
        WHERE i.id_evento = %s
        ORDER BY i.id_ingresso;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id_evento,))
            return cur.fetchall()

# --- Funções de Atualização ---

def update_ingresso_comum(id_ingresso: int, 
                          preco: Optional[Decimal] = None, 
                          id_assento: Optional[int] = None) -> int:
    """
    Atualiza os campos comuns (na tabela Ingresso) de um ingresso.
    """
    updates = []
    params = []
    
    if preco is not None:
        updates.append("preco = %s")
        params.append(preco)
    if id_assento is not None:
        updates.append("id_assento = %s")
        params.append(id_assento)

    if not updates:
        return 0
    
    params.append(id_ingresso)
    sql = f"UPDATE Ingresso SET {', '.join(updates)} WHERE id_ingresso = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    return rows

def update_ingresso_vip_beneficios(id_ingresso: int, beneficios: str) -> int:
    """
    Atualiza os benefícios de um ingresso VIP (na tabela Ingresso_VIP).
    """
    sql = "UPDATE Ingresso_VIP SET beneficios = %s WHERE id_ingresso = %s;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (beneficios, id_ingresso))
            rows = cur.rowcount
        conn.commit()
    return rows

# --- Função de Deleção ---

def delete_ingresso(id_ingresso: int) -> int:
    """
    Deleta um ingresso da tabela 'Ingresso' (superclasse).
    As regras 'ON DELETE CASCADE'  no seu BD irão 
    automaticamente deletar a entrada correspondente em 'Ingresso_VIP' 
    ou 'Ingresso_Padrao'.
    
    Atenção: Falhará (ON DELETE RESTRICT) [cite: 205, 260] se o ingresso 
    já tiver sido associado a uma 'Venda'.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Ingresso WHERE id_ingresso = %s;", (id_ingresso,))
            rows = cur.rowcount
        conn.commit()
    return rows