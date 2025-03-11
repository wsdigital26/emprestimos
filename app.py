from flask import Flask, jsonify, request
import json
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função para carregar os dados
def carregar_dados():
    if not os.path.exists('registros.json'):
        # Cria um arquivo vazio se não existir
        with open('registros.json', 'w') as f:
            json.dump({"usuarios": []}, f, indent=4)
    with open('registros.json', 'r') as f:
        return json.load(f)

# Função para salvar os dados
def salvar_dados(dados):
    with open('registros.json', 'w') as f:
        json.dump(dados, f, indent=4)

# Função para carregar dados do arquivo JSON
def carregar_usuarios():
    with open('usuarios.json', 'r') as f:
        return json.load(f)

# Rota para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nome_usuario = data.get('nome')
    senha_usuario = data.get('senha')

    try:
        # Carregar o arquivo JSON dos usuários
        with open('usuarios.json', 'r') as file:
            usuarios = json.load(file)

        # Verificar se o usuário existe no arquivo
        for usuario in usuarios:
            if usuario['nome'] == nome_usuario and usuario['senha'] == senha_usuario:
                return jsonify({"mensagem": "Login bem-sucedido", "usuario": usuario}), 200

        # Caso o usuário não seja encontrado
        return jsonify({"mensagem": "Usuário ou senha incorretos"}), 401

    except FileNotFoundError:
        return jsonify({"mensagem": "Arquivo de usuários não encontrado"}), 500

# Rota para registrar um novo clique de contrato
@app.route('/registros', methods=['POST'])
def registrar_contrato():
    nome_usuario = request.json.get('nome_usuario')
    cliente = request.json.get('cliente')
    tipo = request.json.get('tipo')
    
    dados = carregar_dados()
    usuario = next((u for u in dados['usuarios'] if u['nome'] == nome_usuario), None)
    
    if usuario:
        novo_contrato = {
            "cliente": cliente,
            "tipo": tipo,
            "data_clique": datetime.now().isoformat(),
            "confirmado": False
        }
        usuario['contratos'].append(novo_contrato)
        salvar_dados(dados)
        return jsonify({"mensagem": "Clique registrado com sucesso", "contrato": novo_contrato}), 201
    else:
        return jsonify({"mensagem": "Usuário não encontrado"}), 404

# Rota para confirmar um contrato
@app.route('/confirmar_contrato', methods=['POST'])
def confirmar_contrato():
    nome_usuario = request.json.get('nome_usuario')
    cliente = request.json.get('cliente')
    
    dados = carregar_dados()
    usuario = next((u for u in dados['usuarios'] if u['nome'] == nome_usuario), None)
    
    if usuario:
        contrato = next((c for c in usuario['contratos'] if c['cliente'] == cliente and not c['confirmado']), None)
        if contrato:
            contrato['confirmado'] = True
            salvar_dados(dados)
            return jsonify({"mensagem": "Contrato confirmado com sucesso", "contrato": contrato}), 200
        else:
            return jsonify({"mensagem": "Contrato não encontrado ou já confirmado"}), 404
    else:
        return jsonify({"mensagem": "Usuário não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
