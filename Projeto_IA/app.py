import os
import json
import schedule
import time
import threading
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

app = Flask(__name__)

client = OpenAI(base_url="http://localhost:1234/v1", api_key="Meta-Llama-3.1-8B-Instruct-GGUF")

PASTA_ARQUIVOS = "arquivos"

# Dicionário para armazenar o conteúdo dos arquivos
indice_arquivos = {}

def indexar_arquivos():
    """ Lê todos os arquivos e armazena em um índice """
    global indice_arquivos
    indice_arquivos = {}

    if not os.path.exists(PASTA_ARQUIVOS):
        os.makedirs(PASTA_ARQUIVOS)

    for root, _, files in os.walk(PASTA_ARQUIVOS):
        for arquivo in files:
            caminho_completo = os.path.join(root, arquivo)

            try:
                conteudo = ""

                if arquivo.endswith(".pdf"):
                    with open(caminho_completo, "rb") as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            conteudo += page.extract_text() + "\n"

                elif arquivo.endswith(".docx"):
                    doc = Document(caminho_completo)
                    for para in doc.paragraphs:
                        conteudo += para.text + "\n"

                elif arquivo.endswith(".csv"):
                    df = pd.read_csv(caminho_completo)
                    conteudo += df.to_string() + "\n"

                elif arquivo.endswith(".json"):
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        conteudo = json.dumps(json.load(f), indent=2)

                elif arquivo.endswith(".txt"):
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        conteudo = f.read()

                if conteudo:
                    indice_arquivos[arquivo] = conteudo  # Armazena o conteúdo no índice

            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")

    print("Indexação concluída!")

def buscar_conteudo(pergunta):
    """ Busca os arquivos mais relevantes para a pergunta do usuário """
    palavras_chave = set(pergunta.lower().split())  # Quebra a pergunta em palavras-chave
    arquivos_relevantes = []

    for nome_arquivo, conteudo in indice_arquivos.items():
        if any(palavra in conteudo.lower() for palavra in palavras_chave):  # Se o arquivo tem alguma palavra da pergunta
            arquivos_relevantes.append(conteudo[:2000])  # Limita o tamanho para não passar do limite da IA

    return "\n".join(arquivos_relevantes) if arquivos_relevantes else "Nenhuma informação relevante encontrada."

# Agendador para reindexar os arquivos diariamente
schedule.every().day.at("00:00").do(indexar_arquivos)

def executar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

t = threading.Thread(target=executar_agendador, daemon=True)
t.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.json
    mensagem_usuario = dados.get("mensagem", "")

    # Busca apenas os trechos relevantes nos arquivos indexados
    contexto = buscar_conteudo(mensagem_usuario)

    completion = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": mensagem_usuario}
        ],
        temperature=0.7,
    )

    resposta = completion.choices[0].message.content
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    indexar_arquivos()  # Carrega os arquivos ao iniciar
    app.run(debug=True)
