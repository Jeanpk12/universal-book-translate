from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from groq import Groq
import PyPDF2

app = Flask(__name__)

# Configuração do diretório de upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extrair_texto_pdf(arquivo_pdf, numero_pagina):
    """
    Extrai o texto de uma página específica de um arquivo PDF.

    :param arquivo_pdf: Caminho para o arquivo PDF.
    :param numero_pagina: Número da página a ser extraída (baseado em 1).
    :return: Texto extraído da página ou uma mensagem de erro se a página for inválida.
    """
    try:
        with open(arquivo_pdf, 'rb') as pdf_file:
            leitor = PyPDF2.PdfReader(pdf_file)
            if 0 < numero_pagina <= len(leitor.pages):
                pagina = leitor.pages[numero_pagina - 1]
                return pagina.extract_text()
            else:
                return "Página inválida"
    except Exception as e:
        return f"Erro ao abrir o PDF: {str(e)}"

def formatar_texto_para_html(texto):
    """
    Formata o texto para HTML, separando parágrafos por tags <p>.

    :param texto: Texto a ser formatado.
    :return: Texto formatado em HTML.
    """
    paragrafos = texto.split('\n\n')
    texto_formatado = ''.join(f'<p>{paragrafo.strip()}</p>' for paragrafo in paragrafos if paragrafo.strip())
    return texto_formatado

def traduzir_texto_groq(texto_extraido):
    """
    Traduz o texto extraído utilizando a API Groq e formata o resultado para HTML.

    :param texto_extraido: Texto extraído do PDF.
    :return: Texto traduzido e formatado em HTML.
    """
    prompt = 'Traduza o seguinte texto para português brasileiro de modo que as frases fiquem coerentes e sejam facilmente entendidas. Faça as adaptações necessárias: '
    
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f'{prompt} {texto_extraido}. Retorne apenas a tradução sem nenhum comentário adicional.',
                }
            ],
            model="llama-3.1-70b-versatile",
        )
        texto_traduzido = chat_completion.choices[0].message.content
        return formatar_texto_para_html(texto_traduzido)
    except Exception as e:
        return f"Erro ao traduzir o texto: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Rota principal que processa o upload do PDF e renderiza o resultado da tradução.

    :return: Template renderizado.
    """
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return 'Nenhum arquivo enviado ou selecionado.'

        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            numero_pagina = int(request.form['page_number'])
        except ValueError:
            return 'Número de página inválido.'

        texto_extraido = extrair_texto_pdf(filepath, numero_pagina)
        texto_traduzido = traduzir_texto_groq(texto_extraido)

        return render_template('result.html', traducao=texto_traduzido, pagina=numero_pagina, caminho_pdf=filepath)

    return render_template('index.html')

@app.route('/pagina', methods=['POST'])
def pagina():
    """
    Rota para navegação entre as páginas do PDF, extraindo e traduzindo o texto conforme solicitado.

    :return: Template renderizado com a tradução da página atualizada.
    """
    try:
        numero_pagina = int(request.form['page_number'])
        caminho_pdf = request.form['filepath']
        acao = request.form['action']

        if acao == 'next':
            numero_pagina += 1
        elif acao == 'previous' and numero_pagina > 1:
            numero_pagina -= 1

        texto_extraido = extrair_texto_pdf(caminho_pdf, numero_pagina)
        texto_traduzido = traduzir_texto_groq(texto_extraido)

        return render_template('result.html', traducao=texto_traduzido, pagina=numero_pagina, caminho_pdf=caminho_pdf)

    except ValueError:
        return 'Número de página inválido.'
    except KeyError:
        return 'Erro nos dados fornecidos.'
    except Exception as e:
        return f"Erro ao processar a página: {str(e)}"

if __name__ == '__main__':
    # Configuração do modo de debug para desenvolvimento
    app.run(debug=True)
