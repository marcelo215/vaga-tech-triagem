# Triagem Inteligente de Currículos

Sistema em Python que automatiza a triagem de currículos para uma agência de empregos focada no ecossistema de tecnologia. O projeto combina regras de negócio determinísticas com análise de IA generativa (rodando localmente via Ollama), monitorando o consumo de tokens e o custo estimado de cada execução.

Desenvolvido como Checkpoint 1 da disciplina de IA & ML, sob orientação do professor Wellington Cidade Silva.

## Como funciona

O fluxo é dividido em três etapas sequenciais:

**1. Extração de PDF**
O currículo do candidato é lido a partir de um arquivo PDF e convertido em texto bruto, usando a biblioteca `pypdf`.

**2. Camada determinística**
Antes de qualquer chamada a um modelo de IA, o sistema aplica filtros de negócio fixos sobre o texto extraído:
- Validação do tempo mínimo de experiência exigido pela vaga.
- Compatibilidade da pretensão salarial do candidato com o orçamento disponível.

Só os candidatos aprovados nessa etapa avançam para a análise generativa. Isso evita gastar processamento com perfis que já não atendem aos requisitos mínimos.

**3. Camada generativa**
Para os candidatos aprovados, o sistema envia o currículo para um LLM rodando localmente através do [Ollama](https://ollama.com), que gera:
- Um parecer sobre a senioridade e as soft skills implícitas no currículo.
- Um resumo executivo do perfil, pronto para ser enviado ao recrutador.

Cada execução dessa etapa é acompanhada de um relatório de consumo de tokens, contando os tokens de entrada (prompt) e de saída (completion) com a biblioteca `tiktoken`, além de uma estimativa de custo equivalente caso fosse usada uma API paga.

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
- [Ollama](https://ollama.com) instalado e rodando na máquina
- Modelo `llama3.2` baixado no Ollama
- Dependências listadas em `requirements.txt`

## Instalação

```bash
git clone <link-do-repositorio>
cd vaga-tech-triagem
pip install -r requirements.txt
ollama pull llama3.2
```

## Execução

Com o Ollama rodando em segundo plano, execute:

```bash
python src/main.py
```

Caso o arquivo `curriculos/curriculo_teste.pdf` não seja encontrado, o sistema utiliza automaticamente um currículo de exemplo, garantindo que a demonstração funcione mesmo sem um PDF real disponível.

## Por que Ollama em vez de uma API paga?

O projeto usa um modelo rodando localmente em vez de uma API como OpenAI ou Anthropic por três motivos:
- Não exige chave de API nem cadastro de cartão de crédito.
- Elimina o risco de expor credenciais no repositório público do GitHub.
- Continua atendendo ao requisito do enunciado de "interagir com um LLM", já que o modelo é uma IA generativa real, apenas executada localmente em vez de na nuvem.

## Exemplo de saída

```
Checando os requisitos da vaga...
Precisa de pelo menos 3 anos de experiência e orçamento até R$ 10000
Anos de experiência encontrados: 5 (precisa de 3)
Pretensão salarial encontrada: R$ 8000.00 (orçamento é R$ 10000)
Candidato aprovado! Mandando para a IA analisar...

Resultado da análise:
**Resumo Executivo do Candidato:**
Rafael Andrade Souza é um desenvolvedor backend experiente com 5 anos de experiência em Python...

**Parecer sobre a Senioridade do Candidato:**
Com base no currículo apresentado, é possível concluir que Rafael Andrade Souza está em uma fase de transição para a senioridade...

----- RESUMO DE TOKENS -----
Tokens que entraram: 343
Tokens que saíram: 407
Total: 750
Custo estimado (se fosse API paga): $0.000296
-----------------------------
```

## Tecnologias utilizadas

- Python
- pypdf
- tiktoken
- Ollama (modelo llama3.2)
- Git e GitHub

## Equipe

Consulte o arquivo `integrantes.txt` para a lista completa de integrantes, RMs e o link do repositório.