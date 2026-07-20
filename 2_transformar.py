
# ==============================================================================
# FASE 2 - TRANSFORMAÇÃO DA CAMADA RAW PARA A CAMADA SILVER
# Banco: PostgreSQL - transparencia
# ==============================================================================
"""
FASE 2 - Transformação dos dados da camada Raw para a camada Silver.

Realiza a leitura das tabelas Raw, converte os tipos de dados,
calcula colunas derivadas e carrega os registros nas tabelas Silver,
seguindo a arquitetura Medallion.
"""

# ==============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS E AMBIENTE
# ==============================================================================
import sys
from pathlib import Path
from datetime import datetime

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from config import TAMANHO_BLOCO
from banco import conectar, executar, inserir_em_lote

# ==========================================================================
# FUNÇÕES ESPECÍFICAS DE CONVERSÃO E TRATAMENTO DE DADOS
# ==========================================================================

# Conversão de valores monetários
def converter_decimal(texto):
    """Converte os valores monetários textuais com virgula decimal em float. Vazio/invalido -> 0.0."""
    if texto is None:
        return 0.0
    texto = texto.strip()
    if texto == "":
        return 0.0
    # Formato BR: ponto e separador de milhar, virgula e decimal.
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0

 # Conversão de datas
def converter_data(texto):
    """Converte 'DD/MM/AAAA' em date. Vazio/invalido -> None (NULL no banco)."""
    if texto is None:
        return None
    texto = texto.strip()
    if texto == "":
        return None
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None

# Conversão de valores
def converter_inteiro(texto):
    """Converte um valor para inteiro. Retorna None se vazio ou inválido."""

    if texto is None:
        return None

    texto = str(texto).strip()

    if texto == "":
        return None

    try:
        return int(texto)
    except (ValueError, TypeError):
        return None

# ==========================================================================
# PIPELINE DE TRANSFORMAÇÃO RAW → SILVER
# Leitura em blocos, tratamento dos dados e carga na camada Silver
# ==========================================================================

def carregar_em_blocos(sql_select, sql_insert, converter_linha):
    """
    Lê os registros da camada Raw em blocos, converte cada linha e
    insere os dados na camada Silver.
    Retorna a quantidade total de registros processados.
    """
    con_leitura = conectar()
    con_escrita = conectar()

    try:
        cursor = con_leitura.cursor()
        cursor.execute(sql_select)

        total = 0

        while True:
            lote = cursor.fetchmany(TAMANHO_BLOCO)

            if not lote:
                break

            convertidas = [converter_linha(linha) for linha in lote]

            inserir_em_lote(con_escrita, sql_insert, convertidas)

            total += len(convertidas)

        cursor.close()
        return total

    finally:
        con_leitura.close()
        con_escrita.close()

# ==========================================================================
# CAMADA SILVER - TABELA VIAGEM (Tabela Principal)
# ==========================================================================
# Consulta utilizada para recuperar apenas as colunas necessárias da camada Raw.
# Os demais campos são descartados durante a transformação para manter
# a camada Silver mais enxuta e adequada para análise.

SELECT_VIAGEM = """
    SELECT id_viagem, num_proposta, situacao, viagem_urgente,
           cod_orgao_superior, nome_orgao_superior, nome_viajante, cargo,
           data_inicio, data_fim, destinos, motivo,
           valor_diarias, valor_passagens, valor_devolucao, valor_outros_gastos
    FROM raw_viagem
"""

INSERT_VIAGEM = """
    INSERT INTO silver_viagem
        (id_viagem, num_proposta, situacao, viagem_urgente,
         cod_orgao_superior, nome_orgao_superior, nome_viajante, cargo,
         data_inicio, data_fim, destinos, motivo,
         valor_diarias, valor_passagens, valor_devolucao, valor_outros_gastos,
         valor_total, duracao_dias)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def linha_viagem(raw):
    """Converte UMA linha da raw_viagem para o formato da silver_viagem."""
    # Desempacota o registro retornado pela consulta banco em variaveis nomeadas.
    (id_viagem, num_proposta, situacao, viagem_urgente,
     cod_orgao_superior, nome_orgao_superior, nome_viajante, cargo,
     data_inicio_txt, data_fim_txt, destinos, motivo,
     diarias_txt, passagens_txt, devolucao_txt, outros_txt) = raw
    
    # onverte os campos textuais para os respectivos tipos de dados.
    data_inicio = converter_data(data_inicio_txt)
    data_fim = converter_data(data_fim_txt)
    valor_diarias = converter_decimal(diarias_txt)
    valor_passagens = converter_decimal(passagens_txt)
    valor_devolucao = converter_decimal(devolucao_txt)
    valor_outros = converter_decimal(outros_txt)

    # Calcula o custo total da viagem.
    valor_total = (
        valor_diarias
        + valor_passagens
        + valor_outros
        - valor_devolucao
    )

    # Calcula a duração da viagem em dias.
    if data_inicio is not None and data_fim is not None:
        duracao_dias = (data_fim - data_inicio).days
    else:
        duracao_dias = None

    # Retorna os dados na mesma ordem definida no comando INSERT.
    return (id_viagem, num_proposta, situacao, viagem_urgente,
            cod_orgao_superior, nome_orgao_superior, nome_viajante, cargo,
            data_inicio, data_fim, destinos, motivo,
            valor_diarias, valor_passagens, valor_devolucao, valor_outros,
            valor_total, duracao_dias)
     
# ==========================================================================
# CAMADA SILVER - TABELA PASSAGEM
# ==========================================================================
# Consulta utilizada para recuperar os registros da tabela raw_passagem.
# Os campos são posteriormente convertidos para os tipos de dados
# definidos na camada Silver.

SELECT_PASSAGEM = """
    SELECT id_viagem, meio_transporte,
           pais_origem_ida, uf_origem_ida, cidade_origem_ida,
           pais_destino_ida, uf_destino_ida, cidade_destino_ida,
           valor_passagem, taxa_servico, data_emissao
    FROM raw_passagem
