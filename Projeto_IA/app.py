from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

# Configuração do cliente OpenAI
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

@app.route("/")
def index():
    return render_template("index.html")  # Carrega a interface HTML

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.json
    conversa = dados.get("mensagem", "")  # Pega a mensagem do usuário

    # Gera resposta da IA
    completion = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": "Always answer in rhymes."},
            {"role": "user", "content": conversa}
        ],
        temperature=0.7,
    )

    resposta = completion.choices[0].message.content

    return jsonify({"resposta": resposta})  # Retorna resposta para o frontend

if __name__ == "__main__":
    app.run(debug=True)
