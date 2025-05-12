import os
import json
import schedule
import time
import threading
import markdown
from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import requests

app = Flask(__name__)

# Inicializa o cliente do OpenAI
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="meta-llama-3.1-8b-instruct",
    timeout=160
)

PASTA_ARQUIVOS = "arquivos"
PASTA_DATA = "data"
ARQUIVO_MEMORIA = os.path.join(PASTA_DATA, "conversas.json")
indice_arquivos = {}
TOKEN_LIMIT = 8096  # Limite de tokens do modelo
RESERVA_USUARIO = 1500  # Espaço reservado para a pergunta e resposta
MAX_ARQUIVOS_PROCESSADOS = 2000  # Número máximo de arquivos a serem processados por vez
memoria_permanente = {}

# Carregar a memória do JSON sem modificá-lo
def carregar_memoria():
    global memoria_permanente
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
                memoria_permanente = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar memória: {e}")

# Função para contar tokens (estimativa simples baseada em palavras)
def contar_tokens(texto):
    return len(texto.split())

# Indexação de arquivos (agora inclui .md)
def indexar_arquivos():
    global indice_arquivos
    indice_arquivos = {}

    if not os.path.exists(PASTA_ARQUIVOS):
        os.makedirs(PASTA_ARQUIVOS)

    for root, _, files in os.walk(PASTA_ARQUIVOS):
        for arquivo in files:
            caminho_completo = os.path.join(root, arquivo)
            conteudo = ""

            try:
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

                elif arquivo.endswith(".md"):  # Processa arquivos Markdown
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        md_content = f.read()
                        conteudo = markdown.markdown(md_content)  

                if conteudo:
                    indice_arquivos[arquivo] = conteudo

            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")

    print(f"Indexação concluída! Arquivos processados: {len(indice_arquivos)}")

# Busca inteligente nos arquivos, respeitando o limite de tokens
def buscar_conteudo(pergunta):
    palavras_chave = set(pergunta.lower().split())
    arquivos_relevantes = []
    tokens_totais = 0
    limite_disponivel = TOKEN_LIMIT - RESERVA_USUARIO
    arquivos_processados = 0

    for nome_arquivo, conteudo in indice_arquivos.items():
        if arquivos_processados >= MAX_ARQUIVOS_PROCESSADOS:
            break

        if any(palavra in conteudo.lower() for palavra in palavras_chave):
            tokens_arquivo = contar_tokens(conteudo)
            if tokens_totais + tokens_arquivo > limite_disponivel:
                break

            arquivos_relevantes.append(conteudo[:1000])  
            tokens_totais += tokens_arquivo
            arquivos_processados += 1

    contexto = "\n".join(arquivos_relevantes)

    while contar_tokens(contexto) > limite_disponivel:
        contexto = " ".join(contexto.split()[:limite_disponivel])

    return contexto if contexto else "Nenhuma informação relevante encontrada."

# Agendamento para indexar os arquivos
schedule.every().day.at("00:00").do(indexar_arquivos)

def executar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Thread para rodar o agendador de indexação
t = threading.Thread(target=executar_agendador, daemon=True)
t.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.json
    mensagem_usuario = dados.get("mensagem", "")

    if not mensagem_usuario:
        return Response("Por favor, envie uma mensagem válida.", content_type='text/plain')

    contexto = buscar_conteudo(mensagem_usuario)
    memoria_texto = "\n".join([f"{k}: {v}" for k, v in memoria_permanente.items()]) if memoria_permanente else "Nenhuma memória disponível."

    try:
        messages = [
            {"role": "system", "content": "Responda de forma natural e humanizada. Seja amigável e forneça informações úteis."},
            {"role": "system", "content": f"Memória permanente:\n{memoria_texto}"},
            {"role": "system", "content": contexto if contexto else "Nenhuma informação relevante encontrada."},
            {"role": "user", "content": mensagem_usuario}
        ]

        completion = client.chat.completions.create(
            model="meta-llama-3.1-8b-instruct",
            messages=messages,
            temperature=0.7
        )

        resposta_gerada = completion.choices[0].message.content
        return Response(resposta_gerada, content_type='text/plain')

    except requests.exceptions.RequestException as e:
        print("Erro de conexão com o modelo:", e)
        return Response("Erro de conexão com o modelo. Tente novamente mais tarde.", content_type='text/plain')

    except Exception as e:
        print("Erro na IA:", e)
        return Response("Desculpe, houve um erro ao processar a resposta.", content_type='text/plain')

if __name__ == "__main__":
    carregar_memoria()
    indexar_arquivos()
    app.run(debug=True)