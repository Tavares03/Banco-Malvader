from flask import Blueprint, render_template, request, redirect, session, url_for
from dao.cliente_dao import obter_saldo_por_usuario, listar_contas_do_usuario, obter_limite_e_score, obter_dados_completos_cliente, listar_contas_do_usuario
from dao.conta_dao import criar_conta_extra, historico_transacoes, conta_por_id, transferir_valor, conta_por_usuario, realizar_deposito, get_limite_e_score, realizar_saque, encerrar_conta
from dao.usuario_dao import buscar_usuario_por_cpf_ou_telefone
cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
def cliente():
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))

    id_usuario = session["usuario_id"]
    saldo_total = obter_saldo_por_usuario(id_usuario)
    contas = listar_contas_do_usuario(id_usuario)

    return render_template("menu_cliente.html", saldo=saldo_total, contas=contas)

@cliente_route.route('/transferir', methods=['GET', 'POST'])
def transferir():
    erro = None
    sucesso = None
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))

    id_usuario = session["usuario_id"]
    contas = listar_contas_do_usuario(id_usuario)
    saldo_total = sum([c['saldo'] for c in contas])

    if request.method == 'POST':
        cpf_destino = request.form.get('cpf_destino', '').strip()
        telefone_destino = request.form.get('telefone_destino', '').strip()
        valor = float(request.form.get('valor', 0))

        if not cpf_destino and not telefone_destino:
            erro = "Informe o CPF ou o telefone do destinatário."
        elif valor <= 0:
            erro = "Informe um valor válido para transferência."
        elif valor > saldo_total:
            erro = "Saldo insuficiente para transferência."
        else:
            usuario_destino = buscar_usuario_por_cpf_ou_telefone(cpf_destino, telefone_destino)
            if not usuario_destino:
                erro = "Destinatário não encontrado."
            elif usuario_destino['id_usuario'] == id_usuario:
                erro = "Não é possível transferir para você mesmo."
            else:
                # Pega a primeira conta do usuário origem e destino (pode melhorar para escolher)
                conta_origem = contas[0]
                conta_destino = conta_por_usuario(usuario_destino['id_usuario'])
                if not conta_destino:
                    erro = "Destinatário não possui conta ativa."
                else:
                    sucesso = transferir_valor(conta_origem['id_conta'], conta_destino['id_conta'], valor)
                    if sucesso:
                        sucesso = f"Transferência de R$ {valor:.2f} realizada com sucesso!"
                    else:
                        erro = "Erro ao realizar transferência."

    return render_template('transferir.html', erro=erro, sucesso=sucesso)

@cliente_route.route('/extrato/<int:id_conta>')
def extrato_conta(id_conta):
    conta = conta_por_id(id_conta)
    transacoes = historico_transacoes(id_conta)

    return render_template('extrato.html', transacoes=transacoes, conta=conta)

@cliente_route.route('/depositar', methods=['GET', 'POST'])
def depositar():
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))
    id_usuario_logado = session["usuario_id"]

    if request.method == 'POST':
        id_conta = request.form.get('id_conta')
        valor_str = request.form.get('valor')

        # --- Validação dos Dados ---
        if not id_conta or not valor_str:
            return redirect(url_for('cliente.depositar'))

        try:
            valor = float(valor_str.replace(',', '.'))
            id_conta = int(id_conta)
            if valor <= 0:
                return redirect(url_for('cliente.depositar'))
        except (ValueError, TypeError):
            return redirect(url_for('cliente.depositar'))
            
        # --- Validação de Segurança ---
        contas_do_usuario = listar_contas_do_usuario(id_usuario_logado)
        ids_contas_permitidas = [c['id_conta'] for c in contas_do_usuario]
        if id_conta not in ids_contas_permitidas:
            return redirect(url_for('cliente.cliente'))
        
        realizar_deposito(id_conta, valor)
        
        # Após a tentativa de depósito, apenas redireciona para o menu principal
        return redirect(url_for('cliente.cliente'))

    # Se o método for GET, apenas exibe a página de depósito
    else:
        contas = listar_contas_do_usuario(id_usuario_logado)
        return render_template('depositar.html', contas=contas)

@cliente_route.route('/pagamentos')
def pagamentos():
    return render_template('pagamentos.html')

@cliente_route.route('/cartao')
def cartao():
    return render_template('cartao.html')

