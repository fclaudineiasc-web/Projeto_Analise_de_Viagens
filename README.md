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

## Conclusões
A análise dos dados de viagens oficiais, utilizando a arquitetura de dados em camadas Raw, Silver e Gold, permitiu identificar padrões de gastos, destinos, meios de transporte e comportamento das despesas públicas durante o período analisado.

### 1. Concentração dos gastos por órgãos públicos

Os resultados demonstram que os gastos com viagens estão concentrados em poucos órgãos governamentais. O Ministério da Justiça e Segurança Pública apresentou o maior custo total,seguido pelo Ministério da Defesa e pelo Ministério da Educação.

Esse cenário indica que órgãos com atividades operacionais, fiscalização, segurança, defesa e atuação nacional possuem maior necessidade de deslocamentos, refletindo diretamente no volume de recursos destinados às viagens.

<img width="1192" height="584" alt="image" src="https://github.com/user-attachments/assets/511cae19-dbba-4fd1-9dba-535b27cbd352" />

## 2. Destinos com maiores custos médios

A análise dos destinos revelou que alguns municípios apresentaram custos médios elevados por viagem, destacando-se:

- Sananduva/RS – custo médio de R$ 108.309,30
- Monte Negro/RO – custo médio de R$ 104.979,28
- Nonoai/RS – custo médio de R$ 99.278,92

Esses valores indicam que determinados destinos podem envolver viagens com maior duração, maiores distâncias percorridas ou necessidades específicas de deslocamento e permanência.

## 3. Viagem de Maior Duração e Seu Custo Total

Foram identificadas viagens com duração superior a um ano, sendo a maior com 383 dias. Entretanto, algumas dessas viagens apresentaram valor total igual a zero, indicando a necessidade de validação da qualidade dos registros financeiros.

Esse resultado evidencia a importância de processos de tratamento e auditoria dos dados antes da tomada de decisão, evitando interpretações incorretas.

## 4. Predominância das despesas com diárias

As diárias representam a principal categoria de pagamento analisada:

- 401.463 pagamentos
-Valor médio: R$ 2.078,28
-Valor total: R$ 834,3 milhões

<img width="884" height="584" alt="image" src="https://github.com/user-attachments/assets/a465a22b-aca4-4d14-b85d-6707ae164e02" />

Esse resultado demonstra que a permanência dos servidores nos locais de destino representa uma parcela significativa dos custos das viagens oficiais.

## 5. Uso predominante de veículos oficiais

O meio de transporte mais utilizado foi o Veículo Oficial, com 386.424 utilizações, seguido pelo transporte aéreo, com 232.666 utilizações.

Esse comportamento indica uma forte utilização da frota própria dos órgãos públicos, enquanto o transporte aéreo permanece relevante principalmente para deslocamentos de maior distância.

<img width="784" height="584" alt="image" src="https://github.com/user-attachments/assets/67c16e88-67df-4dad-8330-87b0c2677c3e" />


6. Concentração geográfica das viagens

As UFs com maior frequência de destino foram:

- 1. São Paulo – 79.684 viagens
- 2. Distrito Federal – 75.449 viagens
- 3. Minas Gerais – 49.316 viagens
- 4. Rio de Janeiro – 43.058 viagens
- 5. Paraná – 38.422 viagens

Os resultados mostram uma concentração das viagens em estados com maior relevância administrativa, econômica e institucional.

Conclusão Geral

A construção da camada Gold possibilitou transformar dados brutos de viagens em informações estratégicas para análise de gastos públicos. Os resultados mostram que os custos estão relacionados principalmente ao órgão responsável, tipo de pagamento, duração da viagem e características do deslocamento.

A análise também revelou pontos que podem ser aprimorados, como a validação de registros com valores zerados e viagens de longa duração. Dessa forma, a solução desenvolvida contribui para maior transparência, controle orçamentário e apoio à tomada de decisão na gestão das viagens oficiais.
