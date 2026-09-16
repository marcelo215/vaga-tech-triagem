import os
import re
import pypdf
import tiktoken

MODO_SIMULADO_IA = True


def extrair_texto_pdf(caminho_pdf):
    """Extrai o texto bruto de um currículo em PDF."""
    if not os.path.exists(caminho_pdf):
        print(f" Aviso: arquivo '{caminho_pdf}' não encontrado. Usando currículo de exemplo.")
        return (
            "Candidato: João Silva.\n"
            "Experiência: 5 anos em Python.\n"
            "Pretensão Salarial: R$ 8000.\n"
        )

    texto_completo = ""
    with open(caminho_pdf, "rb") as arquivo:
        leitor = pypdf.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"
    return texto_completo


def extrair_anos_experiencia(texto_minusculo):
    """Procura um número seguido da palavra 'anos' no texto."""
    match = re.search(r"(\d+)\s*anos", texto_minusculo)
    return int(match.group(1)) if match else 0


def extrair_pretensao_salarial(texto_minusculo):
    """Procura um valor em R$ no texto (aceita formatos como 8000, 8.000, 8.000,00)."""
    match = re.search(r"r\$\s*([\d\.,]+)", texto_minusculo)
    if not match:
        return 0.0
    valor_str = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(valor_str)
    except ValueError:
        return 0.0


def avaliar_filtros_rigidos(texto, anos_minimos, salario_maximo):
    """Aplica as regras de negócio fixas ANTES de acionar a IA."""
    texto_minusculo = texto.lower()

    print("\n--- [Camada Determinística] Aplicando Filtros Rígidos ---")
    print(f"Buscando requisitos mínimos: {anos_minimos} anos de exp / Orçamento máximo: R$ {salario_maximo}")

    anos_candidato = extrair_anos_experiencia(texto_minusculo)
    salario_candidato = extrair_pretensao_salarial(texto_minusculo)

    filtro_experiencia_ok = anos_candidato >= anos_minimos
    filtro_salario_ok = salario_candidato <= salario_maximo

    status_exp = "APROVADO" if filtro_experiencia_ok else "REPROVADO"
    status_sal = "APROVADO" if filtro_salario_ok else "REPROVADO"

    print(f" Experiência encontrada: {anos_candidato} ano(s)  -> {status_exp}")
    print(f" Pretensão salarial encontrada: R$ {salario_candidato:.2f}  -> {status_sal}")

    return filtro_experiencia_ok and filtro_salario_ok


def _obter_codificador():
    try:
        return tiktoken.encoding_for_model("gpt-4o-mini")
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def _chamar_ia_simulada(prompt_sistema, prompt_usuario):
    """Resposta fixa, usada apenas para não depender de chave de API."""
    resposta_ia = (
        "### Resumo Executivo ###\n"
        "Profissional com sólida base técnica em Python, pronto para atuar em "
        "projetos de médio a alto nível de complexidade.\n\n"
        "### Parecer Qualitativo ###\n"
        "Senioridade estimada: Pleno. Boa comunicação implícita pela clareza "
        "na descrição das experiências."
    )
    return resposta_ia


def _chamar_ia_real(prompt_sistema, prompt_usuario):
    """Chamada real a um LLM (Anthropic). Requer 'pip install anthropic'
    e a variável de ambiente ANTHROPIC_API_KEY configurada."""
    import anthropic

    client = anthropic.Anthropic()
    resposta = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=prompt_sistema,
        messages=[{"role": "user", "content": prompt_usuario}],
    )
    return resposta.content[0].text


def analisar_com_ia_e_contar_tokens(texto_curriculo):
    """Gera parecer qualitativo + resumo executivo e conta tokens de entrada/saída."""
    prompt_sistema = "Você é um recrutador técnico especialista em tecnologia."
    prompt_usuario = (
        f"Currículo:\n{texto_curriculo}\n\n"
        "Gere um ### Resumo Executivo ### customizado do perfil do candidato "
        "e um ### Parecer Qualitativo ### sobre senioridade e soft skills implícitas."
    )

    codificador = _obter_codificador()
    tokens_entrada = len(codificador.encode(prompt_sistema + prompt_usuario))

    if MODO_SIMULADO_IA:
        resposta_ia = _chamar_ia_simulada(prompt_sistema, prompt_usuario)
    else:
        resposta_ia = _chamar_ia_real(prompt_sistema, prompt_usuario)

    tokens_saida = len(codificador.encode(resposta_ia))
    return resposta_ia, tokens_entrada, tokens_saida


def exibir_relatorio_custos(t_entrada, t_saida):
    # Preços de exemplo (por 1000 tokens), estilo gpt-4o-mini
    custo_total = ((t_entrada / 1000) * 0.00015) + ((t_saida / 1000) * 0.0006)

    print("\n=============================================")
    print("      RELATÓRIO DE CONSUMO DE TOKENS         ")
    print("=============================================")
    print(f"Tokens de Entrada (Prompt):    {t_entrada}")
    print(f"Tokens de Saída (Completion):  {t_saida}")
    print(f"Total de Tokens Utilizados:    {t_entrada + t_saida}")
    print(f"Estimativa de Custo Total:     ${custo_total:.6f} USD")
    print("=============================================\n")


if __name__ == "__main__":
    caminho_curriculo = "curriculos/curriculo_teste.pdf"
    anos_minimos_vaga = 3
    salario_maximo_vaga = 10000

    texto_extraido = extrair_texto_pdf(caminho_curriculo)

    if avaliar_filtros_rigidos(texto_extraido, anos_minimos_vaga, salario_maximo_vaga):
        print(" Candidato APROVADO nos filtros iniciais. Enviando para IA...")

        resultado_ia, tok_in, tok_out = analisar_com_ia_e_contar_tokens(texto_extraido)

        print("\n--- [Camada Generativa] Resultado da Análise ---")
        print(resultado_ia)

        exibir_relatorio_custos(tok_in, tok_out)
    else:
        print(" Candidato REPROVADO nos filtros rígidos. Triagem encerrada sem custo de IA.")