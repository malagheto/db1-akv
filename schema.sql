-- =====================================================
-- Script de criação do banco de dados TikEvents
-- Sistema de Gestão de Eventos
-- SGBD: PostgreSQL 14+
-- =====================================================
-- Tabela de artistas/bandas
CREATE TABLE Artista (
 id_artista SERIAL PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 genero VARCHAR(50)
);
-- Tabela de locais de eventos
CREATE TABLE Local (
 id_local SERIAL PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 endereco VARCHAR(150),
 capacidade INT NOT NULL CHECK (capacidade > 0)
);
-- Tabela de setores dentro dos locais
CREATE TABLE Setor (
 id_setor SERIAL PRIMARY KEY,
 id_local INT NOT NULL REFERENCES Local(id_local) ON DELETE CASCADE,
 nome VARCHAR(60) NOT NULL,
 UNIQUE (id_local, nome)
);
-- Tabela de assentos
CREATE TABLE Assento (
 id_assento SERIAL PRIMARY KEY,
 id_setor INT NOT NULL REFERENCES Setor(id_setor) ON DELETE CASCADE,
 fileira VARCHAR(10) NOT NULL,
 numero VARCHAR(10) NOT NULL,
 UNIQUE (id_setor, fileira, numero)
);
-- Tabela de eventos
CREATE TABLE Evento (
 id_evento SERIAL PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 data DATE NOT NULL,
 horario TIME,
 descricao TEXT,
 id_local INT NOT NULL REFERENCES Local(id_local)
);
-- Tabela associativa Evento-Artista (N:N)
CREATE TABLE Evento_Artista (
 id_evento INT NOT NULL REFERENCES Evento(id_evento) ON DELETE CASCADE,
 id_artista INT NOT NULL REFERENCES Artista(id_artista) ON DELETE CASCADE,
 PRIMARY KEY (id_evento, id_artista)
);
-- Tabela de ingressos (superclasse)
CREATE TABLE Ingresso (
 id_ingresso SERIAL PRIMARY KEY,
 id_evento INT NOT NULL REFERENCES Evento(id_evento) ON DELETE CASCADE,
 preco NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
 id_assento INT NULL REFERENCES Assento(id_assento),
 CONSTRAINT uq_evento_assento UNIQUE (id_evento, id_assento)
);
-- Especialização: Ingresso VIP
CREATE TABLE Ingresso_VIP (
 id_ingresso INT PRIMARY KEY REFERENCES Ingresso(id_ingresso) ON DELETE CASCADE,
 beneficios TEXT
);
-- Especialização: Ingresso Padrão
CREATE TABLE Ingresso_Padrao (
 id_ingresso INT PRIMARY KEY REFERENCES Ingresso(id_ingresso) ON DELETE CASCADE
);
-- Tabela de compradores
CREATE TABLE Comprador (
 id_comprador SERIAL PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
);
-- Tabela de vendas
CREATE TABLE Venda (
 id_venda SERIAL PRIMARY KEY,
 data DATE NOT NULL,
 quantidade INT NOT NULL CHECK (quantidade > 0),
 id_ingresso INT NOT NULL REFERENCES Ingresso(id_ingresso),
 id_comprador INT NOT NULL REFERENCES Comprador(id_comprador)
);
-- Índices para otimização
CREATE INDEX idx_evento_data ON Evento(data);
CREATE INDEX idx_evento_local ON Evento(id_local);
CREATE INDEX idx_ingresso_evento ON Ingresso(id_evento);
CREATE INDEX idx_venda_data ON Venda(data);
CREATE INDEX idx_venda_comprador ON Venda(id_comprador);
CREATE INDEX idx_comprador_email ON Comprador(email);