// ==================== CONFIGURAÇÕES ====================
const API_URL = 'http://localhost:5000/api';

// ==================== FUNÇÕES DE API ====================
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('Erro na API:', error);
        mostrarNotificacao('Erro de conexão com o servidor!', 'error');
        return null;
    }
}

// ==================== NOTIFICAÇÕES ====================
function mostrarNotificacao(mensagem, tipo = 'success') {
    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${tipo}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    notification.innerHTML = `
        <div class="toast-icon">${icons[tipo] || '✅'}</div>
        <div class="toast-message">${mensagem}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== CARRINHO ====================
function getCarrinho() {
    const carrinho = localStorage.getItem('carrinho');
    return carrinho ? JSON.parse(carrinho) : [];
}

function salvarCarrinho(carrinho) {
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    atualizarCarrinhoCount();
}

function adicionarAoCarrinho(cursoId, nome, preco) {
    let carrinho = getCarrinho();
    const itemExistente = carrinho.find(item => item.id == cursoId);
    
    if (itemExistente) {
        itemExistente.quantidade++;
        mostrarNotificacao(`${nome} - Quantidade atualizada!`, 'info');
    } else {
        carrinho.push({
            id: cursoId,
            nome: nome,
            preco: preco,
            quantidade: 1
        });
        mostrarNotificacao(`${nome} adicionado ao carrinho!`, 'success');
    }
    
    salvarCarrinho(carrinho);
}

function removerDoCarrinho(cursoId) {
    let carrinho = getCarrinho();
    carrinho = carrinho.filter(item => item.id != cursoId);
    salvarCarrinho(carrinho);
    mostrarNotificacao('Item removido do carrinho!', 'info');
    location.reload();
}

function atualizarCarrinhoCount() {
    const carrinho = getCarrinho();
    const totalItens = carrinho.reduce((total, item) => total + item.quantidade, 0);
    const contadores = document.querySelectorAll('#cartCount');
    contadores.forEach(contador => {
        contador.textContent = totalItens;
    });
}

function calcularTotalCarrinho() {
    const carrinho = getCarrinho();
    return carrinho.reduce((total, item) => total + (item.preco * item.quantidade), 0);
}

// ==================== USUÁRIO ====================
function verificarLogin() {
    const usuario = localStorage.getItem('usuario');
    const authLinks = document.getElementById('authLinks');
    
    if (usuario && authLinks) {
        const user = JSON.parse(usuario);
        authLinks.innerHTML = `
            <div class="dropdown">
                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                    <i class="fas fa-user me-1"></i>${user.nome}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="#"><i class="fas fa-user-circle me-2"></i>Meu Perfil</a></li>
                    <li><a class="dropdown-item" href="#"><i class="fas fa-book me-2"></i>Meus Cursos</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>Sair</a></li>
                </ul>
            </div>
        `;
    }
}

function logout() {
    localStorage.removeItem('usuario');
    mostrarNotificacao('Logout realizado com sucesso!', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

// ==================== CURSOS ====================
async function carregarCursos() {
    const cursos = await apiRequest('/cursos');
    return cursos || [];
}

async function carregarCursosDestaque() {
    const cursos = await apiRequest('/cursos/destaques');
    const container = document.getElementById('cursos-destaque');
    
    if (!container) return;
    
    if (cursos && cursos.length > 0) {
        container.innerHTML = cursos.map(curso => `
            <div class="col-md-4 mb-4">
                <div class="card course-card h-100">
                    <img src="../static/img/curso-${curso.id}.jpg" class="card-img-top" alt="${curso.titulo}" onerror="this.src='https://via.placeholder.com/300x200?text=Curso'">
                    <div class="card-body">
                        <span class="badge bg-primary mb-2">Destaque</span>
                        <h5 class="card-title">${curso.titulo}</h5>
                        <p class="card-text">${curso.descricao.substring(0, 100)}...</p>
                        <div class="price-tag">
                            R$ ${curso.preco.toFixed(2).replace('.', ',')}
                            <small>/curso completo</small>
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" onclick="verCurso(${curso.id})">Ver Detalhes</button>
                            <button class="btn btn-outline-primary" onclick="adicionarAoCarrinho(${curso.id}, '${curso.titulo}', ${curso.preco})">
                                Adicionar ao Carrinho
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="col-12 text-center">Nenhum curso em destaque no momento.</div>';
    }
}

async function carregarCategorias() {
    const categorias = await apiRequest('/categorias');
    const container = document.getElementById('categorias');
    
    if (!container) return;
    
    if (categorias && categorias.length > 0) {
        container.innerHTML = categorias.map(cat => `
            <div class="col-md-3 mb-4">
                <div class="card category-card" onclick="window.location.href='cursos.html?categoria=${cat.id}'">
                    <div class="card-body text-center">
                        <div class="category-icon mb-3"><i class="fas ${cat.icone}"></i></div>
                        <h5 class="card-title">${cat.nome}</h5>
                        <p class="card-text small">${cat.descricao}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

function verCurso(cursoId) {
    window.location.href = `curso-detalhe.html?id=${cursoId}`;
}

// ==================== PAGAMENTO ====================
async function finalizarCompra(usuarioId, itens) {
    const result = await apiRequest('/pedido', 'POST', {
        usuario_id: usuarioId,
        itens: itens
    });
    
    if (result && result.success) {
        mostrarNotificacao('Compra realizada com sucesso!', 'success');
        localStorage.removeItem('carrinho');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
        return true;
    } else {
        mostrarNotificacao('Erro ao processar compra!', 'error');
        return false;
    }
}

// ==================== INICIALIZAÇÃO ====================
document.addEventListener('DOMContentLoaded', function() {
    atualizarCarrinhoCount();
    verificarLogin();
});
