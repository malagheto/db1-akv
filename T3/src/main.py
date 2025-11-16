# arquivo: main.py

import sys
import db # db.py para verificar a conexão inicial
from decimal import Decimal
from datetime import date, time

# --- Importando módulos CRUD ---
import crud_artista 
import crud_local
import crud_setor
import crud_assento
import crud_evento
import crud_evento_artista
import crud_ingresso
import crud_venda
import crud_comprador
# --- Funções Auxiliares de Input ---

def pause():
    """Pausa a execução e aguarda o usuário pressionar Enter."""
    input("\nPressione Enter para continuar...")

def input_str(label: str, optional: bool = False) -> str | None:
    """Solicita uma string. Se for opcional, permite Enter para None."""
    val = input(label)
    if not val and optional:
        return None
    while not val and not optional:
        print("Este campo é obrigatório.")
        val = input(label)
    return val

def input_int(label: str, optional: bool = False, min_val: int = None, max_val: int = None) -> int | None:
    """Solicita um inteiro com validação."""
    while True:
        try:
            val_str = input(label)
            if not val_str and optional:
                return None
            val_int = int(val_str)
            
            if min_val is not None and val_int < min_val:
                print(f"Valor deve ser no mínimo {min_val}.")
                continue
            if max_val is not None and val_int > max_val:
                print(f"Valor deve ser no máximo {max_val}.")
                continue
                
            return val_int
        except ValueError:
            print("Entrada inválida. Por favor, digite um número inteiro.")

def input_decimal(label: str, optional: bool = False) -> Decimal | None:
    """Solicita um decimal (para preços)."""
    while True:
        try:
            val_str = input(label)
            if not val_str and optional:
                return None
            val_dec = Decimal(val_str.replace(',', '.')) # Aceita 10,50
            if val_dec < 0:
                print("Valor não pode ser negativo.")
                continue
            return val_dec
        except Exception:
            print("Entrada inválida. Ex: 19.99 ou 20,50")

def input_date(label: str, optional: bool = False) -> date | None:
    """Solicita uma data (AAAA-MM-DD)."""
    while True:
        try:
            val_str = input(label)
            if not val_str and optional:
                return None
            return date.fromisoformat(val_str)
        except ValueError:
            print("Formato inválido. Use AAAA-MM-DD (ex: 2025-10-29)")

# --- Funções de UI: GERENCIAR LOCAIS (Exemplo Completo) ---

def ui_listar_locais():
    print("\n--- Lista de Locais ---")
    try:
        locais = crud_local.read_locais()
        if not locais:
            print("Nenhum local cadastrado.")
            return
        
        # Formata a saída
        print(f"{'ID':<5} | {'Nome':<30} | {'Capacidade':<10} | Endereço")
        print("-" * 60)
        for local in locais:
            # (id_local, nome, endereco, capacidade)
            print(f"{local[0]:<5} | {local[1]:<30} | {local[3]:<10} | {local[2]}")
            
    except Exception as e:
        print(f"Erro ao listar locais: {e}")
    finally:
        pause()

def ui_criar_local():
    print("\n--- Cadastrar Novo Local ---")
    try:
        nome = input_str("Nome: ")
        capacidade = input_int("Capacidade: ")
        endereco = input_str("Endereço (opcional): ", optional=True)
        
        novo_id = crud_local.create_local(nome, capacidade, endereco)
        print(f"\nSucesso! Local '{nome}' criado com ID: {novo_id}.")
        
    except ValueError as e: # Erro de validação (ex: capacidade <= 0)
        print(f"Erro de validação: {e}")
    except Exception as e: # Erros de BD (ex: conexão, constraint)
        print(f"Erro ao criar local: {e}")
    finally:
        pause()

def ui_atualizar_local():
    print("\n--- Atualizar Local ---")
    # Mostra a lista para o usuário saber qual ID atualizar
    print("Locais atuais:")
    try:
        locais = crud_local.read_locais()
        if not locais:
            print("Nenhum local para atualizar.")
            pause()
            return
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for local in locais:
            print(f"{local[0]:<5} | {local[1]}")
        print("-" * 30)

        local_id = input_int("\nDigite o ID do local que deseja atualizar: ")
        
        print("\nDigite os novos valores (deixe em branco para não alterar):")
        
        # O 'None' é tratado corretamente pelas nossas funções CRUD
        novo_nome = input_str("Novo nome (opcional): ", optional=True)
        novo_endereco = input_str("Novo endereço (opcional): ", optional=True)
        nova_capacidade = input_int("Nova capacidade (opcional): ", optional=True)

        if novo_nome is None and novo_endereco is None and nova_capacidade is None:
            print("Nenhuma alteração fornecida.")
            pause()
            return

        linhas_afetadas = crud_local.update_local(local_id, novo_nome, novo_endereco, nova_capacidade)
        
        if linhas_afetadas > 0:
            print("\nSucesso! Local atualizado.")
        else:
            print("\nNenhum local encontrado com esse ID.")
            
    except ValueError as e:
        print(f"Erro de validação: {e}")
    except Exception as e:
        print(f"Erro ao atualizar local: {e}")
    finally:
        pause()

