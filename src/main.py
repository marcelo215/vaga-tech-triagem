import os
import re
import requests
import pypdf
import tiktoken

# endereço do Ollama rodando na própria máquina
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO_IA = "llama3.2"


def ler_curriculo(caminho):
    # se o arquivo não existir, usa um texto de exemplo só pra não travar o teste
    if not os.path.exists(caminho):
        print(f"Não achei o arquivo '{caminho}', vou usar um currículo de exemplo.")
        return "Candidato: João Silva. Experiência: 5 anos em Python. Pretensão Salarial: R$ 8000."

    texto = ""
    arquivo = open(caminho, "rb")
    leitor = pypdf.PdfReader(arquivo)
    for pagina in leitor.pages:
        pedaco = pagina.extract_text()
        if pedaco:
            texto += pedaco + "\n"
    arquivo.close()
    return texto


def passou_nos_filtros(texto, anos_minimos, salario_maximo):
    texto = texto.lower()

    print("\nChecando os requisitos da vaga...")
    print(f"Precisa de pelo menos {anos_minimos} anos de experiência e orçamento até R$ {salario_maximo}")

    # tenta achar quantos anos de experiência tem no texto
    achou_anos = re.search(r"(\d+)\s*anos", texto)
    anos = int(achou_anos.group(1)) if achou_anos else 0

    # tenta achar a pretensão salarial
    achou_salario = re.search(r"r\$\s*([\d\.,]+)", texto)
    if achou_salario:
        salario = achou_salario.group(1).replace(".", "").replace(",", ".")
        salario = float(salario)
    else:
        salario = 0

    tem_experiencia_suficiente = anos >= anos_minimos
    salario_cabe_no_orcamento = salario <= salario_maximo

    print(f"Anos de experiência encontrados: {anos} (precisa de {anos_minimos})")
    print(f"Pretensão salarial encontrada: R$ {salario:.2f} (orçamento é R$ {salario_maximo})")

    return tem_experiencia_suficiente and salario_cabe_no_orcamento


def perguntar_para_ia(texto_curriculo):
    pergunta = (
        f"Você é um recrutador técnico. Aqui está o currículo:\n{texto_curriculo}\n\n"
        "Escreva um resumo executivo do candidato e um parecer sobre a senioridade dele."
    )

    # manda a pergunta pro Ollama, que precisa estar rodando na máquina
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


def mostrar_custo(tokens_entrada, tokens_saida):
    # como o Ollama roda local, não tem custo de verdade, mas deixamos a estimativa
    # no mesmo padrão de preço de mercado só pra fins de comparação (por 1000 tokens)
    custo = (tokens_entrada / 1000 * 0.00015) + (tokens_saida / 1000 * 0.0006)

    print("\n----- RESUMO DE TOKENS -----")
    print(f"Tokens que entraram: {tokens_entrada}")
    print(f"Tokens que saíram: {tokens_saida}")
    print(f"Total: {tokens_entrada + tokens_saida}")
    print(f"Custo estimado (se fosse API paga): ${custo:.6f}")
    print("-----------------------------\n")


# aqui começa o programa de verdade
caminho_do_pdf = "curriculos/curriculo_teste.pdf"
anos_minimos_da_vaga = 3
orcamento_da_vaga = 10000

texto = ler_curriculo(caminho_do_pdf)

if passou_nos_filtros(texto, anos_minimos_da_vaga, orcamento_da_vaga):
    print("Candidato aprovado! Mandando para a IA analisar...")

    try:
        resposta_ia, tokens_in, tokens_out = perguntar_para_ia(texto)
        print("\nResultado da análise:")
        print(resposta_ia)
        mostrar_custo(tokens_in, tokens_out)
    except requests.exceptions.ConnectionError:
        print(
            "\nNão consegui falar com o Ollama. Confirme se ele está instalado e "
            "rodando (abra http://localhost:11434 no navegador pra checar)."
        )
else:
    print("Candidato não passou nos filtros. Nem vamos gastar com a IA.")