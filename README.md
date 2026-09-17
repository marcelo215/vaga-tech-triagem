<h1 align="center">
  Triagem Inteligente de Currículos
</h1>
<p align="center">Automação de recrutamento tech utilizando regras determinísticas e Inteligência Artificial generativa.</p>
<p align="center">
  <a href="https://github.com/marcelo215/vaga-tech-triagem"><img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" /></a>&nbsp;
  <a href="https://github.com/marcelo215/vaga-tech-triagem"><img alt="Ollama" src="https://img.shields.io/badge/Ollama-Local_LLM-000000?style=flat&logo=ollama&logoColor=white" /></a>&nbsp;
  <a href="https://github.com/marcelo215/vaga-tech-triagem"><img alt="Docker" src="https://img.shields.io/badge/Docker-Support-2496ED?style=flat&logo=docker&logoColor=white" /></a>
</p>

---

### Sobre

Este sistema atua como um funil inteligente para otimizar o fluxo de triagem de currículos de uma agência de empregos focada no ecossistema de tecnologia. A triagem e o julgamento dos requisitos de negócio (tempo de experiência e orçamento da vaga) são avaliados diretamente por Inteligência Artificial.

*Desenvolvido como Checkpoint 1 da disciplina de IA & ML, sob orientação do professor Wellington Cidade Silva.*

**Arquitetura e Fluxo de Funcionamento:**

1. **Camada de Ingestão (OCR/Texto):** Extrai o conteúdo bruto de currículos em formato PDF utilizando a biblioteca `pypdf`.
2. **Camada Generativa (LLM Local):** O texto extraído, em conjunto com as regras de negócio inseridas dinamicamente pelo recrutador (anos mínimos exigidos e teto salarial), é submetido a um modelo **Llama 3.2** rodando localmente via Ollama. 
3. **Parsing e Extração de Tags (Regex):** O frontend ou a CLI processa o Markdown e as *XML Tags* (como `<SCORE>`) retornados pela IA, abstraindo falhas comuns do LLM e gerando um relatório limpo e estruturado.

O uso de uma solução local (Ollama) garante privacidade de dados sensíveis, elimina a necessidade de chaves de API pagas e atende ao requisito de interação com IA generativa estabelecido no projeto.

---

### Quick Start

Há três formas de executar o projeto. Escolha a que melhor se adapta ao seu ambiente:

<details>
<summary><strong>Opção 1: Via Docker Compose (Mais rápido)</strong></summary>

```bash
# Clone o repositório
git clone https://github.com/marcelo215/vaga-tech-triagem.git
cd vaga-tech-triagem

# Suba os containers
docker compose up --build

# Abra no navegador:
# http://localhost:5000
```

</details>

<details>
<summary><strong>Opção 2: Nativamente (Python + Ollama)</strong></summary>

```bash
# Clone o repositório
git clone https://github.com/marcelo215/vaga-tech-triagem.git
cd vaga-tech-triagem

# Instale as dependências
pip install -r requirements.txt

# Baixe o modelo do Ollama
ollama pull llama3.2

# Inicie a interface web
python src/web.py

# Opcional: Se preferir rodar no terminal sem interface, use:
# python src/main.py
```
</details>

<details>
<summary><strong>Opção 3: Híbrido (Container Python + Ollama no Host)</strong></summary>

```bash
# Clone o repositório e construa a imagem do app
git clone https://github.com/marcelo215/vaga-tech-triagem.git
cd vaga-tech-triagem
docker build -t vaga-tech-triagem .

# Rode o container acessando a rede (e o Ollama) do host
docker run -p 5000:5000 --network host vaga-tech-triagem

# Abra no navegador:
# http://localhost:5000
```
</details>

> [!IMPORTANT]
> A 1° opção não oferece aceleração via GPU, somente CPU.

---

### Interface Web

Para utilizar a interface gráfica e interagir com o sistema pelo navegador, basta rodar o servidor Flask localmente e acessar a porta 5000:

```bash
python src/web.py
```
Em seguida, abra `http://localhost:5000` no seu navegador.

---

### Exemplo de Saída (CLI)

```text
      SISTEMA DE TRIAGEM DE CURRÍCULOS              

Configuração dos Filtros da Vaga:
Anos mínimos de experiência exigidos. [0 para pular]: 3
Teto salarial máximo. [0 para pular]: 10000

[1/2] Lendo o currículo...
[2/2] Pensando...

RESULTADO DA AVALIAÇÃO

### Resumo Executivo
Rafael Andrade Souza é um desenvolvedor backend com forte viés para...

### Stack Tecnológico
- Python, FastAPI, Flask, SQL, Git, Docker, APIs REST

### Análise de Senioridade
O candidato consolida um perfil Pleno...

<SCORE>72</SCORE>

ESTATÍSTICAS DE CONSUMO
Tokens Entrada: 382
Tokens Saída:   215
Custo Estimado: $0.000186
```

---

### Equipe

| Nome | GitHub | LinkedIn |
| --- | --- | --- |
| **Gabriel Couto Ribeiro** | [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/rouri404) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabricouto/) |
| **Gabriel Kato Peres** | [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/kato8088) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabrikato/) |
| **João Vitor de Matos** | [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/joaomatosq) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joaomatosq/) |
| **Marcelo Affonso Fonseca** | [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/marcelo215) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/marcelo-affonso-fonseca-899682333/) |