def ui_deletar_local():
    print("\n--- Deletar Local ---")
    # Mostra a lista para o usuário saber qual ID deletar
    print("Locais atuais:")
    try:
        locais = crud_local.read_locais()
        if not locais:
            print("Nenhum local para deletar.")
            pause()
            return
            
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for local in locais:
            print(f"{local[0]:<5} | {local[1]}")
        print("-" * 30)

        local_id = input_int("\nDigite o ID do local que deseja deletar: ")
        
        # Confirmação
        confirm = input_str(f"Tem certeza que deseja deletar o local ID {local_id}? (s/n): ").lower()
        
        if confirm == 's':
            linhas_afetadas = crud_local.delete_local(local_id)
            if linhas_afetadas > 0:
                print("\nSucesso! Local deletado.")
            else:
                print("\nNenhum local encontrado com esse ID.")
        else:
            print("Operação cancelada.")

    except Exception as e:
        # Captura o erro de ON DELETE RESTRICT
        if "violates foreign key constraint" in str(e) and "Evento" in str(e):
            print("\nErro: Não é possível deletar este local, pois ele está sendo usado por um ou mais Eventos.")
        else:
            print(f"Erro ao deletar local: {e}")
    finally:
        pause()


# --- Sub-Menus (Looping) ---

def menu_locais():
    """Sub-menu para Gerenciar Locais."""
    while True:
        print("\n--- 📍 Gerenciar Locais ---")
        print("1. Listar Locais")
        print("2. Cadastrar Novo Local")
        print("3. Atualizar Local")
        print("4. Deletar Local")
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=4)

        if opcao == 1:
            ui_listar_locais()
        elif opcao == 2:
            ui_criar_local()
        elif opcao == 3:
            ui_atualizar_local()
        elif opcao == 4:
            ui_deletar_local()
        elif opcao == 0:
            break # Volta para o menu principal

# --- Funções de UI: GERENCIAR ARTISTAS ---

def ui_listar_artistas():
    print("\n--- Lista de Artistas ---")
    try:
        artistas = crud_artista.read_artistas()
        if not artistas:
            print("Nenhum artista cadastrado.")
            return
        
        # Formata a saída
        print(f"{'ID':<5} | {'Nome':<30} | Gênero")
        print("-" * 50)
        for artista in artistas:
            # (id_artista, nome, genero)
            print(f"{artista[0]:<5} | {artista[1]:<30} | {artista[2]}")
            
    except Exception as e:
        print(f"Erro ao listar artistas: {e}")
    finally:
        pause()

def ui_criar_artista():
    print("\n--- Cadastrar Novo Artista ---")
    try:
        nome = input_str("Nome: ")
        genero = input_str("Gênero (opcional): ", optional=True)
        
        novo_id = crud_artista.create_artista(nome, genero)
        print(f"\nSucesso! Artista '{nome}' criado com ID: {novo_id}.")
        
    except Exception as e: # Erros de BD (ex: conexão, constraint)
        print(f"Erro ao criar artista: {e}")
    finally:
        pause()

def ui_atualizar_artista():
    print("\n--- Atualizar Artista ---")
    print("Artistas atuais:")
    try:
        artistas = crud_artista.read_artistas()
        if not artistas:
            print("Nenhum artista para atualizar.")
            pause()
            return
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for artista in artistas:
            print(f"{artista[0]:<5} | {artista[1]}")
        print("-" * 30)

        artista_id = input_int("\nDigite o ID do artista que deseja atualizar: ")
        
        print("\nDigite os novos valores (deixe em branco para não alterar):")
        
        novo_nome = input_str("Novo nome (opcional): ", optional=True)
        novo_genero = input_str("Novo gênero (opcional): ", optional=True)

        if novo_nome is None and novo_genero is None:
            print("Nenhuma alteração fornecida.")
            pause()
            return

        linhas_afetadas = crud_artista.update_artista(artista_id, novo_nome, novo_genero)
        
        if linhas_afetadas > 0:
            print("\nSucesso! Artista atualizado.")
        else:
            print("\nNenhum artista encontrado com esse ID.")
            
    except Exception as e:
        print(f"Erro ao atualizar artista: {e}")
    finally:
        pause()

def ui_deletar_artista():
    print("\n--- Deletar Artista ---")
    print("Artistas atuais:")
    try:
        artistas = crud_artista.read_artistas()
        if not artistas:
            print("Nenhum artista para deletar.")
            pause()
            return
            
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for artista in artistas:
            print(f"{artista[0]:<5} | {artista[1]}")
        print("-" * 30)

        artista_id = input_int("\nDigite o ID do artista que deseja deletar: ")
        
        # Confirmação
        confirm = input_str(f"Tem certeza que deseja deletar o artista ID {artista_id}? (s/n): ").lower()
        
        if confirm == 's':
            linhas_afetadas = crud_artista.delete_artista(artista_id)
            if linhas_afetadas > 0:
                print("\nSucesso! Artista deletado.")
                print("Aviso: Todas as associações (N:N) deste artista com eventos foram removidas (ON DELETE CASCADE).")
            else:
                print("\nNenhum artista encontrado com esse ID.")
        else:
            print("Operação cancelada.")

    except Exception as e:
            print(f"Erro ao deletar artista: {e}")
    finally:
        pause()


# --- Sub-Menus (Looping) ---

def menu_artistas():
    """Sub-menu para Gerenciar Artistas."""
    while True:
        print("\n--- 🎤 Gerenciar Artistas ---")
        print("1. Listar Artistas")
        print("2. Cadastrar Novo Artista")
        print("3. Atualizar Artista")
        print("4. Deletar Artista")
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=4)

        if opcao == 1:
            ui_listar_artistas()
        elif opcao == 2:
            ui_criar_artista()
        elif opcao == 3:
            ui_atualizar_artista()
        elif opcao == 4:
            ui_deletar_artista()
        elif opcao == 0:
            break # Volta para o menu principal

