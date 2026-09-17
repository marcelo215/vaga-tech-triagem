import os
import re
import requests
import pypdf
import tiktoken

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODELO_IA = "llama3.2"


def ler_curriculo(caminho):
    # se o arquivo não existir, usa um texto de exemplo só pra não travar o teste
    if not os.path.exists(caminho):
        print(f"Não achei o arquivo '{caminho}', vou usar um currículo de exemplo.")
        return "Candidato: João Silva. Experiência: 5 anos em Python. Pretensão Salarial: R$ 8000."

    texto = ""
    with open(caminho, "rb") as arquivo:
        leitor = pypdf.PdfReader(arquivo)
        for pagina in leitor.pages:
            pedaco = pagina.extract_text()
            if pedaco:
                texto += pedaco + "\n"
    return texto



def perguntar_para_ia(texto_curriculo, anos_minimos=0, orcamento_max=0):
    """Envia o texto do currículo para o Ollama rodando o Llama 3.2 e pede uma análise baseada nas regras de negócio"""
    
    contexto_vaga = ""
    if anos_minimos > 0 or orcamento_max > 0:
        contexto_vaga = "--- REQUISITOS OBRIGATÓRIOS DA VAGA ---\n"
        if anos_minimos > 0:
            contexto_vaga += f"- Experiência Mínima Exigida: {anos_minimos} anos (você deve deduzir o tempo total de atuação profissional pelas datas).\n"
        if orcamento_max > 0:
            contexto_vaga += f"- Orçamento Máximo (Teto Salarial): R$ {orcamento_max:.2f}.\n"
        contexto_vaga += "ATENÇÃO: Se o candidato tiver menos experiência que o mínimo, ou pedir um salário maior que o teto, ele deve receber uma nota BAIXA (abaixo de 60) e você deve focar sua análise em explicar o motivo da reprovação.\n---------------------------------------\n\n"

    pergunta = (
        f"Você é um Tech Recruiter Sênior avaliando um currículo para vagas de Engenharia de Software e Tecnologia.\n\n"
        f"{contexto_vaga}"
        f"--- CURRÍCULO DO CANDIDATO ---\n{texto_curriculo}\n-------------------------------\n\n"
        "Sua missão é realizar uma análise técnica profunda e criteriosa. Você deve retornar sua avaliação "
        "seguindo EXATAMENTE a estrutura abaixo, sem inventar outros formatos:\n\n"
        "### Resumo Executivo\n"
        "[Seu texto...]\n\n"
        "### Stack Tecnológico\n"
        "[Seu texto...]\n\n"
        "### Análise de Senioridade\n"
        "[Seu texto...]\n\n"
        "### Pontos Fortes/De Atenção\n"
        "[Seu texto...]\n\n"
        "<SCORE>0</SCORE>\n"
        "(O '0' dentro da tag SCORE é apenas um exemplo. Substitua pela sua nota final da avaliação.)\n\n"
        "REGRAS PARA O 'score':\n"
        "- Deve ser APENAS um número inteiro de 0 a 100.\n"
        "- Notas acima de 80: Candidatos excepcionais que atendem todos os requisitos.\n"
        "- Notas entre 60 e 79: Candidatos bons, mas com pontos de atenção.\n"
        "- Notas abaixo de 60: Perfis imaturos, currículos fracos, ou que violam os Requisitos Obrigatórios da Vaga (falta de experiência ou salário incompatível)."
    )

    # manda a pergunta pro Ollama (sem forçar JSON, deixando ele usar as XML Tags naturalmente)
    resposta_http = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO_IA,
            "messages": [{"role": "user", "content": pergunta}],
            "stream": False,
        },
        timeout=120,
    )
    resposta_http.raise_for_status()
    resposta = resposta_http.json()["message"]["content"]

    # o tiktoken é só pra contar quantos "pedaços de palavra" (tokens) tem no texto
    try:
        contador = tiktoken.encoding_for_model("gpt-4o-mini")
    except Exception:
        contador = tiktoken.get_encoding("cl100k_base")

    tokens_de_entrada = len(contador.encode(pergunta))
    tokens_de_saida = len(contador.encode(resposta))

    return resposta, tokens_de_entrada, tokens_de_saida


if __name__ == "__main__":
    import sys

    C_AZUL = '\033[94m'
    C_VERDE = '\033[92m'
    C_AMARELO = '\033[93m'
    C_VERMELHO = '\033[91m'
    C_NEGRITO = '\033[1m'
    C_RESET = '\033[0m'

    print(f"{C_AZUL}{C_NEGRITO}      SISTEMA DE TRIAGEM DE CURRÍCULOS              {C_RESET}\n")

    caminho_do_pdf = "curriculos/curriculo_teste.pdf"
    
    # Coleta de Parâmetros de Negócio
    print(f"{C_AMARELO}Configuração dos Filtros da Vaga:{C_RESET}")
    
    anos_minimos = 0
    while True:
        try:
            inp = input("Anos mínimos de experiência exigidos. [0 para pular]: ")
            anos_minimos = int(inp) if inp.strip() != "" else 0
            break
        except ValueError:
            print(f"{C_VERMELHO}Erro: Por favor, digite apenas um número inteiro.{C_RESET}")
            
    orcamento_max = 0.0
    while True:
        try:
            inp = input("Teto salarial máximo. [0 para pular]: ")
            orcamento_max = float(inp) if inp.strip() != "" else 0.0
            break
        except ValueError:
            print(f"{C_VERMELHO}Erro: Por favor, digite um número válido (use ponto para decimais).{C_RESET}")

    print(f"\n{C_AMARELO}[1/2] Lendo o currículo...{C_RESET}")
    texto = ler_curriculo(caminho_do_pdf)

    print(f"{C_AMARELO}[2/2] Pensando...{C_RESET}")
    
    try:
        resposta_ia, tokens_in, tokens_out = perguntar_para_ia(texto, anos_minimos, orcamento_max)
        
        print(f"\n{C_VERDE}{C_NEGRITO}RESULTADO DA AVALIAÇÃO{C_RESET}")
        print(f"\n{resposta_ia}\n")
        
        print(f"{C_AZUL}{C_NEGRITO}ESTATÍSTICAS DE CONSUMO{C_RESET}")
        custo = (tokens_in / 1000 * 0.00015) + (tokens_out / 1000 * 0.0006)
        print(f"Tokens Entrada: {tokens_in}")
        print(f"Tokens Saída:   {tokens_out}")
        print(f"Custo Estimado: ${custo:.6f}")
        
    except Exception as e:
        print(f"\n{C_VERMELHO}Erro: {e}{C_RESET}")