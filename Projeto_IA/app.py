import os
import json
import schedule
import time
import threading
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
indice_arquivos = {}
TOKEN_LIMIT = 8096  # Limite de tokens do modelo
RESERVA_USUARIO = 1500  # Espaço reservado para a pergunta e resposta
MAX_ARQUIVOS_PROCESSADOS = 3  # Número máximo de arquivos a serem processados por vez

# Função para contar tokens (estimativa simples baseada em palavras)
def contar_tokens(texto):
    return len(texto.split())

# Função para carregar conversas do arquivo JSON
def carregar_conversas():
    PASTA_DADOS = "data"
    ARQUIVO_CONVERSAS = os.path.join(PASTA_DADOS, "conversas.json")
    
    if os.path.exists(ARQUIVO_CONVERSAS):
        with open(ARQUIVO_CONVERSAS, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                return dados.get("messages", [])
            except json.JSONDecodeError:
                return []
    return []

# Indexação de arquivos
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
    limite_disponivel = TOKEN_LIMIT - RESERVA_USUARIO  # Reserva espaço para pergunta e resposta
    arquivos_processados = 0

    for nome_arquivo, conteudo in indice_arquivos.items():
        if arquivos_processados >= MAX_ARQUIVOS_PROCESSADOS:
            break  # Limita o número de arquivos processados

        if any(palavra in conteudo.lower() for palavra in palavras_chave):
            tokens_arquivo = contar_tokens(conteudo)
            if tokens_totais + tokens_arquivo > limite_disponivel:
                break  # Evita ultrapassar o limite de tokens permitido

            arquivos_relevantes.append(conteudo[:1000])  # Limita o conteúdo de cada arquivo para 1000 tokens (aproximadamente)
            tokens_totais += tokens_arquivo
            arquivos_processados += 1

    contexto = "\n".join(arquivos_relevantes)

    # Se mesmo assim ultrapassar o limite, cortar até ficar dentro do permitido
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

    # Carregar histórico de conversas
    historico_conversa = carregar_conversas()

    # Adiciona a interação anterior para manter o fluxo da conversa
    historico_conversa.append({"role": "user", "content": mensagem_usuario})

    # Recuperar contexto da conversa anterior (se houver)
    contexto = buscar_conteudo(mensagem_usuario)

    try:
        # Certifique-se de que o histórico está correto
        messages = [
            {"role": "system", "content": "Responda de forma natural e humanizada. Seja amigável e forneça informações úteis."},
            *historico_conversa,
            {"role": "system", "content": contexto if contexto else "Nenhuma informação relevante encontrada."}
        ]

        # Enviar o histórico de conversa completo
        completion = client.chat.completions.create(
            model="meta-llama-3.1-8b-instruct",
            messages=messages,
            temperature=0.7
        )

        resposta_gerada = completion.choices[0].message.content

        # Retorna a resposta gerada
        return Response(resposta_gerada, content_type='text/plain')

    except requests.exceptions.RequestException as e:
        print("Erro de conexão com o modelo:", e)
        return Response("Erro de conexão com o modelo. Tente novamente mais tarde.", content_type='text/plain')

    except Exception as e:
        print("Erro na IA:", e)
        return Response("Desculpe, houve um erro ao processar a resposta.", content_type='text/plain')

if __name__ == "__main__":
    indexar_arquivos()  # Indexação inicial dos arquivos
    app.run(debug=True)