# --- Funções Auxiliares (Helpers) para Eventos ---

def _selecionar_evento() -> int | None:
    """
    Função auxiliar para listar e selecionar um Evento.
    Retorna o ID do evento selecionado, ou None se cancelar.
    """
    print("\n--- Selecione um Evento ---")
    try:
        eventos = crud_evento.read_todos_eventos()
        if not eventos:
            print("Nenhum evento cadastrado.")
            return None
        
        print(f"{'ID':<5} | {'Data':<12} | Nome")
        print("-" * 50)
        for ev in eventos:
            # (id_evento, nome, data, horario, id_local)
            print(f"{ev[0]:<5} | {str(ev[2]):<12} | {ev[1]}")
        print("-" * 50)
        
        evento_id = input_int("Digite o ID do evento (ou 0 para cancelar): ", optional=True)
        if evento_id == 0 or evento_id is None:
            return None
        
        if evento_id not in [ev[0] for ev in eventos]:
            print("ID de evento inválido.")
            return None
            
        return evento_id
        
    except Exception as e:
        print(f"Erro ao selecionar evento: {e}")
        return None

def _selecionar_artista() -> int | None:
    """
    Função auxiliar para listar e selecionar um Artista.
    Retorna o ID do artista selecionado, ou None se cancelar.
    """
    print("\n--- Selecione um Artista ---")
    try:
        artistas = crud_artista.read_artistas()
        if not artistas:
            print("Nenhum artista cadastrado.")
            return None
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for artista in artistas:
            print(f"{artista[0]:<5} | {artista[1]}")
        print("-" * 30)
        
        artista_id = input_int("Digite o ID do artista (ou 0 para cancelar): ", optional=True)
        if artista_id == 0 or artista_id is None:
            return None

        if artista_id not in [a[0] for a in artistas]:
            print("ID de artista inválido.")
            return None
            
        return artista_id
        
    except Exception as e:
        print(f"Erro ao selecionar artista: {e}")
        return None


# --- Funções de UI: GERENCIAR EVENTOS (CRUD Básico) ---

def ui_listar_eventos():
    print("\n--- Lista de Eventos (Ordenados por Data) ---")
    try:
        eventos = crud_evento.read_todos_eventos()
        if not eventos:
            print("Nenhum evento cadastrado.")
            return
        
        print(f"{'ID':<5} | {'Data':<12} | {'Horário':<10} | {'ID Local':<8} | Nome")
        print("-" * 70)
        for ev in eventos:
            # (id_evento, nome, data, horario, id_local)
            horario_str = str(ev[3]) if ev[3] else "N/D"
            print(f"{ev[0]:<5} | {str(ev[2]):<12} | {horario_str:<10} | {ev[4]:<8} | {ev[1]}")
            
    except Exception as e:
        print(f"Erro ao listar eventos: {e}")
    finally:
        pause()

def ui_criar_evento():
    print("\n--- Cadastrar Novo Evento ---")
    # Um evento PRECISA de um local
    local_id = _selecionar_local() # Reutiliza a função do menu de setores
    if local_id is None:
        print("Criação de evento cancelada (um local é obrigatório).")
        pause()
        return

    try:
        print(f"\nCriando evento para o Local ID: {local_id}")
        nome = input_str("Nome do evento: ")
        data_ev = input_date("Data (AAAA-MM-DD): ")
        
        # Lógica para horário opcional
        horario_str = input_str("Horário (HH:MM) (opcional): ", optional=True)
        horario_ev = None
        if horario_str:
            horario_ev = time.fromisoformat(horario_str)
            
        descricao = input_str("Descrição (opcional): ", optional=True)
        
        novo_id = crud_evento.create_evento(nome, data_ev, local_id, horario_ev, descricao)
        print(f"\nSucesso! Evento '{nome}' criado com ID: {novo_id}.")
        
    except ValueError:
        print("Erro: Formato de horário inválido. Use HH:MM.")
    except Exception as e:
        print(f"Erro ao criar evento: {e}")
    finally:
        pause()

def ui_deletar_evento():
    print("\n--- Deletar Evento ---")
    evento_id = _selecionar_evento()
    if evento_id is None:
        print("Operação cancelada.")
        pause()
        return

    try:
        confirm = input_str(f"Tem certeza que deseja deletar o Evento ID {evento_id}? (s/n)\n"
                          "AVISO: Todos os INGRESSOS e associações de ARTISTAS deste evento\n"
                          "serão deletados permanentemente (CASCADE).\n"
                          "Digite 's' para confirmar: ").lower()
        
        if confirm == 's':
            linhas_afetadas = crud_evento.delete_evento(evento_id)
            if linhas_afetadas > 0:
                print("\nSucesso! Evento deletado.")
            else:
                print("\nNenhum evento encontrado com esse ID.")
        else:
            print("Operação cancelada.")
            
    except Exception as e:
        print(f"Erro ao deletar evento: {e}")
    finally:
        pause()


# --- Funções de UI: GERENCIAR ARTISTAS DE UM EVENTO (N:N) ---

