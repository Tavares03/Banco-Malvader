from util.db import conectar

def cadastrar_endereco(id_endereco, cep, lugar, numero_casa, bairro, cidade, estado, complemento):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO endereco (id_endereco, cep, lugar, numero_casa, bairro, cidade, estado, complemento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                id_endereco, cep, lugar, numero_casa, bairro, cidade, estado, complemento
            ))
        conexao.commit()
    finally:
        conexao.close()