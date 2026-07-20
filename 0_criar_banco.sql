-- ==============================================================================
-- PROJETO: ANÁLISE DE VIAGENS A SERVIÇO
-- FASE 0 - CRIAÇÃO DO BANCO E TABELAS (0_criar_banco.sql)
-- SGBD: PostgreSQL
-- ==============================================================================
--- =============================================================================
--- CRIAÇÃO DO DATABASE
--- =============================================================================

-- ATENÇÃO NO VS CODE: Execute estas duas linhas primeiro, 
-- reconecte sua extensão no banco "transparencia" e execute o restante.

DROP DATABASE IF EXISTS transparencia;
CREATE DATABASE transparencia;

-- ==============================================================================
-- CAMADA RAW (Cópia fiel dos CSVs)
-- ==============================================================================

-- criação das 4 tabelas Raw (todas as colunas como VARCHAR, cópia fiel dos CSVs.
-- Usamos DROP na RAW para permitir reexecuções limpas do script de carga (Full Load).

DROP TABLE IF EXISTS raw_viagem CASCADE;
CREATE TABLE raw_viagem (
    id_viagem                 VARCHAR(255),
    num_proposta              VARCHAR(255),
    situacao                  VARCHAR(255),
    viagem_urgente            VARCHAR(255),
    justificativa_urgencia    VARCHAR(4000),
    cod_orgao_superior        VARCHAR(255),
    nome_orgao_superior       VARCHAR(255),
    cod_orgao_solicitante     VARCHAR(255),
    nome_orgao_solicitante    VARCHAR(255),
    cpf_viajante              VARCHAR(255),
    nome_viajante             VARCHAR(255),
    cargo                     VARCHAR(255),
    funcao                    VARCHAR(255),
    descricao_funcao          VARCHAR(255),
    data_inicio               VARCHAR(255),
    data_fim                  VARCHAR(255),
    destinos                  VARCHAR(4000),
    motivo                    VARCHAR(4000),
    valor_diarias             VARCHAR(255),
    valor_passagens           VARCHAR(255),
    valor_devolucao           VARCHAR(255),
    valor_outros_gastos       VARCHAR(255)
);

DROP TABLE IF EXISTS raw_passagem CASCADE;
CREATE TABLE raw_passagem(
    id_viagem                 VARCHAR(255),
    num_proposta              VARCHAR(255),
    meio_transporte           VARCHAR(255),
    pais_origem_ida           VARCHAR(255),
    uf_origem_ida             VARCHAR(255),
    cidade_origem_ida         VARCHAR(255),
    pais_destino_ida          VARCHAR(255),
    uf_destino_ida            VARCHAR(255),
    cidade_destino_ida        VARCHAR(255),
    pais_origem_volta         VARCHAR(255),
    uf_origem_volta           VARCHAR(255),
    cidade_origem_volta       VARCHAR(255),
    pais_destino_volta        VARCHAR(255),
    uf_destino_volta          VARCHAR(255),
    cidade_destino_volta      VARCHAR(255),
    valor_passagem            VARCHAR(255),
    taxa_servico              VARCHAR(255),
    data_emissao              VARCHAR(255),
    hora_emissao              VARCHAR(255)
);

DROP TABLE IF EXISTS raw_pagamento CASCADE;
CREATE TABLE raw_pagamento(
    id_viagem                 VARCHAR(255),
    num_proposta              VARCHAR(255),
    cod_orgao_superior        VARCHAR(255),
    nome_orgao_superior       VARCHAR(255),
    cod_orgao_pagador         VARCHAR(255),
    nome_orgao_pagador        VARCHAR(255),
    cod_ug_pagadora           VARCHAR(255),
    nome_ug_pagadora          VARCHAR(255),
    tipo_pagamento            VARCHAR(255),
    valor                     VARCHAR(255)
);

DROP TABLE IF EXISTS raw_trecho CASCADE;
CREATE TABLE raw_trecho(
    id_viagem                 VARCHAR(255),
    num_proposta              VARCHAR(255),
    sequencia_trecho          VARCHAR(255),
    origem_data               VARCHAR(255),
    origem_pais               VARCHAR(255),
    origem_uf                 VARCHAR(255),
    origem_cidade             VARCHAR(255),
    destino_data              VARCHAR(255),
    destino_pais              VARCHAR(255),
    destino_uf                VARCHAR(255),
    destino_cidade            VARCHAR(255),
    meio_transporte           VARCHAR(255),
    numero_diarias            VARCHAR(255),
    missao                    VARCHAR(255)
);
-- ==============================================================================
-- 2. CAMADA SILVER (Tipadas, PK, FK e constraints)
-- ==============================================================================

-- criação das 4 tabelas Silver (tipadas, com PK, FK e duas constraints extras por tabela).

-- É crucial dropar na ordem inversa das FKs para não quebrar restrições existentes

DROP TABLE IF EXISTS trecho_viagem;
DROP TABLE IF EXISTS trecho_passagem;
DROP TABLE IF EXISTS trecho_pagamento;
DROP TABLE IF EXISTS trecho_viagem;
---------------------------------------------------------------------------------
-- 1. Tabela Principal Silver Viagem
---------------------------------------------------------------------------------

-- Tabela Silver Viagem
CREATE TABLE silver_viagem (
    id_viagem              VARCHAR(20)  NOT NULL,
    num_proposta           VARCHAR(20),
    situacao               VARCHAR(50),
    viagem_urgente         VARCHAR(5),
    cod_orgao_superior     VARCHAR(20),
    nome_orgao_superior    VARCHAR(255) NOT NULL, -- Constraint 1 (NOT NULL)
    nome_viajante          VARCHAR(255),
    cargo                  VARCHAR(255),
    data_inicio            DATE, 
    data_fim               DATE,
    destinos               VARCHAR(4000),
    motivo                 VARCHAR(4000),
    valor_diarias          DECIMAL(10,2), 
    valor_passagens        DECIMAL(10,2), 
    valor_devolucao        DECIMAL(10,2), 
    valor_outros_gastos    DECIMAL(10,2), 
    valor_total            DECIMAL(12,2), 
    duracao_dias           INTEGER,
    PRIMARY KEY (id_viagem),
    CONSTRAINT chk_valor_diarias CHECK (valor_diarias >= 0)  -- Constraint 2 (CHECK)
);
---------------------------------------------------------------------------------
-- 2. Tabelas Dependentes (FK-> silver_viagem)
---------------------------------------------------------------------------------

--  Tabela Silver Pagamento
CREATE TABLE silver_pagamento (
    id_pagamento              SERIAL, 
    id_viagem                 VARCHAR(20) NOT NULL,
    num_proposta              VARCHAR(20),
    nome_orgao_pagador        VARCHAR(255),
    nome_ug_pagadora          VARCHAR(255), 
    tipo_pagamento            VARCHAR(50) NOT NULL, -- Constraint 1 (NOT NULL)
    valor                     DECIMAL(10,2),
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem), -- Relacionamento (Foreign Key)
    CONSTRAINT chk_valor_pagamento CHECK (valor >= 0)  -- Constraint 2 (CHECK)
);

