# arquivo: crud_evento.py

from typing import List, Tuple, Optional
# Importa os tipos date e time para os campos do evento
from datetime import date, time
# Importa a função de conexão do arquivo db.py
from db import get_conn 

def create_evento(nome: str, data: date, id_local: int, 
                  horario: Optional[time] = None, 
                  descricao: Optional[str] = None) -> int:
    """
    Insere um novo evento.
    Requer 'nome' [cite: 241], 'data' [cite: 242] e 'id_local'.
    'horario' [cite: 243] e 'descricao' [cite: 244] são opcionais.
    Retorna o ID do evento criado.
    
    Nota: Falhará se o id_local não existir.
    """
    sql = """
        INSERT INTO Evento (nome, data, horario, descricao, id_local) 
        VALUES (%s, %s, %s, %s, %s) 
        RETURNING id_evento;
    """
    params = (nome, data, horario, descricao, id_local)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            evento_id = cur.fetchone()[0]
        conn.commit()
    return evento_id

def read_todos_eventos() -> List[Tuple]:
    """
    Retorna todos os eventos cadastrados (id, nome, data, horario, id_local), 
    ordenados por data e horário.
    """
    sql = """
        SELECT id_evento, nome, data, horario, id_local 
        FROM Evento 
        ORDER BY data, horario;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

def read_eventos_por_local(local_id: int) -> List[Tuple]:
    """
    Retorna todos os eventos de um local específico, ordenados por data.
    """
    sql = """
        SELECT id_evento, nome, data, horario, descricao 
        FROM Evento 
        WHERE id_local = %s 
        ORDER BY data, horario;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (local_id,))
            return cur.fetchall()

def update_evento(evento_id: int, 
                  nome: Optional[str] = None, 
                  data: Optional[date] = None,
                  horario: Optional[time] = None,
                  descricao: Optional[str] = None,
                  id_local: Optional[int] = None) -> int:
    """
    Atualiza dados de um evento. Retorna o número de linhas afetadas.
    Permite alterar qualquer campo, incluindo mover o evento para outro local.
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    if data is not None:
        updates.append("data = %s")
        params.append(data)
    if horario is not None:
        updates.append("horario = %s")
        params.append(horario)
    if descricao is not None:
        updates.append("descricao = %s")
        params.append(descricao)
    if id_local is not None:
        updates.append("id_local = %s")
        params.append(id_local)
    
    if not updates:
        return 0
    
    params.append(evento_id)
    sql = f"UPDATE Evento SET {', '.join(updates)} WHERE id_evento = %s;"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.rowcount
        conn.commit()
    return rows

def delete_evento(evento_id: int) -> int:
    """
    Remove um evento. Retorna o número de linhas afetadas.
    
    Atenção: Deletar um evento irá apagar (ON DELETE CASCADE)  todos os
    Ingressos e registros de Evento_Artista associados a ele.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Evento WHERE id_evento = %s;", (evento_id,))
            rows = cur.rowcount
        conn.commit()
    return rows