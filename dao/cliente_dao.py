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