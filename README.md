# Análise de Dados com Python e PostgreSQL – Pipeline ETL

(Arquitetura Medallion)

## Análise de Viagens a Serviço do Governo Federal

Projeto Avaliativo - Módulo 1 - Semana 13

Aluna: Claudineia Ferreira
Turma: Análise De Dados T1

## 📖 Sobre o Projeto

Este projeto foi desenvolvido como atividade prática do Curso de **Análise de
Dados**, com o objetivo de construir um  **pipeline  ETL completo**, utilizando Python e
PostgreSQL, aplicando a **Arquitetura Medallion (Raw, Silver e Gold)**.

O pipeline automatiza todo o processo de extração, armazenamento, limpeza, transformação e análise
dos dados, permitindo gerar indicadores confiáveis para apoio à tomada de decisão,

## Fonte dos Dados

Os dados utilizados foram obtidos do Portal da Transparência do Governo Federal e referem-se às
Viagens a Serviço.

Para este projeto foi utilizada a base referente ao primeiro semestre do ano de 2025, posteriormente disponibilizada em um arquivo compactado  (.zip)  para facilitar o desenvolvimento do pipeline ETL.

A base reúne informações sobre viagens oficiais realizadas por servidores públicos federais, incluindo despesas com diárias, passagens, trechos percorridos e pagamentos efetuados pelos órgãos da Administração Pública Federal.

### A consulta oficial pode ser acessada em:

Portal da Transparência do Governo Federal:

https://portaldatransparencia.gov.br/viagens/consulta

## Problema

Os dados publicados pelo Portal da Transparência encontram-se em formato bruto, dificultando sua
utilização para análises gerenciais.
O projeto resolve esse problema por meio de um processo ETL que:

- Realiza o download automático dos arquivos;
- Preserva os dados originais na camada raw;
- Transforma e padroniza os dados na camada silver;
- Gera indicadores e análises na camada gold;

## Objetivos

- Automatizar o download dos arquivos.
- Armazenar os dados brutos.
- Aplicar limpeza e padronização.
- Garantir integridade referencial.
- Construir uma camada analítica.
- Responder perguntas de negócio utilizando SQL.
- Produzir gráficos para visualização dos resultados

## Arquitetura Medallion

O pipeline segue o modelo Medallion, dividido em três camadas.

```text

              Portal da Transparência
                         │
                         ▼
                Download Automático
                         │
                         ▼
                 Camada RAW (Bronze)
           Dados originais sem alterações
                         │
                         ▼
                Camada SILVER (Prata)
        Dados limpos, tipados e relacionados
                         │
                         ▼
                 Camada GOLD (Ouro)
           Indicadores, métricas e análises

```

## Estrutura do Projeto

```text

analise-viagens-governo-2025/
│
├── config.py
├── banco.py
├── .env.example
├── .gitignore
├── requirements.txt
│
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── 3_analise.ipynb
│
├── README.md
│
├── data/
│   ├── raw/
│   ├── silver/
│   └── gold/
│
└── imagens/

```

## Tecnologias utilizadas

###Linguagem

- Python 3

## Banco de Dados

- PostgreSQL

## Bibliotecas

- Pandas
- NumPy
- SQLAlchemy
- Psycopg2
- Requests
- Python-dotenv
- Matplotlib
- Jupyter Notebook

### Modelo do Banco

O banco é composto por oito tabelas.

### Camada Raw

- raw_viagem
- raw_pagamento
- raw_passagem
- raw_trecho

Características:

- todas as colunas VARCHAR;
- sem chaves;
- sem constraints;
- preservação total do arquivo original.

### Camada Silver

- silver_viagem
- silver_pagamento
- silver_passagem
- silver_trecho

Características:

- dados tipados;
- PRIMARY KEY;
- FOREIGN KEY;
- NOT NULL;
- CHECK;
- UNIQUE;
- integridade referencial

## Fluxo do Pipeline

```text

 Download ZIP
      │
      ▼
Extração dos CSV
      │
      ▼
  Carga RAW
      │
      ▼
Transformação
      │
      ▼
Carga SILVER
      │
      ▼
Criação GOLD
      │
      ▼
Consultas SQL
      │
      ▼
  Gráficos

```

## Como executar

### 1. Clonar o projeto

Para acessar o código fonte ou clonar a página, acesse o link abaixo:

🔗 **[Acesse o Repositório Oficial](https://github.com/fclaudineiasc-web/Projeto_Analise_de_Viagens)**

### 2. Criar ambiente virtual

Windows

```bash
python-m venv venv

venv\Scripts\activate
```

Linux

```bash
python3-m venv venv

source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install-r requirements.txt
```

### 4. Configurar o arquivo .env

Copie:

```bash
.env.example
```

para

```bash
.env
```

Configure:

```bash
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

DRIVE_FILE_ID=
```

### 5. Criar o banco

Execute o arquivo:

```bash
sql/0_criar_banco.sql
```

### 6. Executar a Extração

```bash
python src/1_extrair.py
```

### 7. Executar a Transformação

```bash
python src/2_transformar.py
```

### 8. Executar as análises

Abra:

```bash
notebooks/3_analise.ipynb
```

e execute todas as células.

## Perguntas de Negócio

As seguintes análises foram desenvolvidas:

1. Os cinco órgãos com maior custo total.
2. Os três destinos com maior custo médio por viagem.
3. A viagem de maior duração e seu custo total.
4. O tipo de pagamento com maior valor médio.
5. O meio de transporte mais utilizado.
6. A UF de destino mais frequente.
7. O órgão que apresentou maior gasto total.

## Visualizações

O notebook produz gráficos contendo:

- título;
- eixos identificados;
- legenda quando necessária;
- escalas adequadas;
- informações derivadas da camada Gold

- Código modular.
- Padrão PEP 8.
- Credenciais armazenadas no arquivo .env
- Uso de tratamento de exceções ( try/except ).
- Processo idempotente ( TRUNCATE antes da carga ).
- Leitura dos arquivos CSV em blocos ( chunksize ).
- Integridade referencial nas tabelas Silver

## Conclusões

O desenvolvimento deste projeto permitiu aplicar conceitos fundamentais de Engenharia de Dados, contemplando todas as etapas de um pipeline ETL.

A utilização da Arquitetura Medallion garantiu a separação entre dados brutos, dados tratados e dados analíticos, proporcionando maior confiabilidade às informações.

A camada Gold possibilitou responder às perguntas de negócio propostas, fornecendo indicadores e visualizações que facilitam a interpretação dos gastos públicos com viagens a serviço.

Além de consolidar conhecimentos em Python e SQL, o projeto reforçou a importância da modelagem de dados, da integridade referencial e da automação dos processos de tratamento de dados.
