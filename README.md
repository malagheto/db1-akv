Projeto: TikEvents - Gestão de Eventos (EP Banco de Dados)

A aplicação é um sistema de gerenciamento de eventos (TikEvents) com uma interface de linha de comando (CLI) escrita em Python, conectando-se diretamente a um banco de dados PostgreSQL sem o uso de frameworks, conforme especificado nos requisitos.

📋 Implementações
Esta entrega foca em finalizar a camada de acesso a dados (CRUD) e a interface de usuário básica para todas as entidades, além de implementar uma consulta complexa de 3 tabelas .

1. Manutenção de Todas as Tabelas (CRUD Completo) 

O código foi modularizado em uma camada de acesso a dados (arquivos crud_...py) e uma camada de interface (main.py).

Foram implementadas as rotinas de manutenção (CRUD) para todas as entidades-base:

Local (CRUD)

Artista (CRUD)

Comprador (CRUD)

Foram implementadas as rotinas para entidades com dependências hierárquicas:
Evento (dependente de Local)

Setor (dependente de Local)

Assento (dependente de Setor)

Foi implementado o gerenciamento do relacionamento N:N:

Evento_Artista (com funções de associar e desassociar artista de um evento).

Foi implementado o gerenciamento da Especialização:

Ingresso (superclasse) -> Ingresso_VIP / Ingresso_Padrao (subclasses).

As funções de criação (ex: create_ingresso_vip) utilizam transações para garantir a inserção atômica na superclasse e na subclasse.

Foi implementada a transação de Venda, que conecta Ingresso e Comprador.

2. Consulta com 3 Tabelas 

A consulta obrigatória de pelo menos 3 tabelas foi implementada na função crud_venda.read_vendas_por_comprador().

Esta função utiliza JOIN entre as tabelas Venda, Ingresso e Evento para gerar um histórico de compras detalhado para um usuário.

Esta consulta é apresentada ao usuário no "Menu de Relatórios" (opção 1).

Exemplo de uma consulta com 4 tabelas 

SELECT
  C.nome AS Comprador,
  E.nome AS Evento_Comprado,
  I.preco AS Preco_Pago,
  V.data AS Data_Venda
FROM Venda AS V
JOIN Comprador AS C ON V.id_comprador = C.id_comprador
JOIN Ingresso AS I ON V.id_ingresso = I.id_ingresso
JOIN Evento AS E ON I.id_evento = E.id_evento
WHERE C.id_comprador = ?; -- O ID do comprador é passado como parâmetro

🚀 Como Executar
Siga os passos abaixo para configurar o banco de dados e executar a aplicação.

1. Pré-requisitos (Banco de Dados PostgreSQL)
É necessário ter o PostgreSQL (v14+) instalado e em execução.

Para instalação, siga os procedimentos descritos no Relatório da Fase 2 (seção 3) .

Após a instalação, crie o banco de dados e o usuário que a aplicação irá usar. A aplicação está configurada para as seguintes credenciais (definidas em db.py):

Banco: tikevents

Usuário: dev

Senha: devpass

Você pode criar o banco e o usuário com os seguintes comandos SQL (via psql ou pgAdmin):

SQL

CREATE DATABASE tikevents;
CREATE USER dev WITH PASSWORD 'devpass';
GRANT ALL PRIVILEGES ON DATABASE tikevents TO dev;

Se tiver problema com as permissões ao entrar como dev volte (\q)  e entre como superusuario 
psql -U postgres -d tikevents

e volte para dev 
psql -U dev -d tikevents -h localhost

GRANT CREATE ON SCHEMA public TO nome_do_seu_usuario;  nesse caso deve ser dev


2. Configuração do Esquema (Tabelas)
Com o banco tikevents criado e acessível pelo usuário dev, execute o script SQL completo para criar todas as 11 tabelas, índices e restrições.

O script está localizado no documento TikEvents - Modelo BD - Fase 2.pdf (Seção 4. Script SQL para Criação das Tabelas) .

As tabelas serão criadas vazias, podem ser feitos inserts genericos para testes ou podem ser feitos pela interface

3. Configuração do Ambiente Python
Recomenda-se fortemente o uso de um ambiente virtual (venv) para isolar as dependências do projeto.

Crie o ambiente virtual:

Bash

python -m venv venv


Ative o ambiente:

No Linux/macOS:

Bash

source venv/bin/activate


No Windows:

Bash

venv\Scripts\activate


Instale a dependência: O projeto requer apenas a biblioteca psycopg2 para se conectar ao PostgreSQL.


Bash

pip install psycopg2-binary
4. Execução da Aplicação
Uma vez que o banco esteja configurado e as dependências instaladas, execute o arquivo main.py a partir do seu terminal:

Bash

python main.py
O sistema testará a conexão com o banco de dados. Se for bem-sucedido, exibirá o menu principal para interação.

📂 Estrutura do Projeto (Fase 3)
Os arquivos de código-fonte (.py) a serem entregues são:

db.py: Contém a DSN de conexão e a função genérica get_conn().

crud_artista.py: Camada de acesso a dados para a tabela Artista.

crud_local.py: Camada de acesso a dados para a tabela Local.

crud_setor.py: Camada de acesso a dados para a tabela Setor.

crud_assento.py: Camada de acesso a dados para a tabela Assento.

crud_evento.py: Camada de acesso a dados para a tabela Evento.

crud_comprador.py: Camada de acesso a dados para a tabela Comprador.

crud_evento_artista.py: Camada de acesso a dados para a tabela associativa Evento_Artista (N:N).

crud_ingresso.py: Camada de acesso a dados para a superclasse Ingresso e subclasses Ingresso_VIP/Ingresso_Padrao.

crud_venda.py: Camada de acesso a dados para a tabela Venda.

main.py: Camada de interface (CLI). Contém os menus de usuário, validação de entrada e chama as funções dos módulos CRUD.