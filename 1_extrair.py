# ==============================================================================
# FASE 1 - EXTRAÇÃO E CARGA DA CAMADA RAW
# Banco: PostgreSQL - transparencia
# ==============================================================================
# Baixa o .zip do Google Drive, extrai os 4 CSVs e carrega cada um na sua
#tabela raw_* SEM tratar o conteudo. O processo e idempotente (TRUNCATE antes
#de carregar)
"""
FASE 1 - EXTRAÇÃO E CARGA DA CAMADA RAW 
Pipeline : Download -> Extração -> Carga Segura em Chunks
"""

import sys
import zipfile
from pathlib import Path
import gdown
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS E AMBIENTE
# ==============================================================================

# Caminhos base usando Pathlib (evita quebras entre Windows/Linux)
RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from config import (
    DRIVE_FILE_ID,
    PASTA_DADOS,
    ARQUIVOS,
    TAMANHO_BLOCO,
    CSV_SEPARADOR,
    CSV_ENCODING,
)

from banco import conectar, executar, inserir_em_lote

PASTA_DADOS = RAIZ / "data"
CAMINHO_ZIP = PASTA_DADOS / "viagens_2025_6meses.zip" # Caminho do arquivo .zip 

# ==============================================================================
# 2. FUNÇÕES DE INFRAESTRUTURA (DOWNLOAD E EXTRAÇÃO)
# ==============================================================================
def baixar_zip():
    """BLOCO 2: baixa o .zip do Google Drive para a pasta data/."""
    
    PASTA_DADOS.mkdir(exist_ok=True)

    # Se o zip ja foi baixado , não baixa novsmente.
    if CAMINHO_ZIP.exists():
        print(f"O arquivo Zip ja existe em {CAMINHO_ZIP} -> pulando download.")
        return

    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    print("-> Iniciando download do arquivo do Google Drive...")
    
    try:
        gdown.download(url, str(CAMINHO_ZIP), quiet=False)
        print("-> Download concluído com sucesso.")
    except Exception as e:
        print(f"ERR: Erro crítico ao baixar o arquivo: {e}")
        sys.exit(1)

# ==============================================================================
# 3. FUNÇÕES DE BANCO DE DADOS E CARGA (PIPELINE)
# ==============================================================================

def extrair_zip():

    """BLOCO 3: descompacta os 4 CSVs de dentro do arquivo .zip."""
    # Abre o arquivo .zip em modo leitura.
    print("Extraindo os CSVs do .zip...")
    with zipfile.ZipFile(CAMINHO_ZIP, "r") as zip_ref:
        # Extrai todo o conteudo do arquivo .Zip para a pasta data/.
        zip_ref.extractall(PASTA_DADOS)
    print("Extracao concluida.")

 # Mapeia as colunas oficiais do banco de dados
def obter_colunas(conexao, tabela):
    """ Nomes das colunas da tabela, na ordem do banco."""
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = %s ORDER BY ordinal_position;",
        (tabela,),
    )
    colunas = [linha[0] for linha in cursor.fetchall()]
    cursor.close()
    return colunas

def carregar_csv_na_raw(conexao, caminho_csv, tabela_raw, colunas): 
    """Lê um CSV em blocos e insere na tabela raw (TRUNCATE antes)."""
    # Limpa a tabela antes de carregar -> garante idempotencia 
    executar(conexao, f"TRUNCATE TABLE {tabela_raw};")

    # Monta o INSERT dinamicamente, com um %s para cada coluna.
    lista_colunas = ", ".join(colunas)
    marcadores = ", ".join(["%s"] * len(colunas))
    sql_insert = f"INSERT INTO {tabela_raw} ({lista_colunas}) VALUES ({marcadores})"

     # 3. Leitura otimizada do arquivo texto
    leitor = pd.read_csv(
        caminho_csv,
        sep=CSV_SEPARADOR,        
        encoding=CSV_ENCODING,   
        dtype=str,                # Mantém dados puros (Camada RAW não trata tipos)
        keep_default_na=False,    # Evita que campos vazios virem float 'NaN'
        header=0,                 # Ignora o cabeçalho original do arquivo
        names=colunas,            # Força o mapeamento direto no schema do banco
        chunksize=TAMANHO_BLOCO, 
    )

    total = 0
    for bloco in leitor:
        
        linhas = list(bloco.itertuples(index=False, name=None))
        inserir_em_lote(conexao, sql_insert, linhas)  
        total += len(linhas)

    print(f"-> Carga de {tabela_raw} finalizada com sucesso! Total: {total} linhas carregadas.")
    
# ==============================================================================
# 4. EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print(" INICIANDO PIPELINE DE DADOS BRUTOS (FASE 1 - RAW) ")
    print("=" * 50)
    try:
        # Baixar -> descompactar -> carregar cada CSV.
        baixar_zip()
        extrair_zip()

        conexao = conectar()
        try:
            
            for chave, info in ARQUIVOS.items():
                caminho_csv = PASTA_DADOS / info["csv"]
                tabela = info["tabela_raw"]
                print(f"\nCarregando {info['csv']} -> {tabela}")
                colunas = obter_colunas(conexao, tabela)
                carregar_csv_na_raw(conexao, caminho_csv, tabela, colunas)
        finally:
            
            conexao.close() # Fechar conexão

        print("\n=== FASE 1 CONCLUÍDA COM SUCESSO ===")

        print("\nDados brutos carregados na camada Raw.")
    except Exception as erro:
        print(f"\nErro na extracao: {erro}")
       

