def ui_listar_artistas_do_evento(evento_id: int):
    print(f"\n--- Artistas do Evento ID: {evento_id} ---")
    try:
        artistas = crud_evento_artista.read_artistas_por_evento(evento_id)
        if not artistas:
            print("Nenhum artista associado a este evento.")
            return
        
        print(f"{'ID Artista':<10} | Nome")
        print("-" * 30)
        for artista in artistas:
            # (a.id_artista, a.nome, a.genero)
            print(f"{artista[0]:<10} | {artista[1]}")
            
    except Exception as e:
        print(f"Erro ao listar artistas do evento: {e}")
    finally:
        pause()

def ui_associar_artista_evento(evento_id: int):
    print(f"\n--- Associar Artista ao Evento ID: {evento_id} ---")
    artista_id = _selecionar_artista()
    if artista_id is None:
        print("Operação cancelada.")
        pause()
        return

    try:
        linhas_afetadas = crud_evento_artista.associar_artista_evento(evento_id, artista_id)
        if linhas_afetadas > 0:
            print("\nSucesso! Artista associado ao evento.")
    except Exception as e:
        if "violates primary key constraint" in str(e):
            print("\nErro: Este artista já está associado a este evento.")
        else:
            print(f"Erro ao associar artista: {e}")
    finally:
        pause()

def menu_gerenciar_artistas_evento():
    print("\n--- Gerenciar Artistas de um Evento ---")
    evento_id = _selecionar_evento()
    if evento_id is None:
        print("Operação cancelada.")
        pause()
        return
        
    while True:
        print(f"\n--- 🎤 Gerenciando Artistas [Evento ID: {evento_id}] ---")
        print("1. Listar Artistas do Evento")
        print("2. Adicionar Artista ao Evento")
        # TODO: Implementar "Remover Artista"
        print("0. Voltar")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=2)
        
        if opcao == 1:
            ui_listar_artistas_do_evento(evento_id)
        elif opcao == 2:
            ui_associar_artista_evento(evento_id)
        elif opcao == 0:
            break


# --- Funções de UI: GERENCIAR INGRESSOS DE UM EVENTO (Especialização) ---

def ui_listar_ingressos_do_evento(evento_id: int):
    print(f"\n--- Ingressos do Evento ID: {evento_id} ---")
    try:
        ingressos = crud_ingresso.read_ingressos_por_evento(evento_id)
        if not ingressos:
            print("Nenhum ingresso cadastrado para este evento.")
            return

        print(f"{'ID':<5} | {'Preço':<10} | {'Tipo':<10} | Benefícios/Assento")
        print("-" * 70)
        for ing in ingressos:
            # (i.id_ingresso, i.preco, i.id_assento, vip.beneficios, padrao.id_ingresso)
            tipo = "VIP" if ing[3] is not None else "Padrão"
            preco_str = f"R$ {ing[1]:.2f}"
            
            detalhe = f"Benefícios: {ing[3]}" if tipo == "VIP" else f"Assento ID: {ing[2]}"
            if ing[2] is None and tipo == "Padrão":
                detalhe = "(Pista/Livre)"

            print(f"{ing[0]:<5} | {preco_str:<10} | {tipo:<10} | {detalhe}")

    except Exception as e:
        print(f"Erro ao listar ingressos: {e}")
    finally:
        pause()

def ui_criar_ingresso_evento(evento_id: int):
    print(f"\n--- Criar Ingresso para o Evento ID: {evento_id} ---")
    try:
        preco = input_decimal("Preço (ex: 49.99): ")
        
        # TODO: Implementar seleção de assento (complexo, omitido por enquanto)
        print("Aviso: Seleção de assento não implementada. Criando como Pista (Assento=NULL).")
        id_assento = None 
        
        tipo = input_str("Tipo de ingresso (1: VIP, 2: Padrão): ")
        
        if tipo == '1':
            beneficios = input_str("Benefícios VIP (opcional): ", optional=True)
            novo_id = crud_ingresso.create_ingresso_vip(evento_id, preco, id_assento, beneficios)
            print(f"\nSucesso! Ingresso VIP criado com ID: {novo_id}.")
            
        elif tipo == '2':
            novo_id = crud_ingresso.create_ingresso_padrao(evento_id, preco, id_assento)
            print(f"\nSucesso! Ingresso Padrão criado com ID: {novo_id}.")
        else:
            print("Tipo inválido. Operação cancelada.")
            
    except Exception as e:
        if "violates unique constraint" in str(e) and "uq_evento_assento" in str(e):
            print("\nErro: Este assento já foi vendido para este evento.")
        else:
            print(f"Erro ao criar ingresso: {e}")
    finally:
        pause()

def menu_gerenciar_ingressos_evento():
    print("\n--- Gerenciar Ingressos de um Evento ---")
    evento_id = _selecionar_evento()
    if evento_id is None:
        print("Operação cancelada.")
        pause()
        return

    while True:
        print(f"\n--- 🎫 Gerenciando Ingressos [Evento ID: {evento_id}] ---")
        print("1. Listar Ingressos do Evento")
        print("2. Criar Novo Ingresso para o Evento")
        # TODO: Implementar "Deletar Ingresso"
        print("0. Voltar")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=2)
        
        if opcao == 1:
            ui_listar_ingressos_do_evento(evento_id)
        elif opcao == 2:
            ui_criar_ingresso_evento(evento_id)
        elif opcao == 0:
            break


# --- Sub-Menu (Looping) ---

