import os
import json
import uuid
from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "chave-secreta"

client = OpenAI(base_url="http://localhost:1234/v1", api_key="Meta-Llama-3.1-8B-Instruct-GGUF")

DATA_DIR = "data"
CONVERSAS_FILE = os.path.join(DATA_DIR, "conversas.json")

# Garante que a pasta existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Se o arquivo não existir, cria um JSON vazio
if not os.path.exists(CONVERSAS_FILE) or os.stat(CONVERSAS_FILE).st_size == 0:
    with open(CONVERSAS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def carregar_conversas():
    """Carrega o histórico de conversas do arquivo JSON."""
    try:
        with open(CONVERSAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f) or {}  # Retorna um dicionário vazio se o JSON estiver vazio
    except json.JSONDecodeError:
        return {}  # Se houver erro ao carregar, retorna um dicionário vazio

def salvar_conversas(conversas):
    """Salva o histórico de conversas no arquivo JSON."""
    with open(CONVERSAS_FILE, "w", encoding="utf-8") as f:
        json.dump(conversas, f, indent=4)

@app.route("/")
def index():
    if "chat_id" not in session:
        session["chat_id"] = str(uuid.uuid4())
        session["historico"] = []

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    conversas = carregar_conversas()
    chat_id = session["chat_id"]

    if chat_id not in conversas:
        conversas[chat_id] = []

    conversas[chat_id].append({"role": "user", "content": mensagem})

    completion = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": "Sempre responda de forma clara e objetiva."}
        ] + conversas[chat_id],
        temperature=0.7,
    )

    resposta = completion.choices[0].message.content

    conversas[chat_id].append({"role": "assistant", "content": resposta})
    salvar_conversas(conversas)

    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(debug=True)
