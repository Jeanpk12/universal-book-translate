# Universal Book Translator with Groq API

Este é um aplicativo Flask que permite o upload de arquivos PDF, extração e tradução de texto de páginas específicas utilizando a API Groq. O texto traduzido é exibido em HTML formatado e a aplicação suporta navegação entre as páginas do PDF.

## Funcionalidades

- Upload de arquivos PDF
- Extração de texto de páginas específicas do PDF
- Tradução do texto extraído para o português usando a API Groq
- Formatação do texto traduzido em HTML
- Navegação entre páginas do PDF com visualização dinâmica das traduções

## Pré-requisitos

Antes de iniciar, você precisará ter os seguintes itens instalados:

- Python 3.x
- Flask
- PyPDF2
- Groq API


## Estrutura do Projeto
- app.py: Arquivo principal contendo a lógica da aplicação e rotas.
- templates/: Diretório contendo os arquivos HTML (index.html e result.html).
- uploads/: Diretório onde os PDFs enviados são armazenados temporariamente.
- .env: Arquivo para configuração da chave da API Groq.
