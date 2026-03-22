from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import Usuario, Curso, Pedido, Admin
import json

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Instanciar modelos
usuario_model = Usuario()
curso_model = Curso()
pedido_model = Pedido()
admin_model = Admin()

# ==================== ROTAS PÚBLICAS ====================

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# ==================== API - USUÁRIOS ====================

@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    data = request.json
    result = usuario_model.cadastrar(
        data['nome'],
        data['email'],
        data['senha']
    )
    return jsonify(result)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    result = usuario_model.login(data['email'], data['senha'])
    return jsonify(result)

# ==================== API - CURSOS ====================

@app.route('/api/cursos', methods=['GET'])
def listar_cursos():
    categoria = request.args.get('categoria')
    busca = request.args.get('busca')
    cursos = curso_model.listar_todos(categoria, busca)
    return jsonify(cursos)

@app.route('/api/cursos/destaques', methods=['GET'])
def cursos_destaques():
    cursos = curso_model.listar_destaques()
    return jsonify(cursos)

@app.route('/api/cursos/<int:curso_id>', methods=['GET'])
def buscar_curso(curso_id):
    curso = curso_model.buscar_por_id(curso_id)
    if curso:
        return jsonify(curso)
    return jsonify({"error": "Curso não encontrado"}), 404

@app.route('/api/categorias', methods=['GET'])
def listar_categorias():
    categorias = curso_model.listar_categorias()
    return jsonify(categorias)

# ==================== API - PEDIDOS ====================

@app.route('/api/pedido', methods=['POST'])
def criar_pedido():
    data = request.json
    result = pedido_model.criar_pedido(data['usuario_id'], data['itens'])
    return jsonify(result)

@app.route('/api/pedidos/<int:usuario_id>', methods=['GET'])
def listar_pedidos(usuario_id):
    pedidos = pedido_model.listar_pedidos_usuario(usuario_id)
    return jsonify(pedidos)

# ==================== API - ADMIN ====================

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    stats = admin_model.get_stats()
    return jsonify(stats)

@app.route('/api/admin/cursos', methods=['POST'])
def admin_criar_curso():
    data = request.json
    result = admin_model.adicionar_curso(data)
    return jsonify({"success": result})

@app.route('/api/admin/cursos/<int:curso_id>', methods=['PUT'])
def admin_atualizar_curso(curso_id):
    data = request.json
    result = admin_model.atualizar_curso(curso_id, data)
    return jsonify({"success": result})

@app.route('/api/admin/cursos/<int:curso_id>', methods=['DELETE'])
def admin_deletar_curso(curso_id):
    result = admin_model.deletar_curso(curso_id)
    return jsonify({"success": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