def menu_eventos():
    """Sub-menu para Gerenciar Eventos."""
    while True:
        print("\n--- 🗓️ Gerenciar Eventos e Ingressos ---")
        print("\n-- Gestão de Eventos --")
        print("1. Listar Todos os Eventos")
        print("2. Cadastrar Novo Evento")
        print("3. Deletar Evento")
        # TODO: Implementar "Atualizar Evento"
        print("\n-- Gestão de Componentes do Evento --")
        print("4. Gerenciar Artistas de um Evento (N:N)")
        print("5. Gerenciar Ingressos de um Evento (Especialização)")
        print("\n----------------------------------")
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=5)

        if opcao == 1:
            ui_listar_eventos()
        elif opcao == 2:
            ui_criar_evento()
        elif opcao == 3:
            ui_deletar_evento()
        elif opcao == 4:
            menu_gerenciar_artistas_evento()
        elif opcao == 5:
            menu_gerenciar_ingressos_evento()
        elif opcao == 0:
            break

# --- Funções Auxiliares (Helpers) para Setores/Assentos ---

def _selecionar_local() -> int | None:
    """
    Função auxiliar para listar e selecionar um Local.
    Retorna o ID do local selecionado, ou None se cancelar.
    """
    print("\n--- Selecione um Local ---")
    try:
        locais = crud_local.read_locais()
        if not locais:
            print("Nenhum local cadastrado. Cadastre um local primeiro.")
            return None
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for local in locais:
            # (id_local, nome, ...)
            print(f"{local[0]:<5} | {local[1]}")
        print("-" * 30)
        
        local_id = input_int("Digite o ID do local (ou 0 para cancelar): ", optional=True)
        if local_id == 0 or local_id is None:
            return None
        
        # Validação simples para ver se o ID existe (embora o BD vá checar)
        if local_id not in [loc[0] for loc in locais]:
            print("ID de local inválido.")
            return None
            
        return local_id
        
    except Exception as e:
        print(f"Erro ao selecionar local: {e}")
        return None

def _selecionar_setor(local_id: int) -> int | None:
    """
    Função auxiliar para listar e selecionar um Setor de um Local específico.
    Retorna o ID do setor selecionado, ou None se cancelar.
    """
    print(f"\n--- Selecione um Setor (do Local ID: {local_id}) ---")
    try:
        setores = crud_setor.read_setores_por_local(local_id)
        if not setores:
            print("Nenhum setor cadastrado para este local.")
            return None
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for setor in setores:
            # (id_setor, nome)
            print(f"{setor[0]:<5} | {setor[1]}")
        print("-" * 30)
        
        setor_id = input_int("Digite o ID do setor (ou 0 para cancelar): ", optional=True)
        if setor_id == 0 or setor_id is None:
            return None
        
        if setor_id not in [s[0] for s in setores]:
            print("ID de setor inválido.")
            return None
            
        return setor_id
        
    except Exception as e:
        print(f"Erro ao selecionar setor: {e}")
        return None

# --- Funções de UI: GERENCIAR SETORES ---

def ui_listar_setores():
    print("\n--- Listar Setores por Local ---")
    local_id = _selecionar_local()
    if local_id is None:
        print("Operação cancelada.")
        pause()
        return

    try:
        print(f"\n--- Setores do Local ID: {local_id} ---")
        setores = crud_setor.read_setores_por_local(local_id)
        if not setores:
            print("Nenhum setor encontrado para este local.")
        else:
            print(f"{'ID':<5} | Nome")
            print("-" * 30)
            for setor in setores:
                print(f"{setor[0]:<5} | {setor[1]}")
    except Exception as e:
        print(f"Erro ao listar setores: {e}")
    finally:
        pause()

def ui_criar_setor():
    print("\n--- Cadastrar Novo Setor ---")
    local_id = _selecionar_local()
    if local_id is None:
        print("Operação cancelada. (Um setor precisa de um local)")
        pause()
        return
        
    try:
        nome_setor = input_str(f"Nome do novo setor para o Local ID {local_id}: ")
        
        novo_id = crud_setor.create_setor(nome_setor, local_id)
        print(f"\nSucesso! Setor '{nome_setor}' criado com ID: {novo_id}.")
        
    except Exception as e:
        if "violates unique constraint" in str(e) and "setor_id_local_nome_key" in str(e):
            print("\nErro: Já existe um setor com este nome neste local.")
        else:
            print(f"Erro ao criar setor: {e}")
    finally:
        pause()

def ui_deletar_setor():
    print("\n--- Deletar Setor ---")
    local_id = _selecionar_local()
    if local_id is None:
        print("Operação cancelada.")
        pause()
        return
        
    setor_id = _selecionar_setor(local_id)
    if setor_id is None:
        print("Operação cancelada.")
        pause()
        return

    try:
        confirm = input_str(f"Tem certeza que deseja deletar o Setor ID {setor_id}? (s/n)\n"
                          "AVISO: Todos os ASSENTOS deste setor serão deletados (CASCADE).\n"
                          "Digite 's' para confirmar: ").lower()
        
        if confirm == 's':
            linhas_afetadas = crud_setor.delete_setor(setor_id)
            if linhas_afetadas > 0:
                print("\nSucesso! Setor deletado.")
            else:
                print("\nNenhum setor encontrado com esse ID.")
        else:
            print("Operação cancelada.")
            
    except Exception as e:
        print(f"Erro ao deletar setor: {e}")
    finally:
        pause()


# --- Funções de UI: GERENCIAR ASSENTOS ---

