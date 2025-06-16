from util.db import conectar

def cadastrar_cliente(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = "INSERT INTO cliente (id_usuario) VALUES (%s)"
            cursor.execute(sql, (id_usuario,))
        conexao.commit()
    finally:
        conexao.close()

def obter_saldo_por_usuario(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT SUM(co.saldo) AS saldo_total
                FROM cliente cl
                JOIN conta co ON cl.id_cliente = co.id_cliente
                WHERE cl.id_usuario = %s
            """
            cursor.execute(sql, (id_usuario,))
            resultado = cursor.fetchone()
            return resultado["saldo_total"] if resultado and resultado["saldo_total"] is not None else 0
    finally:
        conexao.close()

def listar_contas_do_usuario(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT co.id_conta, co.numero_conta, co.saldo, co.tipo_conta
                FROM conta co
                JOIN cliente cl ON co.id_cliente = cl.id_cliente
                WHERE cl.id_usuario = %s AND co.status = 'ATIVA'
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchall()
    finally:
        conexao.close()


def criar_cliente_com_conta(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("CALL criar_cliente_e_conta(%s)", (id_usuario,))
        conexao.commit()
    finally:
        conexao.close()

def obter_limite_e_score(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT co.limite, u.score_credito
                FROM cliente cl
                JOIN conta co ON cl.id_cliente = co.id_cliente
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                WHERE cl.id_usuario = %s
                LIMIT 1
            """
            cursor.execute(sql, (id_usuario,))
            row = cursor.fetchone()
            if row:
                return float(row[0] or 0), int(row[1] or 0)
            else:
                return 0.0, 0
    finally:
        conexao.close()

def obter_dados_completos_cliente(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT 
                    u.nome, u.cpf, u.data_nascimento, u.telefone, u.tipo_usuario,
                    c.id_cliente, c.score_credito,
                    e.cep, e.lugar, e.numero_casa, e.bairro, e.cidade, e.estado, e.complemento
                FROM usuario u
                LEFT JOIN cliente c ON u.id_usuario = c.id_usuario
                LEFT JOIN endereco e ON u.id_usuario = e.id_usuario
                WHERE u.id_usuario = %s
                LIMIT 1
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
    finally:
        conexao.close()