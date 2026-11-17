import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
 
# 1) Carrega as variáveis do arquivo .env (GROQ_API_KEY e GROQ_MODEL)
load_dotenv()
 
app = Flask(__name__)
 
# 2) Cria o cliente da Groq usando a chave guardada no .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
 
# 3) Modelo de IA usado. Pode ser trocado no .env sem mexer no código.
MODELO = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
 
# 4) "Personalidade" do assistente (mensagem de sistema)
INSTRUCOES = (
    "Você é um assistente simpático que conversa em português do Brasil "
    "com alunos de um curso de informática. Responda de forma clara, "
    "natural e didática, como um professor paciente. Lembre-se do que "
    "já foi dito na conversa e use isso nas próximas respostas."
)
 
# 5) Quantas mensagens antigas o bot "lembra" (evita textos gigantes)
LIMITE_HISTORICO = 20
 
 
@app.route("/")
def index():
    # Mostra a tela do chat (arquivo templates/chat.html)
    return render_template("chat.html", modelo=MODELO)
 
 
@app.route("/api/chat", methods=["POST"])
def chat():
    dados = request.get_json(silent=True) or {}
    historico = dados.get("historico") or []
 
    # Mantém só mensagens válidas de "user" e "assistant"
    mensagens_validas = [
        {"role": m["role"], "content": str(m["content"])}
        for m in historico
        if isinstance(m, dict)
        and m.get("role") in ("user", "assistant")
        and str(m.get("content", "")).strip()
    ]
 
    if not mensagens_validas or mensagens_validas[-1]["role"] != "user":
        return jsonify({"resposta": "Digite alguma coisa para eu responder."})
 
    # Monta a conversa: instruções + últimas mensagens (a memória do bot)
    mensagens = [{"role": "system", "content": INSTRUCOES}]
    mensagens += mensagens_validas[-LIMITE_HISTORICO:]
 
    try:
        resposta = client.chat.completions.create(
            model=MODELO,
            messages=mensagens,
            temperature=0.7,
            max_tokens=1024,
        )
        texto = resposta.choices[0].message.content
        return jsonify({"resposta": texto})
    except Exception as erro:
        print("Erro ao falar com a Groq:", erro)
        return jsonify({"resposta": f"Ops! Deu erro ao falar com a IA: {erro}"}), 500
 
 
if __name__ == "__main__":
    app.run(debug=True)
