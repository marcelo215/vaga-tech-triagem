# Triagem Inteligente de Currículos

Sistema em Python que automatiza a triagem de currículos para uma agência de empregos focada no ecossistema de tecnologia. O projeto combina regras de negócio determinísticas com análise de IA generativa, monitorando de forma rigorosa o consumo de tokens e o custo de cada execução.

Desenvolvido como Checkpoint 1 da disciplina de IA & ML, sob orientação do professor Wellington Cidade Silva.

## Como funciona

O fluxo é dividido em três etapas sequenciais:

**1. Extração de PDF**
O currículo do candidato é lido a partir de um arquivo PDF e convertido em texto bruto, usando a biblioteca `pypdf`.

**2. Camada determinística**
Antes de qualquer chamada a um modelo de IA, o sistema aplica filtros de negócio fixos sobre o texto extraído:
- Validação do tempo mínimo de experiência exigido pela vaga.
- Compatibilidade da pretensão salarial do candidato com o orçamento disponível.

Só os candidatos aprovados nessa etapa avançam para a análise generativa, o que evita gastar processamento e dinheiro com perfis que já não atendem aos requisitos mínimos.

**3. Camada generativa**
Para os candidatos aprovados, o sistema interage com um LLM para gerar:
- Um parecer qualitativo sobre a senioridade e as soft skills implícitas no currículo.
- Um resumo executivo customizado, pronto para ser enviado ao recrutador da empresa contratante.

Cada execução dessa etapa é acompanhada de um relatório de consumo de tokens, contando separadamente os tokens de entrada (prompt) e de saída (completion) com a biblioteca `tiktoken`, além de uma estimativa de custo em dólares.

## Estrutura do projeto

```
vaga-tech-triagem/
├── curriculos/
│   └── curriculo_teste.pdf
├── src/
│   └── main.py
├── integrantes.txt
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.10 ou superior
- Dependências listadas em `requirements.txt`

## Instalação

```bash
git clone <link-do-repositorio>
cd vaga-tech-triagem
pip install -r requirements.txt
```

## Execução

```bash
python src/main.py
```

Caso o arquivo `curriculos/curriculo_teste.pdf` não seja encontrado, o sistema utiliza automaticamente um currículo de exemplo, garantindo que a demonstração funcione mesmo sem um PDF real disponível.

## Modo de operação da IA

Por padrão, o projeto roda com `MODO_SIMULADO_IA = True` em `main.py`, o que permite testar todo o fluxo sem necessidade de uma chave de API. Para usar um modelo de linguagem real, basta:

1. Instalar o pacote correspondente (por exemplo, `pip install anthropic`).
2. Configurar a variável de ambiente com a chave de API.
3. Alterar `MODO_SIMULADO_IA` para `False` em `main.py`.

## Exemplo de saída

```
--- [Camada Determinística] Aplicando Filtros Rígidos ---
Buscando requisitos mínimos: 3 anos de exp / Orçamento máximo: R$ 10000
 Experiência encontrada: 5 ano(s)  -> APROVADO
 Pretensão salarial encontrada: R$ 8000.00  -> APROVADO
 Candidato APROVADO nos filtros iniciais. Enviando para IA...

--- [Camada Generativa] Resultado da Análise ---
### Resumo Executivo ###
Profissional com sólida base técnica em Python, pronto para atuar em projetos de médio a alto nível de complexidade.

### Parecer Qualitativo ###
Senioridade estimada: Pleno. Boa comunicação implícita pela clareza na descrição das experiências.

=============================================
      RELATÓRIO DE CONSUMO DE TOKENS
=============================================
Tokens de Entrada (Prompt):    72
Tokens de Saída (Completion):  56
Total de Tokens Utilizados:    128
Estimativa de Custo Total:     $0.000044 USD
=============================================
```

## Tecnologias utilizadas

- Python
- pypdf
- tiktoken
- Git e GitHub

## Equipe

Consulte o arquivo `integrantes.txt` para a lista completa de integrantes, RMs e o link do repositório.