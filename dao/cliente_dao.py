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
                WHERE cl.id_usuario = %s
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