"""

# Comando de inserção na tabela silver_passagem.
INSERT_PASSAGEM = """
    INSERT INTO silver_passagem
        (id_viagem, meio_transporte,
         pais_origem_ida, uf_origem_ida, cidade_origem_ida,
         pais_destino_ida, uf_destino_ida, cidade_destino_ida,
         valor_passagem, taxa_servico, data_emissao)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def linha_passagem(raw):
    """Converte UMA linha da raw_passagem para o formato da silver_passagem."""
    (id_viagem, meio_transporte,
     pais_origem_ida, uf_origem_ida, cidade_origem_ida,
     pais_destino_ida, uf_destino_ida, cidade_destino_ida,
     valor_passagem_txt, taxa_servico_txt, data_emissao_txt) = raw

    return (id_viagem, meio_transporte,
            pais_origem_ida, uf_origem_ida, cidade_origem_ida,
            pais_destino_ida, uf_destino_ida, cidade_destino_ida,
            converter_decimal(valor_passagem_txt),
            converter_decimal(taxa_servico_txt),
            converter_data(data_emissao_txt))

# ==========================================================================
# CAMADA SILVER - TABELA PAGAMENTO
# ==========================================================================
# Consulta utilizada para recuperar os registros da tabela raw_pagamento.
# Os valores monetários serão convertidos para o tipo DECIMAL antes da carga.

SELECT_PAGAMENTO = """
    SELECT id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
           tipo_pagamento, valor
    FROM raw_pagamento
"""

INSERT_PAGAMENTO = """
    INSERT INTO silver_pagamento
        (id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
         tipo_pagamento, valor)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

def linha_pagamento(raw):
    """
    Converte um registro da tabela raw_pagamento para o formato
    da tabela silver_pagamento.
    """
    (id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
    tipo_pagamento, valor) = raw

    return (id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
            tipo_pagamento, 
            converter_decimal(valor))

# ==========================================================================
# CAMADA SILVER - TABELA TRECHO
# ==========================================================================
# Consulta utilizada para recuperar os registros da tabela raw_trecho.
# Os campos serão convertidos para os tipos de dados definidos
# na camada Silver.

SELECT_TRECHO = """
    SELECT id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
           destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias
    FROM raw_trecho
"""

INSERT_TRECHO = """
    INSERT INTO silver_trecho
        (id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
         destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
def linha_trecho(raw):
    """
    Converte um registro da tabela raw_trecho para o formato
    da tabela silver_trecho.

    Parâmetros:
        raw (tuple): Registro proveniente da tabela raw_trecho.

    Retorno:
        tuple: Registro convertido para inserção na tabela silver_trecho.
    """
    (id_viagem, sequencia_trecho_txt, origem_data_txt, origem_uf, origem_cidade,
     destino_data_txt, destino_uf, destino_cidade, meio_transporte, numero_diarias_txt) = raw

    # Retorna os dados convertidos na mesma ordem definida no INSERT.
    return (
        id_viagem,
        converter_inteiro(sequencia_trecho_txt),
        converter_data(origem_data_txt),
        origem_uf,
        origem_cidade,
        converter_data(destino_data_txt),
        destino_uf,
        destino_cidade,
        meio_transporte,
        converter_decimal(numero_diarias_txt),
    )

# ==============================================================================
# EXECUÇÃO DO PROCESSO DE TRANSFORMAÇÃO
# ==============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("INICIANDO A CARGA DA CAMADA SILVER")
    print("=" * 70)

    # Limpa as tabelas da camada Silver antes da carga.
    print("\nLimpando as tabelas da camada Silver...")

    con = conectar()

    executar(
        con,
        """
        TRUNCATE TABLE
            silver_viagem,
            silver_passagem,
            silver_pagamento,
            silver_trecho
        RESTART IDENTITY CASCADE;
        """
    )

    con.close()

    # --------------------------------------------------------------------------
    # Tabela silver_viagem
    # --------------------------------------------------------------------------
    print("\nCarregando tabela silver_viagem...")
    n = carregar_em_blocos(SELECT_VIAGEM, INSERT_VIAGEM, linha_viagem)
    print(f"silver_viagem: {n} linhas carregadas.")

    # --------------------------------------------------------------------------
    # Tabela silver_passagem
    # --------------------------------------------------------------------------
    print("Carregando silver_passagem...")
    n = carregar_em_blocos(SELECT_PASSAGEM, INSERT_PASSAGEM, linha_passagem)
    print(f"silver_passagem: {n} linhas carregada.")
          
    # --------------------------------------------------------------------------
    # Tabela silver_pagamento
    # --------------------------------------------------------------------------
    print("Carregando silver_pagamento...")
    n = carregar_em_blocos(SELECT_PAGAMENTO, INSERT_PAGAMENTO, linha_pagamento)
    print(f"silver_pagamento: {n} linhas carregadas.")      

    # --------------------------------------------------------------------------
    # Tabela silver_trecho
    # --------------------------------------------------------------------------
    print("Carregando silver_trecho...")
    n = carregar_em_blocos(SELECT_TRECHO, INSERT_TRECHO, linha_trecho)
    print(f"silver_trecho: {n} linhas carregadas.")

    print("\n" + "=" * 70)
    print("CARGA DA CAMADA SILVER FINALIZADA COM SUCESSO!")
    print("=" * 70)