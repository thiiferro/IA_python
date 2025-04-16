import os
import json
import schedule
import time
import threading
from flask import Flask, request, render_template, Response
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

app = Flask(__name__, static_url_path='/Projeto_IA/static')

# Inicializa o cliente do OpenAI
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="meta-llama-3-8b-instruct",
    timeout=160
)

# Constantes
PASTA_ARQUIVOS = "arquivos"
PASTA_DADOS = "data"
ARQUIVO_CONVERSAS = os.path.join(PASTA_DADOS, "conversas.json")
TOKEN_LIMIT = 8096
RESERVA_USUARIO = 1500
MAX_ARQUIVOS_PROCESSADOS = 3

# Variáveis globais
indice_arquivos = {}

# Função para contar tokens
def contar_tokens(texto):
    return len(texto.split())

# Função para carregar conversas do arquivo JSON
def carregar_conversas():
    if os.path.exists(ARQUIVO_CONVERSAS):
        with open(ARQUIVO_CONVERSAS, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                return dados.get("messages", [])
            except json.JSONDecodeError:
                return []
    return []

# Função para indexar arquivos
def indexar_arquivos():
    global indice_arquivos
    indice_arquivos = {}
    
    os.makedirs(PASTA_ARQUIVOS, exist_ok=True)

    for root, _, files in os.walk(PASTA_ARQUIVOS):
        for arquivo in files:
            caminho_completo = os.path.join(root, arquivo)
            conteudo = ""

            try:
                conteudo = processar_arquivo(arquivo, caminho_completo)
                if conteudo:
                    indice_arquivos[arquivo] = conteudo
            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")

    print(f"Indexação concluída! Arquivos processados: {len(indice_arquivos)}")

# Função para processar diferentes tipos de arquivo
def processar_arquivo(arquivo, caminho):
    conteudo = ""
    
    if arquivo.endswith(".pdf"):
        with open(caminho, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                conteudo += page.extract_text() + "\n"
    elif arquivo.endswith(".docx"):
        doc = Document(caminho)
        for para in doc.paragraphs:
            conteudo += para.text + "\n"
    elif arquivo.endswith(".csv"):
        df = pd.read_csv(caminho)
        conteudo += df.to_string() + "\n"
    elif arquivo.endswith(".json"):
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = json.dumps(json.load(f), indent=2)
    elif arquivo.endswith(".txt"):
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

    return conteudo

# Função para buscar conteúdo relevante
def buscar_conteudo(pergunta):
    palavras_chave = set(pergunta.lower().split())
    arquivos_relevantes = []
    tokens_totais = 0
    limite_disponivel = TOKEN_LIMIT - RESERVA_USUARIO

    for nome_arquivo, conteudo in indice_arquivos.items():
        if len(arquivos_relevantes) >= MAX_ARQUIVOS_PROCESSADOS:
            break

        if any(palavra in conteudo.lower() for palavra in palavras_chave):
            tokens_arquivo = contar_tokens(conteudo)
            if tokens_totais + tokens_arquivo > limite_disponivel:
                break

            arquivos_relevantes.append(conteudo[:1000])  # Limita o conteúdo para 1000 caracteres
            tokens_totais += tokens_arquivo

    contexto = "\n".join(arquivos_relevantes)

    while contar_tokens(contexto) > limite_disponivel:
        contexto = " ".join(contexto.split()[:limite_disponivel])

    return contexto if contexto else "Nenhuma informação relevante encontrada."

# Agendamento para indexar os arquivos diariamente
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

@app.route("/chat/completions", methods=["POST"])
def chat():
    dados = request.json
    mensagem_usuario = dados.get("mensagem", "")
    print("Mensagem recebida:", mensagem_usuario)  # Log da mensagem recebida

    if not mensagem_usuario:
        return Response("Por favor, envie uma mensagem válida.", content_type='text/plain')

    historico_conversa = carregar_conversas()
    historico_conversa.append({"role": "user", "content": mensagem_usuario})

    contexto = buscar_conteudo(mensagem_usuario)
    print("Contexto para a IA:", contexto)  # Log do contexto para a IA

    try:
        messages = [
            {"role": "system", "content": "Responda de forma natural e humanizada. Seja amigável e forneça informações úteis."},
            *historico_conversa,
            {"role": "system", "content": contexto}
        ]

        completion = client.chat.completions.create(
            model="meta-llama-3-8b-instruct",
            messages=messages,
            temperature=0.7
        )

        resposta_gerada = completion.choices[0].message.content
        print("Resposta gerada:", resposta_gerada)  # Log da resposta gerada
        return Response(resposta_gerada, content_type='text/plain')

    except Exception as e:
        print("Erro na IA:", str(e))
        return Response("Desculpe, houve um erro ao processar a resposta.", content_type='text/plain')

if __name__ == "__main__":
    indexar_arquivos()  # Indexação inicial dos arquivos
    app.run(debug=True)