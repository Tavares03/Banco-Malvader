from util.db import conectar

def criar_funcionario_padrao(id_usuario, codigo_funcionario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = "CALL criar_funcionario_padrao(%s, %s)"
            cursor.execute(sql, (id_usuario, codigo_funcionario))
        conexao.commit()
    finally:
        conexao.close()

def obter_funcionario_por_usuario(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT f.*, u.nome, u.cpf, u.telefone
                FROM funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                WHERE f.id_usuario = %s
                LIMIT 1
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
    finally:
        conexao.close()

def listar_todas_contas_com_cliente():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT 
                    co.id_conta, co.numero_conta, co.tipo_conta, co.saldo, co.status,
                    u.nome AS nome_cliente, u.cpf
                FROM conta co
                JOIN cliente cl ON co.id_cliente = cl.id_cliente
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                ORDER BY co.id_conta DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexao.close()

def atualizar_status_conta(id_conta, novo_status):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("UPDATE conta SET status = %s WHERE id_conta = %s", (novo_status, id_conta))
        conexao.commit()
        return True
    finally:
        conexao.close()

def listar_todos_clientes():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT 
                    u.nome, u.cpf, u.telefone, u.data_nascimento,
                    e.cep, e.lugar, e.numero_casa, e.bairro, e.cidade, e.estado, e.complemento
                FROM cliente cl
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                LEFT JOIN endereco e ON u.id_usuario = e.id_usuario
                ORDER BY u.nome
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexao.close()

def relatorio_resumo_banco():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Total de clientes
            cursor.execute("SELECT COUNT(*) AS total_clientes FROM cliente")
            total_clientes = cursor.fetchone()["total_clientes"]

            # Total de funcionários
            cursor.execute("SELECT COUNT(*) AS total_funcionarios FROM funcionario")
            total_funcionarios = cursor.fetchone()["total_funcionarios"]

            # Total de contas
            cursor.execute("SELECT COUNT(*) AS total_contas FROM conta")
            total_contas = cursor.fetchone()["total_contas"]

            # Soma de todos os saldos
            cursor.execute("SELECT SUM(saldo) AS saldo_total FROM conta")
            saldo_total = cursor.fetchone()["saldo_total"] or 0

            return {
                "total_clientes": total_clientes,
                "total_funcionarios": total_funcionarios,
                "total_contas": total_contas,
                "saldo_total": saldo_total
            }
    finally:
        conexao.close()

def relatorio_ultimas_movimentacoes():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT t.data_hora, t.tipo_transacao, t.valor, t.descricao,
                       co.numero_conta AS conta_origem, cd.numero_conta AS conta_destino
                FROM transacao t
                LEFT JOIN conta co ON t.id_conta_origem = co.id_conta
                LEFT JOIN conta cd ON t.id_conta_destino = cd.id_conta
                ORDER BY t.data_hora DESC
                LIMIT 10
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexao.close()

def relatorio_clientes_negativo_ou_limite():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Clientes com saldo negativo
            sql_negativo = """
                SELECT u.nome, u.cpf, c.numero_conta, c.saldo
                FROM conta c
                JOIN cliente cl ON c.id_cliente = cl.id_cliente
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                WHERE c.saldo < 0
            """
            cursor.execute(sql_negativo)
            negativos = cursor.fetchall()

            # Clientes com limite excedido (saldo < -limite)
            sql_limite = """
                SELECT u.nome, u.cpf, c.numero_conta, c.saldo, cc.limite
                FROM conta c
                JOIN conta_corrente cc ON c.id_conta = cc.id_conta
                JOIN cliente cl ON c.id_cliente = cl.id_cliente
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                WHERE c.tipo_conta = 'CORRENTE' AND c.saldo < -cc.limite
            """
            cursor.execute(sql_limite)
            excedidos = cursor.fetchall()

            return {
                "negativos": negativos,
                "excedidos": excedidos
            }
    finally:
        conexao.close()