def ui_listar_assentos():
    print("\n--- Listar Assentos por Setor ---")
    local_id = _selecionar_local()
    if local_id is None:
        print("Operação cancelada.")
        pause()
        return
        
    setor_id = _selecionar_setor(local_id)
    if setor_id is None:
        print("Operação cancelada.")
        pause()
        return

    try:
        print(f"\n--- Assentos do Setor ID: {setor_id} ---")
        assentos = crud_assento.read_assentos_por_setor(setor_id)
        if not assentos:
            print("Nenhum assento encontrado para este setor.")
        else:
            print(f"{'ID':<5} | {'Fileira':<10} | Número")
            print("-" * 30)
            for assento in assentos:
                # (id_assento, fileira, numero)
                print(f"{assento[0]:<5} | {assento[1]:<10} | {assento[2]}")
    except Exception as e:
        print(f"Erro ao listar assentos: {e}")
    finally:
        pause()

def ui_criar_assento():
    print("\n--- Cadastrar Novo Assento ---")
    local_id = _selecionar_local()
    if local_id is None:
        print("Operação cancelada.")
        pause()
        return
        
    setor_id = _selecionar_setor(local_id)
    if setor_id is None:
        print("Operação cancelada. (Um assento precisa de um setor)")
        pause()
        return

    try:
        print(f"\nCadastrando assento para o Setor ID: {setor_id}")
        fileira = input_str("Fileira (ex: A, B, 10): ")
        numero = input_str("Número (ex: 1, 2, C12): ")
        
        novo_id = crud_assento.create_assento(setor_id, fileira, numero)
        print(f"\nSucesso! Assento '{fileira}-{numero}' criado com ID: {novo_id}.")
        
    except Exception as e:
        if "violates unique constraint" in str(e) and "assento_id_setor_fileira_numero_key" in str(e):
            print("\nErro: Este assento (Fileira/Número) já existe neste setor.")
        else:
            print(f"Erro ao criar assento: {e}")
    finally:
        pause()


# --- Sub-Menu (Looping) ---

def menu_setores_e_assentos():
    """Sub-menu para Gerenciar Setores e Assentos."""
    while True:
        print("\n--- 🏛️ Gerenciar Setores e Assentos ---")
        print("\n-- Gerenciamento de Setores --")
        print("1. Listar Setores (de um Local)")
        print("2. Cadastrar Novo Setor (em um Local)")
        print("3. Deletar Setor")
        print("\n-- Gerenciamento de Assentos --")
        print("4. Listar Assentos (de um Setor)")
        print("5. Cadastrar Novo Assento (em um Setor)")
        print("\n----------------------------------")
        print("0. Voltar ao Menu Principal")
        
        # Nota: Omiti Update para simplificar este menu,
        # mas pode ser adicionado seguindo o padrão
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=5)

        if opcao == 1:
            ui_listar_setores()
        elif opcao == 2:
            ui_criar_setor()
        elif opcao == 3:
            ui_deletar_setor()
        elif opcao == 4:
            ui_listar_assentos()
        elif opcao == 5:
            ui_criar_assento()
        elif opcao == 0:
            break


# --- Funções de UI: GERENCIAR COMPRADORES ---

def ui_listar_compradores():
    print("\n--- Lista de Compradores ---")
    try:
        # ANTES: compradores = crud_venda.read_compradores()
        compradores = crud_comprador.read_compradores() # DEPOIS: Corrigido
        if not compradores:
            print("Nenhum comprador cadastrado.")
            return
        
        # Formata a saída
        print(f"{'ID':<5} | {'Nome':<30} | Email")
        print("-" * 60)
        for comprador in compradores:
            # (id_comprador, nome, email)
            print(f"{comprador[0]:<5} | {comprador[1]:<30} | {comprador[2]}")
            
    except Exception as e:
        print(f"Erro ao listar compradores: {e}")
    finally:
        pause()

def ui_criar_comprador():
    print("\n--- Cadastrar Novo Comprador ---")
    try:
        nome = input_str("Nome: ")
        email = input_str("Email: ")
        
        # ANTES: novo_id = crud_venda.create_comprador(nome, email)
        novo_id = crud_comprador.create_comprador(nome, email) # DEPOIS: Corrigido
        print(f"\nSucesso! Comprador '{nome}' criado com ID: {novo_id}.")
        
    except Exception as e:
        # Captura o erro de email UNIQUE
        if "violates unique constraint" in str(e) and "comprador_email_key" in str(e):
             print(f"\nErro: O email '{email}' já está cadastrado.")
        else:
            print(f"Erro ao criar comprador: {e}")
    finally:
        pause()

def ui_atualizar_comprador():
    print("\n--- Atualizar Comprador ---")
    print("Compradores atuais:")
    try:
        compradores = crud_comprador.read_compradores() 
        if not compradores:
            print("Nenhum comprador para atualizar.")
            pause()
            return
        
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for comprador in compradores:
            print(f"{comprador[0]:<5} | {comprador[1]}")
        print("-" * 30)

        comprador_id = input_int("\nDigite o ID do comprador que deseja atualizar: ")
        
        print("\nDigite os novos valores (deixe em branco para não alterar):")
        
        novo_nome = input_str("Novo nome (opcional): ", optional=True)
        novo_email = input_str("Novo email (opcional): ", optional=True)

        if novo_nome is None and novo_email is None:
            print("Nenhuma alteração fornecida.")
            pause()
            return

        linhas_afetadas = crud_comprador.update_comprador(comprador_id, novo_nome, novo_email) 
        
        if linhas_afetadas > 0:
            print("\nSucesso! Comprador atualizado.")
        else:
            print("\nNenhum comprador encontrado com esse ID.")
            
    except Exception as e:
        # Captura o erro de email UNIQUE
        if "violates unique constraint" in str(e) and "comprador_email_key" in str(e):
             print(f"\nErro: O novo email '{novo_email}' já está cadastrado por outro usuário.")
        else:
            print(f"Erro ao atualizar comprador: {e}")
    finally:
        pause()

