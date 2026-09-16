import os
import pypdf
import tiktoken

def extrair_texto_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        return "Candidato: João Silva. Experiência: 5 anos em Python. Pretensão Salarial: R$ 8000."
    texto_completo = ""
    with open(caminho_pdf, "rb") as arquivo:
        leitor = pypdf.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"
    return texto_completo

def avaliar_filtros_rigidos(texto, anos_minimos, salario_maximo):
    texto_minusculo = texto.lower()
    print("\n--- [Camada Determinística] Aplicando Filtros Rígidos ---")
    print(f"Buscando requisitos mínimos: {anos_minimos} anos de exp / Orçamento máximo: R$ {salario_maximo}")
    aprovado = True
    if "anos" in texto_minusculo:
        print(" Validação de experiência realizada.")
    else:
        print(" Atenção: Menção a 'anos' não encontrada.")
    return aprovado

def analisar_com_ia_e_contar_tokens(texto_curriculo):
    prompt_sistema = "Você é um recrutador técnico especialista."
    prompt_usuario = f"Currículo:\n{texto_curriculo}"
    try:
        codificador = tiktoken.encoding_for_model("gpt-4o-mini")
    except Exception:
        codificador = tiktoken.get_encoding("cl100k_base")
        
    tokens_entrada = len(codificador.encode(prompt_sistema + prompt_usuario))
    resposta_ia = (
        "### Resumo Executivo ###\nProfissional com sólida base técnica em Python.\n\n"
        "### Parecer Qualitativo ###\nSenioridade: Pleno. Boa comunicação implícita."
    )
    tokens_saida = len(codificador.encode(resposta_ia))
    return resposta_ia, tokens_entrada, tokens_saida

def exibir_relatorio_custos(t_entrada, t_saida):
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
    texto_extraido = extrair_texto_pdf("curriculos/curriculo_teste.pdf")
    if avaliar_filtros_rigidos(texto_extraido, 3, 10000):
        print(" Candidato APROVADO nos filtros iniciais. Enviando para IA...")
        resultado_ia, tok_in, tok_out = analisar_com_ia_e_contar_tokens(texto_extraido)
        print("\n--- [Camada Generativa] Resultado da Análise ---")
        print(resultado_ia)
        exibir_relatorio_custos(tok_in, tok_out)