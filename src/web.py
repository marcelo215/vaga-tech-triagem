import json
import pypdf
import requests
import markdown
from flask import Flask, request, render_template_string

# Importa as funções originais do seu main.py
from main import passou_nos_filtros, perguntar_para_ia, OLLAMA_URL

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Análise de Currículo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
    <style>
        :root, [data-theme="light"] {
            --bg: #F9FAFB;
            --surface: #FFFFFF;
            --surface-soft: #F3F4F6;
            --ink: #111827;
            --ink-muted: #6B7280;
            --line: #E5E7EB;
            --accent: #2F6FE0;
            --accent-hover: #2558B8;
            --accent-soft: #E3ECFC;
            --error: #DC2626;
        }
        
        [data-theme="dark"] {
            --bg: #121316;
            --surface: #1B1D21;
            --surface-soft: #202226;
            --ink: #ECEDEE;
            --ink-muted: #9A9CA3;
            --line: #2E3136;
            --accent: #3F7FE0;
            --accent-hover: #5B95F0;
            --accent-soft: #1E2A40;
            --error: #E2695A;
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--ink);
            transition: background-color 0.3s, color 0.3s;
        }
        .page { max-width: 640px; margin: 0 auto; padding: 64px 24px 96px; position: relative; }
        
        /* Botão de Tema */
        .theme-toggle {
            position: fixed;
            top: 24px;
            right: 24px;
            background: transparent;
            border: none;
            color: var(--ink-muted);
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: color 0.2s, background 0.2s;
        }
        .theme-toggle:hover { color: var(--ink); background: var(--surface-soft); }
        .theme-toggle svg { width: 22px; height: 22px; }

        [data-theme="dark"] .icon-moon { display: none; }
        [data-theme="light"] .icon-sun { display: none; }

        .page-header { margin-bottom: 40px; }
        h1 { font-family: 'Source Serif 4', Georgia, serif; font-size: 32px; font-weight: 600; line-height: 1.2; margin: 0 0 12px; letter-spacing: -0.01em; }
        .subtitle { font-size: 15px; color: var(--ink-muted); line-height: 1.6; max-width: 46ch; margin: 0; }
        
        .card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 32px; box-shadow: 0 1px 2px rgba(33,32,27,0.04), 0 8px 24px rgba(33,32,27,0.04); transition: background-color 0.3s, border-color 0.3s; }
        .field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .field { margin-bottom: 22px; }
        .field label { display: block; font-size: 13px; font-weight: 500; color: var(--ink); margin-bottom: 8px; }
        
        input[type="number"] { width: 100%; padding: 11px 14px; border: 1px solid var(--line); border-radius: 8px; font-size: 15px; font-family: inherit; color: var(--ink); background: var(--surface-soft); transition: border-color .15s, box-shadow .15s, background-color 0.3s, color 0.3s; }
        input[type="number"]:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
        
        .dropzone { position: relative; border: 1.5px dashed var(--line); border-radius: 10px; padding: 28px 16px; text-align: center; background: var(--surface-soft); transition: border-color .15s, background-color 0.3s; }
        .dropzone:has(input:focus) { border-color: var(--accent); }
        .dropzone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
        .dropzone-icon { display: block; margin: 0 auto 10px; width: 22px; height: 22px; color: var(--ink-muted); }
        .dropzone-text { font-size: 13.5px; color: var(--ink-muted); }
        .dropzone.has-file { border-style: solid; border-color: var(--accent); }
        .dropzone.has-file .dropzone-text { color: var(--ink); font-weight: 500; }
        
        button[type="submit"] { position: relative; display: flex; align-items: center; justify-content: center; width: 100%; margin-top: 6px; padding: 13px; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-size: 15px; font-weight: 500; font-family: inherit; cursor: pointer; transition: background .15s, opacity .15s; }
        button[type="submit"]:hover { background: var(--accent-hover); }
        button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
        button[type="submit"].loading { pointer-events: none; opacity: 0.9; }
        
        .btn-text-wrapper { position: relative; display: inline-flex; align-items: center; justify-content: center; }
        .spinner { position: absolute; right: 100%; margin-right: 8px; width: 18px; height: 18px; opacity: 0; visibility: hidden; transition: opacity 0.2s; animation: spin 1s linear infinite; }
        button[type="submit"].loading .spinner { opacity: 1; visibility: visible; }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
        
        .notice { margin-top: 24px; padding: 16px 18px; border-left: 3px solid var(--error); background: var(--surface); border-radius: 0 8px 8px 0; transition: background-color 0.3s; }
        .notice p { margin: 0; font-size: 14px; line-height: 1.6; }
        
        .result { margin-top: 40px; }
        .result-score { margin-bottom: 28px; }
        .result-score-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
        .result-score-label { font-size: 13px; color: var(--ink-muted); }
        .result-score-value { font-family: 'Source Serif 4', Georgia, serif; font-size: 28px; font-weight: 600; }
        .result-score-max { font-size: 14px; font-weight: 400; color: var(--ink-muted); margin-left: 2px; }
        .result-score-bar { height: 6px; border-radius: 999px; background: var(--line); overflow: hidden; }
        .result-score-fill { height: 100%; background: var(--accent); border-radius: 999px; transition: width 1s ease-out; }
        
        .result-content { font-size: 15.5px; line-height: 1.75; }
        .result-content p { margin: 0 0 1em; }
        .result-content strong { font-weight: 600; }
        .result-content ul { padding-left: 20px; margin: 0 0 1em; }
        .result-content li { margin-bottom: 6px; }
        .result-content h1, .result-content h2, .result-content h3 { font-family: 'Source Serif 4', Georgia, serif; font-size: 17px; margin: 1.4em 0 .5em; }
        
        .status-badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-left: 12px; vertical-align: middle; }
        .status-aprovado { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
        .status-reprovado { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }

        .result-meta { margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--line); font-size: 12.5px; color: var(--ink-muted); }
        
        @media (max-width: 640px) {
            .page { padding: 40px 20px 64px; }
            .field-row { grid-template-columns: 1fr; gap: 0; }
            .card { padding: 24px; }
            .theme-toggle { top: 12px; right: 12px; }
        }
        @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
    </style>
