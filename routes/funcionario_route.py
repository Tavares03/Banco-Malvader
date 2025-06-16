from flask import Blueprint, render_template, session, redirect, request, url_for
from dao.funcionario_dao import obter_funcionario_por_usuario, listar_todos_clientes, listar_todas_contas_com_cliente, atualizar_status_conta, relatorio_resumo_banco, relatorio_ultimas_movimentacoes, relatorio_clientes_negativo_ou_limite
from dao.usuario_dao import cadastrar_usuario
from dao.endereco_dao import cadastrar_endereco
from dao.conta_dao import criar_conta_completa, atualizar_dados_conta_corrente
import random

funcionario_route = Blueprint('funcionario', __name__)

@funcionario_route.route('/')
def funcionario():
    if "usuario_id" not in session or session.get("tipo_usuario") != "FUNCIONARIO":
        return redirect(url_for('login.login'))
    id_usuario = session["usuario_id"]
    funcionario = obter_funcionario_por_usuario(id_usuario)
    return render_template('menu_funcionario.html', funcionario=funcionario)

@funcionario_route.route('/visualizar_clientes')
def visualizar_clientes():
    clientes = listar_todos_clientes()
    return render_template('visualizar_clientes.html', clientes=clientes)

@funcionario_route.route('/gerenciar_contas', methods=['GET', 'POST'])
def gerenciar_contas():
    if request.method == 'POST':
        id_conta = request.form.get('id_conta')
        acao = request.form.get('acao')
        if acao == 'ativar':
            atualizar_status_conta(id_conta, 'ATIVA')
        elif acao == 'encerrar':
            atualizar_status_conta(id_conta, 'ENCERRADA')
        elif acao == 'bloquear':
            atualizar_status_conta(id_conta, 'BLOQUEADA')
        return redirect(url_for('funcionario.gerenciar_contas'))

    contas = listar_todas_contas_com_cliente()
    return render_template('gerenciar_contas.html', contas=contas)

@funcionario_route.route('/relatorios')
def relatorios():
    resumo = relatorio_resumo_banco()
    ultimas = relatorio_ultimas_movimentacoes()
    negativos_limite = relatorio_clientes_negativo_ou_limite()
    return render_template(
        'relatorios.html',
        resumo=resumo,
        ultimas=ultimas,
        negativos=negativos_limite["negativos"],
        excedidos=negativos_limite["excedidos"]
    )

@funcionario_route.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login.login'))

@funcionario_route.route('/abertura_conta', methods=['GET', 'POST'])
def abertura_conta():
    if "usuario_id" not in session or session.get("tipo_usuario") != "FUNCIONARIO":
        return redirect(url_for('login.login'))

    mensagem = None

    if request.method == 'POST':
        # Dados do usuário
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        nascimento = request.form.get('nascimento')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario', 'CLIENTE').upper()

        # Endereço
        cep = request.form.get('cep')
        lugar = request.form.get('lugar')
        numero_casa = request.form.get('numero_casa')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        complemento = request.form.get('complemento')

        # Tipo de conta
        tipo_conta = request.form.get('tipo_conta')

        # Campos específicos
        taxa_rendimento = request.form.get('taxa_rendimento')
        limite = request.form.get('limite')
        data_vencimento = request.form.get('data_vencimento')
        taxa_manutencao = request.form.get('taxa_manutencao')
        perfil_risco = request.form.get('perfil_risco')
        valor_minimo = request.form.get('valor_minimo')
        taxa_rendimento_base = request.form.get('taxa_rendimento_base')

        # 1. Cadastra usuário
        id_usuario = cadastrar_usuario(nome, cpf, nascimento, telefone, senha, tipo_usuario)
        # 2. Cadastra endereço
        cadastrar_endereco(id_usuario, cep, lugar, numero_casa, bairro, cidade, estado, complemento)

        # 3. Cria conta conforme tipo
        kwargs = {}
        if tipo_conta == "POUPANCA":
            kwargs['taxa_rendimento'] = float(taxa_rendimento or 0.5)
        elif tipo_conta == "INVESTIMENTO":
            kwargs['perfil_risco'] = perfil_risco or 'MEDIO'
            kwargs['valor_minimo'] = float(valor_minimo or 500)
            kwargs['taxa_rendimento_base'] = float(taxa_rendimento_base or 1.25)
        elif tipo_conta == "CORRENTE":
            kwargs['limite'] = float(limite or 1000)
            kwargs['data_vencimento'] = data_vencimento or '2099-12-31'
            kwargs['taxa_manutencao'] = float(taxa_manutencao or 5)

        criar_conta_completa(id_usuario, tipo_conta, **kwargs)
        mensagem = "Conta criada com sucesso!"

    return render_template('abertura_de_conta.html', mensagem=mensagem)