def ui_deletar_comprador():
    print("\n--- Deletar Comprador ---")
    print("Compradores atuais:")
    try:  
        compradores = crud_comprador.read_compradores() 
        if not compradores:
            print("Nenhum comprador para deletar.")
            pause()
            return
            
        print(f"{'ID':<5} | Nome")
        print("-" * 30)
        for comprador in compradores:
            print(f"{comprador[0]:<5} | {comprador[1]}")
        print("-" * 30)

        comprador_id = input_int("\nDigite o ID do comprador que deseja deletar: ")
        
        confirm = input_str(f"Tem certeza que deseja deletar o comprador ID {comprador_id}? (s/n): ").lower()
        
        if confirm == 's':
            linhas_afetadas = crud_comprador.delete_comprador(comprador_id) 
            if linhas_afetadas > 0:
                print("\nSucesso! Comprador deletado.")
            else:
                print("\nNenhum comprador encontrado com esse ID.")
        else:
            print("Operação cancelada.")

    except Exception as e:
        # Captura o erro de ON DELETE RESTRICT
        if "violates foreign key constraint" in str(e) and "Venda" in str(e):
            print("\nErro: Não é possível deletar este comprador, pois ele possui Vendas registradas em seu nome.")
        else:
            print(f"Erro ao deletar comprador: {e}")
    finally:
        pause()


# --- Sub-Menus (Looping) ---

def menu_compradores():
    """Sub-menu para Gerenciar Compradores."""
    while True:
        print("\n--- 👤 Gerenciar Compradores ---")
        print("1. Listar Compradores")
        print("2. Cadastrar Novo Comprador")
        print("3. Atualizar Comprador")
        print("4. Deletar Comprador")
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=4)

        if opcao == 1:
            ui_listar_compradores()
        elif opcao == 2:
            ui_criar_comprador()
        elif opcao == 3:
            ui_atualizar_comprador()
        elif opcao == 4:
            ui_deletar_comprador()
        elif opcao == 0:
            break

# --- Funções Auxiliares (Helpers) para Vendas ---

def _selecionar_comprador() -> int | None:
    """
    Função auxiliar para listar e selecionar um Comprador.
    Retorna o ID do comprador selecionado, ou None se cancelar.
    """
    print("\n--- Selecione um Comprador ---")
    try:
        compradores = crud_comprador.read_compradores()
        if not compradores:
            print("Nenhum comprador cadastrado. Cadastre um comprador primeiro.")
            return None
        
        print(f"{'ID':<5} | {'Nome':<30} | Email")
        print("-" * 60)
        for comprador in compradores:
            # (id_comprador, nome, email)
            print(f"{comprador[0]:<5} | {comprador[1]:<30} | {comprador[2]}")
        print("-" * 60)
        
        comprador_id = input_int("Digite o ID do comprador (ou 0 para cancelar): ", optional=True)
        if comprador_id == 0 or comprador_id is None:
            return None
        
        if comprador_id not in [c[0] for c in compradores]:
            print("ID de comprador inválido.")
            return None
            
        return comprador_id
        
    except Exception as e:
        print(f"Erro ao selecionar comprador: {e}")
        return None

def _selecionar_ingresso(evento_id: int) -> int | None:
    """
    Função auxiliar para listar e selecionar um Ingresso de um Evento específico.
    Retorna o ID do ingresso selecionado, ou None se cancelar.
    """
    print(f"\n--- Selecione um Ingresso (Evento ID: {evento_id}) ---")
    try:
        ingressos = crud_ingresso.read_ingressos_por_evento(evento_id)
        if not ingressos:
            print("Nenhum ingresso cadastrado para este evento.")
            return None

        print(f"{'ID':<5} | {'Preço':<10} | {'Tipo':<10} | Detalhes")
        print("-" * 70)
        for ing in ingressos:
            # (i.id_ingresso, i.preco, i.id_assento, vip.beneficios, padrao.id_ingresso)
            tipo = "VIP" if ing[3] is not None else "Padrão"
            preco_str = f"R$ {ing[1]:.2f}"
            
            detalhe = f"Benefícios: {ing[3]}" if tipo == "VIP" else f"Assento ID: {ing[2]}"
            if ing[2] is None and tipo == "Padrão":
                detalhe = "(Pista/Livre)"

            print(f"{ing[0]:<5} | {preco_str:<10} | {tipo:<10} | {detalhe}")
        print("-" * 70)
        
        ingresso_id = input_int("Digite o ID do ingresso (ou 0 para cancelar): ", optional=True)
        if ingresso_id == 0 or ingresso_id is None:
            return None
        
        if ingresso_id not in [i[0] for i in ingressos]:
            print("ID de ingresso inválido.")
            return None
            
        return ingresso_id
        
    except Exception as e:
        print(f"Erro ao selecionar ingresso: {e}")
        return None