</head>
<body>
    <main class="page">
        <!-- Botão Toggle de Tema -->
        <button id="theme-toggle" class="theme-toggle" aria-label="Mudar tema">
            <!-- Ícone Sol (Aparece no tema Dark) -->
            <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
        </button>

        <header class="page-header">
            <h1>Análise de Currículo</h1>
            <p class="subtitle">Envie um currículo em PDF e receba uma leitura objetiva do perfil.</p>
        </header>

        <section class="card">
            <form method="POST" enctype="multipart/form-data">
                <div class="field-row">
                    <div class="field">
                        <label for="anos_minimos">Experiência mínima (anos)</label>
                        <input type="number" id="anos_minimos" name="anos_minimos" value="3" min="0" required>
                    </div>
                    <div class="field">
                        <label for="orcamento_max">Teto salarial (R$)</label>
                        <input type="number" id="orcamento_max" name="orcamento_max" value="10000" min="0" required>
                    </div>
                </div>

                <div class="field">
                    <label for="pdf_file">Currículo em PDF</label>
                    <div class="dropzone" id="dropzone">
                        <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required>
                        <svg class="dropzone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M13 2v6h6"/></svg>
                        <span class="dropzone-text" id="dropzone-text">Arraste o arquivo ou clique para selecionar</span>
                    </div>
                </div>

                <button type="submit" id="submit-btn">
                    <span class="btn-text-wrapper">
                        <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                        </svg>
                        <span id="submit-text">Analisar currículo</span>
                    </span>
                </button>
            </form>
        </section>

        {% if erro %}
        <div class="notice">
            {{ erro | safe }}
        </div>
        {% endif %}

        {% if resultado_html or status_triagem %}
        <section class="result">
            {% if score_num is not none %}
            <div class="result-score">
                <div class="result-score-top">
                    <div>
                        <span class="result-score-label">Nota de aderência</span>
                        {% if status_triagem %}
                        <span class="status-badge {{ 'status-aprovado' if status_triagem == 'APROVADO' else 'status-reprovado' }}">{{ status_triagem }}</span>
                        {% endif %}
                    </div>
                    <span class="result-score-value">{{ score_num }}<span class="result-score-max">/100</span></span>
                </div>
                <div class="result-score-bar"><div class="result-score-fill" style="width: {{ score_num }}%;"></div></div>
            </div>
            {% elif score %}
            <div class="result-score">
                <div class="result-score-top">
                    <div>
                        <span class="result-score-label">Nota de aderência</span>
                        {% if status_triagem %}
                        <span class="status-badge {{ 'status-aprovado' if status_triagem == 'APROVADO' else 'status-reprovado' }}">{{ status_triagem }}</span>
                        {% endif %}
                    </div>
                    <span class="result-score-value">{{ score }}</span>
                </div>
            </div>
            {% elif status_triagem %}
            <div class="result-score" style="margin-bottom: 20px;">
                <span class="status-badge {{ 'status-aprovado' if status_triagem == 'APROVADO' else 'status-reprovado' }}" style="margin-left: 0;">STATUS: {{ status_triagem }}</span>
            </div>
            {% endif %}

            <div class="result-content">
                {{ resultado_html | safe }}
            </div>

            {% if custo %}
            <p class="result-meta">
                Análise gerada por Inteligência Artificial. Tokens: {{ tokens_in }} (in) / {{ tokens_out }} (out) &bull; Custo estimado: {{ custo }}
            </p>
            {% endif %}

            <div style="margin-top: 32px; text-align: center;">
                <a href="/" style="display: inline-block; padding: 10px 24px; background: var(--surface-soft); color: var(--ink); text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 500; border: 1px solid var(--line); transition: background 0.2s;">Realizar Nova Análise</a>
            </div>
        </section>
        {% endif %}
    </main>

    <script>
        // Lógica do Drag and Drop (Nome do arquivo)
        document.querySelectorAll('.dropzone input[type="file"]').forEach(function (input) {
            input.addEventListener('change', function () {
                var zone = input.closest('.dropzone');
                var text = zone.querySelector('.dropzone-text');
                if (input.files && input.files.length > 0) {
                    text.textContent = input.files[0].name;
                    zone.classList.add('has-file');
                } else {
                    text.textContent = 'Arraste o arquivo ou clique para selecionar';
                    zone.classList.remove('has-file');
                }
            });
        });

        // Lógica do botão Toggle Theme
        const themeToggleBtn = document.getElementById('theme-toggle');
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // Lógica de Loading ao enviar o formulário
        const form = document.querySelector('form');
        const submitBtn = document.getElementById('submit-btn');
        const submitText = document.getElementById('submit-text');

        form.addEventListener('submit', function() {
            // Apenas aplica o loading se o formulário for válido (arquivos e inputs preenchidos)
            if (form.checkValidity()) {
                submitBtn.classList.add('loading');
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        anos_minimos = int(request.form.get("anos_minimos", 3))
        orcamento_max = float(request.form.get("orcamento_max", 10000))
        pdf_file = request.files.get("pdf_file")

        if not pdf_file or pdf_file.filename == '':
            return render_template_string(HTML_TEMPLATE, erro="Por favor, anexe um arquivo PDF válido.")

        # Leitura bruta do PDF
        texto_curriculo = ""
        try:
            leitor = pypdf.PdfReader(pdf_file)
            for pagina in leitor.pages:
                pedaco = pagina.extract_text()
                if pedaco:
                    texto_curriculo += pedaco + "\n"
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, erro="Ocorreu uma falha ao tentar ler o PDF.")

        # IA Generativa (Ollama) avalia o currículo, a senioridade e a pretensão salarial
        try:
            resposta_ia, tokens_in, tokens_out = perguntar_para_ia(texto_curriculo, anos_minimos, orcamento_max)
            
            # O Llama 3.2 performa muito melhor com XML Tags do que tentando montar JSON na raça.
            score_num = None
            score_text = None
            texto_limpo = resposta_ia
            
            import re
            # 1. Tenta pegar a nota de dentro das tags oficiais <SCORE>85</SCORE> (ignorando maiúsculas e espaços)
            match = re.search(r'<\s*SCORE\s*>\s*(\d+)\s*<\s*/\s*SCORE\s*>', resposta_ia, re.IGNORECASE)
            
            if match:
                score_num = max(0, min(100, int(match.group(1))))
                # Arranca a tag e qualquer coisa abaixo dela para não poluir a tela
                texto_limpo = re.sub(r'<\s*SCORE\s*>.*', '', resposta_ia, flags=re.IGNORECASE | re.DOTALL).strip()
            else:
                # 2. Fallback: Se a IA ignorou a tag e só escreveu "Score: 85" ou "**Score**: 85"
                match_fallback = re.search(r'[*"\s]*score[*"\s:\-]*(\d+)', resposta_ia, re.IGNORECASE)
                if match_fallback:
                    score_num = max(0, min(100, int(match_fallback.group(1))))
                    texto_limpo = re.sub(r'[*"\s]*score[*"\s:\-]*\d+.*?$', '', resposta_ia, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL).strip()
                else:
                    # 3. Last Resort: Tenta achar um número isolado no final do texto
                    match_last = re.search(r'\b(\d{1,3})(?:/100)?\s*$', resposta_ia)
                    if match_last:
                        score_num = max(0, min(100, int(match_last.group(1))))
                        texto_limpo = re.sub(r'\b\d{1,3}(?:/100)?\s*$', '', resposta_ia).strip()
            
            texto_limpo = re.sub(r'\(.*exemplo.*\)', '', texto_limpo, flags=re.IGNORECASE).strip()
            texto_limpo = texto_limpo.rstrip('* \n')

            # Corrige listas inline e garante quebras de linha antes de listas (problema clássico do Llama)
            texto_limpo = re.sub(r'([a-zA-Z0-9.,;:!?])\s+-\s+([A-Za-z0-9])', r'\1\n- \2', texto_limpo)
            texto_limpo = re.sub(r'([^\n])\n([*-]\s)', r'\1\n\n\2', texto_limpo)
            
            # Remove caracteres "pipe" (|) soltos que o LLM às vezes alucina para tentar desenhar separadores
            texto_limpo = re.sub(r'^\s*\|\s*$', '', texto_limpo, flags=re.MULTILINE)

            # Converte o Markdown gerado pela IA para HTML, ativando suporte a quebras de linha duras e listas
            resultado_html = markdown.markdown(texto_limpo, extensions=['nl2br'])
            
            # Regra de negócio: Aprovado se nota for maior ou igual a 60
            status_final = "APROVADO" if score_num is not None and score_num >= 60 else "REPROVADO"

            custo = f"${(tokens_in / 1000 * 0.00015) + (tokens_out / 1000 * 0.0006):.6f}"
            return render_template_string(HTML_TEMPLATE, resultado_html=resultado_html, score=score_text, score_num=score_num, custo=custo, tokens_in=tokens_in, tokens_out=tokens_out, status_triagem=status_final)

        except requests.exceptions.ConnectionError:
            erro_msg = """
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 24px; height: 24px; color: var(--error); flex-shrink: 0;" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                    <h3 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 600; color: var(--error);">Conexão com a IA falhou</h3>
                    <p style="margin: 0 0 10px 0; font-size: 14.5px; color: var(--ink);">O servidor do <strong>Ollama</strong> não está respondendo. Para processar currículos com Inteligência Artificial, o motor local precisa estar rodando na sua máquina.</p>
                    <ul style="margin: 0; padding-left: 18px; font-size: 14px; color: var(--ink-muted);">
                        <li style="margin-bottom: 4px;">Abra seu terminal e digite <code style="background: var(--surface-soft); padding: 2px 6px; border-radius: 4px;">ollama serve</code> ou inicie o container.</li>
                        <li>Acesse <a href="http://localhost:11434" target="_blank" style="color: var(--accent); text-decoration: none;">http://localhost:11434</a> para checar se ele está ativo.</li>
                    </ul>
                </div>
            </div>
            """
            return render_template_string(HTML_TEMPLATE, erro=erro_msg)
        except requests.exceptions.HTTPError as e:
            detalhes = e.response.text if hasattr(e, 'response') else str(e)
            erro_msg = f"""
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 24px; height: 24px; color: var(--error); flex-shrink: 0;" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                    <h3 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 600; color: var(--error);">Erro Interno na IA (HTTP 500)</h3>
                    <p style="margin: 0 0 10px 0; font-size: 14.5px; color: var(--ink);">O serviço do Ollama travou enquanto processava os dados. Isso geralmente acontece por falta de memória (OOM) na máquina ou falha ao carregar o modelo <code>llama3.2</code>.</p>
                    <p style="margin: 0; font-size: 13px; color: var(--ink-muted); font-family: monospace;">Detalhes: {detalhes}</p>
                </div>
            </div>
            """
            return render_template_string(HTML_TEMPLATE, erro=erro_msg)
        except Exception as e:
            erro_msg = f"""
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 24px; height: 24px; color: var(--error); flex-shrink: 0;" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                    <h3 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 600; color: var(--error);">Erro Inesperado</h3>
                    <p style="margin: 0 0 10px 0; font-size: 14.5px; color: var(--ink);">Ocorreu uma falha grave na comunicação com a inteligência artificial.</p>
                    <p style="margin: 0; font-size: 13px; color: var(--ink-muted); font-family: monospace;">{str(e)}</p>
                </div>
            </div>
            """
            return render_template_string(HTML_TEMPLATE, erro=erro_msg)

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
