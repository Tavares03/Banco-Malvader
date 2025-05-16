from util.db import conectar
import hashlib

def cadastrar_usuario(nome, cpf, nascimento, telefone, senha, tipo_usuario):
    conexao = conectar()
    try:
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO usuario (nome, cpf, data_nascimento, telefone, tipo_usuario, senha_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nome, cpf, nascimento, telefone, tipo_usuario, senha_hash))
            conexao.commit()
            return cursor.lastrowid
    finally:
        conexao.close()

def autenticar_usuario(cpf, senha):
    conexao = conectar()
    try:
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM usuario WHERE cpf = %s AND senha_hash = %s"
            cursor.execute(sql, (cpf, senha_hash))
            return cursor.fetchone()
    finally:
        conexao.close()