# --- Funções de UI: REALIZAR VENDA ---

def ui_realizar_venda():
    print("\n--- 💵 Registrar Nova Venda ---")
    
    try:
        # Passo 1: Selecionar Comprador
        comprador_id = _selecionar_comprador()
        if comprador_id is None:
            print("Venda cancelada.")
            pause()
            return
            
        # Passo 2: Selecionar Evento
        evento_id = _selecionar_evento() # Reutiliza helper do menu de eventos
        if evento_id is None:
            print("Venda cancelada.")
            pause()
            return
            
        # Passo 3: Selecionar Ingresso (daquele evento)
        ingresso_id = _selecionar_ingresso(evento_id)
        if ingresso_id is None:
            print("Venda cancelada.")
            pause()
            return
            
        # Passo 4: Informar Quantidade
        quantidade = input_int("Digite a quantidade: ", min_val=1)
        if quantidade is None:
            print("Venda cancelada.")
            pause()
            return
            
        # Passo 5: Obter data e criar a venda
        data_venda = date.today()
        
        novo_id = crud_venda.create_venda(data_venda, quantidade, ingresso_id, comprador_id)
        
        print(f"\nSucesso! Venda registrada com ID: {novo_id} (Data: {data_venda}).")
        
    except ValueError as e:
        print(f"Erro de validação: {e}")
    except Exception as e:
        print(f"Erro ao registrar venda: {e}")
    finally:
        pause()


# --- Sub-Menus (Looping) ---

def menu_vendas():
    """Sub-menu para Realizar Venda."""
    while True:
        print("\n--- 💸 Realizar Venda ---")
        print("1. Registrar Nova Venda")
        # TODO: Implementar "Cancelar Venda" (ui_deletar_venda)
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=1)

        if opcao == 1:
            ui_realizar_venda()
        elif opcao == 0:
            break

# --- Funções de UI: RELATÓRIOS (FASE 3) ---

def ui_relatorio_vendas_por_comprador():
    print("\n--- Relatório: Histórico de Vendas por Comprador (Consulta Fase 3) ---")
    try:
        comprador_id = _selecionar_comprador() # Reusa helper do menu de vendas
        if comprador_id is None:
            print("Operação cancelada.")
            pause()
            return
        
        # Esta função (de crud_venda.py) já usa 3 tabelas:
        # Venda JOIN Ingresso JOIN Evento
        vendas = crud_venda.read_vendas_por_comprador(comprador_id)
        
        if not vendas:
            print("Nenhuma venda encontrada para este comprador.")
            pause()
            return

        print(f"\n--- Vendas do Comprador ID: {comprador_id} ---")
        print(f"{'ID Venda':<10} | {'Data':<12} | {'Evento':<30} | {'Qtd':<4} | Total")
        print("-" * 75)
        
        total_geral = Decimal(0)
        for v in vendas:
            # (v.id_venda, v.data, e.nome_evento, i.preco, v.quantidade, total)
            total_geral += v[5]
            total_str = f"R$ {v[5]:.2f}"
            print(f"{v[0]:<10} | {str(v[1]):<12} | {v[2]:<30} | {v[4]:<4} | {total_str}")
        
        print("-" * 75)
        print(f"Total gasto pelo comprador: R$ {total_geral:.2f}")

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
    finally:
        pause()


# --- Sub-Menus (Looping) ---

def menu_relatorios():
    """Sub-menu para Relatórios (Fase 3)."""
    while True:
        print("\n--- 📊 Relatórios do Sistema ---")
        print("1. Histórico de Vendas por Comprador (Consulta 3 Tabelas)")
        print("0. Voltar ao Menu Principal")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=1)

        if opcao == 1:
            ui_relatorio_vendas_por_comprador()
        elif opcao == 0:
            break


# --- Menu Principal ---

def main_menu():
    """Menu principal do sistema."""
    while True:
        print("\n--- 🎟️  Sistema de Gestão TikEvents ---")
        print("1. Gerenciar Locais")
        print("2. Gerenciar Artistas")
        print("3. Gerenciar Eventos e Ingressos")
        print("4. Gerenciar Setores e Assentos")
        print("5. Gerenciar Compradores")
        print("6. Realizar Venda")
        print("7. Relatórios")
        print("0. Sair")
        
        opcao = input_int("Escolha uma opção: ", min_val=0, max_val=7)

        if opcao == 1:
            menu_locais()
        elif opcao == 2:
            menu_artistas()
        elif opcao == 3:
            menu_eventos() 
        elif opcao == 4:
            menu_setores_e_assentos()
        elif opcao == 5:
            menu_compradores()
        elif opcao == 6:
            menu_vendas()
        elif opcao == 7:
            menu_relatorios()
        elif opcao == 0:
            print("Saindo do sistema. Até logo!")
            break

# --- Ponto de Entrada do Programa ---

if __name__ == "__main__":
    # 1. Verifica a conexão com o banco de dados antes de tudo
    try:
        conn = db.get_conn()
        conn.close()
        print("Conexão com o banco de dados estabelecida com sucesso.")
    except Exception as e:
        print(f"Erro fatal: Não foi possível conectar ao banco de dados.", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        print("\nVerifique se o PostgreSQL está rodando e se a DSN em 'db.py' está correta.")
        sys.exit(1) # Encerra o programa se não puder conectar

    # 2. Inicia o menu principal
    main_menu()