@funcionario_route.route('/encerramento_conta', methods=['GET', 'POST'])
def encerramento_conta():
    if "usuario_id" not in session or session.get("tipo_usuario") != "FUNCIONARIO":
        return redirect('/')

    # Exemplo: buscar contas para exibir no select
    from dao.conta_dao import listar_todas_contas  # Implemente essa função conforme seu banco
    contas = listar_todas_contas()

    if request.method == 'POST':
        conta_id = request.form.get('conta')
        motivo = request.form.get('motivo')
        admin_senha = request.form.get('admin_senha')
        otp = request.form.get('otp') 
        return redirect('/encerramento_conta')

    return render_template('encerramento_de_conta.html', contas=contas)

@funcionario_route.route('/alterardados', methods=['GET', 'POST'])
def alterar_dados():
    if "usuario_id" not in session or session.get("tipo_usuario") != "FUNCIONARIO":
        return redirect('/')
    mensagem = None
    if request.method == 'POST':
        numero_conta = request.form.get('numero_conta')
        novo_limite = request.form.get('limite')
        nova_data = request.form.get('data_vencimento')
        nova_taxa = request.form.get('taxa_manutencao')
        sucesso = atualizar_dados_conta_corrente(numero_conta, novo_limite, nova_data, nova_taxa)
        if sucesso:
            mensagem = "Dados da conta atualizados com sucesso!"
        else:
            mensagem = "Conta não encontrada ou não é do tipo corrente."
    return render_template('alterardados.html', mensagem=mensagem)

from dao.funcionario_dao import criar_funcionario_padrao

@funcionario_route.route('/cadastro_funcionarios', methods=['GET', 'POST'])
def cadastro_funcionarios():
    mensagem = None
    if "usuario_id" not in session or session.get("tipo_usuario") != "FUNCIONARIO":
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        nascimento = request.form.get('nascimento')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        cep = request.form.get('cep')
        lugar = request.form.get('lugar')
        numero_casa = request.form.get('numero_casa')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        complemento = request.form.get('complemento')
        cargo = request.form.get('cargo')
        codigo_funcionario = f"FUNC{random.randint(1000,9999)}"

        # Cria usuário
        from dao.usuario_dao import cadastrar_usuario
        from dao.endereco_dao import cadastrar_endereco

        id_usuario = cadastrar_usuario(nome, cpf, nascimento, telefone, senha, "FUNCIONARIO")
        cadastrar_endereco(id_usuario, cep, lugar, numero_casa, bairro, cidade, estado, complemento)

        # Chama a procedure para criar o funcionário (cargo será ajustado depois se necessário)
        criar_funcionario_padrao(id_usuario, codigo_funcionario)

        # Atualiza o cargo se diferente do padrão
        if cargo and cargo != "ESTAGIARIO":
            conexao = None
            try:
                from util.db import conectar
                conexao = conectar()
                with conexao.cursor() as cursor:
                    cursor.execute("UPDATE funcionario SET cargo = %s WHERE id_usuario = %s", (cargo, id_usuario))
                conexao.commit()
            finally:
                if conexao:
                    conexao.close()

        mensagem = "Funcionário cadastrado com sucesso!"

    return render_template('cadastro_de_funcionarios.html', mensagem=mensagem)