--  Tabela Silver Passagem
CREATE TABLE silver_passagem (
    id_passagem              SERIAL,                   
    id_viagem                VARCHAR(20) NOT NULL,
    meio_transporte          VARCHAR(50),
    pais_origem_ida          VARCHAR(60),
    uf_origem_ida            VARCHAR(40),
    cidade_origem_ida        VARCHAR(80),
    pais_destino_ida         VARCHAR(60),
    uf_destino_ida           VARCHAR(40),
    cidade_destino_ida       VARCHAR(80),
    valor_passagem           DECIMAL(10,2),
    taxa_servico             DECIMAL(10,2),
    data_emissao             DATE,
    PRIMARY KEY(id_passagem),
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem) ON DELETE CASCADE,  -- Relacionamento (Foreign Key)
    CONSTRAINT chk_passagem_valor CHECK (valor_passagem >= 0), -- Constraints 1 e 2 (CHECKs)
    CONSTRAINT chk_passagem_servico CHECK (taxa_servico >= 0)
);

-- Tabela Silver Trecho
CREATE TABLE silver_trecho (
    id_trecho              SERIAL, 
    id_viagem              VARCHAR(20) NOT NULL,
    sequencia_trecho       INT,
    origem_data            DATE,
    origem_uf              VARCHAR(40),
    origem_cidade          VARCHAR(80),
    destino_data           DATE,
    destino_uf             VARCHAR(40),
    destino_cidade         VARCHAR(80),
    meio_transporte        VARCHAR(50),
    numero_diarias         DECIMAL(10,2),
    PRIMARY KEY (id_trecho),
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem) ON DELETE CASCADE, -- Relacionamento (Foreign Key)
    CONSTRAINT chk_trecho_diarias CHECK (numero_diarias >= 0), 
    CONSTRAINT uq_trecho UNIQUE (id_viagem, sequencia_trecho)  -- Constraint 2 (UNIQUE)
);
