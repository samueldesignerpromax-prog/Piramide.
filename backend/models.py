import bcrypt
from database import Database

class Usuario:
    def __init__(self):
        self.db = Database()
    
    def cadastrar(self, nome, email, senha):
        # Verificar se email já existe
        query = "SELECT id FROM usuarios WHERE email = %s"
        existe = self.db.fetch_one(query, (email,))
        
        if existe:
            return {"success": False, "message": "E-mail já cadastrado!"}
        
        # Hash da senha
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
        
        # Inserir usuário
        query = """
            INSERT INTO usuarios (nome, email, senha, tipo) 
            VALUES (%s, %s, %s, 'cliente')
        """
        params = (nome, email, senha_hash.decode('utf-8'))
        
        if self.db.execute_query(query, params):
            return {"success": True, "message": "Cadastro realizado com sucesso!"}
        return {"success": False, "message": "Erro ao cadastrar!"}
    
    def login(self, email, senha):
        query = "SELECT * FROM usuarios WHERE email = %s"
        usuario = self.db.fetch_one(query, (email,))
        
        if usuario:
            if bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
                return {
                    "success": True,
                    "user": {
                        "id": usuario['id'],
                        "nome": usuario['nome'],
                        "email": usuario['email'],
                        "tipo": usuario['tipo']
                    }
                }
        return {"success": False, "message": "E-mail ou senha incorretos!"}
    
    def get_user_by_id(self, user_id):
        query = "SELECT id, nome, email, tipo FROM usuarios WHERE id = %s"
        return self.db.fetch_one(query, (user_id,))

class Curso:
    def __init__(self):
        self.db = Database()
    
    def listar_todos(self, categoria_id=None, busca=None):
        query = """
            SELECT c.*, cat.nome as categoria_nome, cat.icone 
            FROM cursos c 
            LEFT JOIN categorias cat ON c.categoria_id = cat.id 
            WHERE 1=1
        """
        params = []
        
        if categoria_id:
            query += " AND c.categoria_id = %s"
            params.append(categoria_id)
        
        if busca:
            query += " AND (c.titulo LIKE %s OR c.descricao LIKE %s)"
            busca_param = f"%{busca}%"
            params.append(busca_param)
            params.append(busca_param)
        
        query += " ORDER BY c.destaque DESC, c.data_criacao DESC"
        
        return self.db.fetch_all(query, tuple(params) if params else None)
    
    def buscar_por_id(self, curso_id):
        query = """
            SELECT c.*, cat.nome as categoria_nome 
            FROM cursos c 
            LEFT JOIN categorias cat ON c.categoria_id = cat.id 
            WHERE c.id = %s
        """
        return self.db.fetch_one(query, (curso_id,))
    
    def listar_destaques(self, limit=6):
        query = """
            SELECT * FROM cursos 
            WHERE destaque = 1 
            ORDER BY data_criacao DESC 
            LIMIT %s
        """
        return self.db.fetch_all(query, (limit,))
    
    def listar_categorias(self):
        query = "SELECT * FROM categorias"
        return self.db.fetch_all(query)

class Pedido:
    def __init__(self):
        self.db = Database()
    
    def criar_pedido(self, usuario_id, itens):
        total = sum(item['preco'] * item['quantidade'] for item in itens)
        
        # Inserir pedido
        query = "INSERT INTO pedidos (usuario_id, valor_total, status) VALUES (%s, %s, 'pago')"
        if self.db.execute_query(query, (usuario_id, total)):
            pedido_id = self.db.cursor.lastrowid
            
            # Inserir itens e matrículas
            for item in itens:
                # Inserir item do pedido
                query_item = """
                    INSERT INTO pedido_itens (pedido_id, curso_id, preco_unitario) 
                    VALUES (%s, %s, %s)
                """
                self.db.execute_query(query_item, (pedido_id, item['id'], item['preco']))
                
                # Criar matrícula
                query_matricula = """
                    INSERT INTO matriculas (usuario_id, curso_id) 
                    VALUES (%s, %s)
                """
                self.db.execute_query(query_matricula, (usuario_id, item['id']))
            
            return {"success": True, "pedido_id": pedido_id}
        
        return {"success": False, "message": "Erro ao processar pedido!"}
    
    def listar_pedidos_usuario(self, usuario_id):
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(c.titulo SEPARATOR ', ') as cursos 
            FROM pedidos p
            LEFT JOIN pedido_itens pi ON p.id = pi.pedido_id
            LEFT JOIN cursos c ON pi.curso_id = c.id
            WHERE p.usuario_id = %s
            GROUP BY p.id
            ORDER BY p.data_pedido DESC
        """
        return self.db.fetch_all(query, (usuario_id,))

class Admin:
    def __init__(self):
        self.db = Database()
    
    def get_stats(self):
        stats = {}
        
        # Total de cursos
        query = "SELECT COUNT(*) as total FROM cursos"
        stats['total_cursos'] = self.db.fetch_one(query)['total']
        
        # Total de usuários
        query = "SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'cliente'"
        stats['total_usuarios'] = self.db.fetch_one(query)['total']
        
        # Total de vendas
        query = """
            SELECT COUNT(*) as total, SUM(valor_total) as total_valor 
            FROM pedidos WHERE status = 'pago'
        """
        result = self.db.fetch_one(query)
        stats['total_vendas'] = result['total'] if result else 0
        stats['total_valor'] = result['total_valor'] if result else 0
        
        return stats
    
    def adicionar_curso(self, dados):
        query = """
            INSERT INTO cursos (titulo, descricao, preco, carga_horaria, categoria_id, destaque)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            dados['titulo'],
            dados['descricao'],
            dados['preco'],
            dados['carga_horaria'],
            dados['categoria_id'],
            dados.get('destaque', 0)
        )
        return self.db.execute_query(query, params)
    
    def atualizar_curso(self, curso_id, dados):
        query = """
            UPDATE cursos 
            SET titulo=%s, descricao=%s, preco=%s, carga_horaria=%s, 
                categoria_id=%s, destaque=%s
            WHERE id=%s
        """
        params = (
            dados['titulo'],
            dados['descricao'],
            dados['preco'],
            dados['carga_horaria'],
            dados['categoria_id'],
            dados.get('destaque', 0),
            curso_id
        )
        return self.db.execute_query(query, params)
    
    def deletar_curso(self, curso_id):
        query = "DELETE FROM cursos WHERE id = %s"
        return self.db.execute_query(query, (curso_id,))