@cliente_route.route('/abrir_conta', methods=['GET', 'POST'])
def abrir_conta():
    if "usuario_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        tipo_conta = request.form.get("tipo_conta")

        id_usuario = session["usuario_id"]
        sucesso = criar_conta_extra(id_usuario, tipo_conta)

        if sucesso:
            return redirect("/cliente")
        else:
            return "Erro ao criar a conta"

    return render_template("abrir_conta.html")

@cliente_route.route('/perfil')
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))
    id_usuario = session["usuario_id"]
    cliente = obter_dados_completos_cliente(id_usuario)
    return render_template('perfil.html', cliente=cliente)

@cliente_route.route('/sacar', methods=['GET', 'POST'])
def sacar():
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))
    id_usuario_logado = session["usuario_id"]

    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        id_conta = request.form.get('id_conta')
        valor_str = request.form.get('valor')

        # Validações iniciais
        if not id_conta or not valor_str:
            return redirect(url_for('cliente.sacar'))
        try:
            valor = float(valor_str.replace(',', '.'))
            id_conta = int(id_conta)
            if valor <= 0:
                return redirect(url_for('cliente.sacar'))
        except (ValueError, TypeError):
            return redirect(url_for('cliente.sacar'))
            
        # Validação de segurança para garantir que a conta pertence ao usuário logado
        contas_do_usuario = listar_contas_do_usuario(id_usuario_logado)
        ids_contas_permitidas = [c['id_conta'] for c in contas_do_usuario]
        if id_conta not in ids_contas_permitidas:
            return redirect(url_for('cliente.cliente'))
        
        # Chama a função do DAO para tentar realizar o saque
        resultado = realizar_saque(id_conta, valor)

        # Ação baseada no resultado da função do DAO
        if resultado == True:
            # Sucesso! Apenas redireciona para o menu.
            print("Saque realizado com sucesso!")
        elif resultado == 'SALDO_INSUFICIENTE':
            # Saldo insuficiente. Apenas redireciona.
            print("Tentativa de saque falhou: Saldo insuficiente.")
        else:
            # Outro erro. Apenas redireciona.
            print("Tentativa de saque falhou: Erro geral.")
            
        return redirect(url_for('cliente.cliente'))

    # Se a requisição for GET, apenas mostra a página com o formulário
    else:
        contas = listar_contas_do_usuario(id_usuario_logado)
        return render_template('sacar.html', contas=contas)

@cliente_route.route('/consultar_limite')
def consultar_limite():
    if "usuario_id" not in session:
        return redirect(url_for('login.login'))
    id_usuario_logado = session["usuario_id"]
    # 1. Pega todas as contas do usuário
    contas = listar_contas_do_usuario(id_usuario_logado)
    
    # Lista para guardar as informações de limite de cada conta
    info_limites = []

    # 2. Itera sobre as contas para calcular o limite de cada uma
    for conta in contas:
        # Apenas contas do tipo 'CORRENTE' possuem limite
        if conta['tipo_conta'] == 'CORRENTE':
            dados = get_limite_e_score(conta['id_conta'])
            
            if dados:
                limite_atual = dados['limite']
                score = dados['score_credito']

                # 3. Limite base de 200 + bônus pelo score
                limite_potencial = 200 + (score * 10)

                info_limites.append({
                    'numero_conta': conta['numero_conta'],
                    'limite_atual': limite_atual,
                    'score_credito': score,
                    'limite_potencial': limite_potencial
                })

    return render_template('consultar_limite.html', info_limites=info_limites)

@cliente_route.route('/encerrar_conta', methods=['GET', 'POST'])
def encerrar_conta_route(): # Mudei o nome para não conflitar com a função do DAO
    if 'usuario_id' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        numero_conta = request.form.get('numero_conta')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')

        if not all([numero_conta, cpf, senha]):
            # Idealmente, aqui iria uma mensagem de erro
            return redirect(url_for('cliente.encerrar_conta_route'))
        
        resultado = encerrar_conta(numero_conta, cpf, senha)

        if resultado == True:
            # Se a conta foi encerrada com sucesso, desloga o usuário e o envia para a página de login
            session.clear() # Limpa a sessão
            # Idealmente, aqui iria uma mensagem de "Conta encerrada com sucesso"
            return redirect(url_for('login.login'))
        else:
            # Se houve um erro (saldo não zerado, dados incorretos, etc.),
            # apenas redireciona de volta para a página de encerramento.
            # O ideal seria mostrar uma mensagem específica do erro.
            print(f"Falha ao encerrar conta. Motivo: {resultado}")
            return redirect(url_for('cliente.encerrar_conta_route'))

    # Se for GET, apenas mostra a página
    return render_template('encerrar_conta.html')

@cliente_route.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login.login'))

