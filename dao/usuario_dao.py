from util.db import conectar
from datetime import datetime
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
            cursor.execute("""
                SELECT * FROM usuario
                WHERE cpf = %s AND senha_hash = %s
            """, (cpf, senha_hash))
            return cursor.fetchone()
    finally:
        conexao.close()

def gerar_otp_usuario(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("CALL gerar_otp(%s)", (id_usuario,))
            resultado = cursor.fetchone()
        conexao.commit()
        return resultado["novo_otp"] if resultado else None
    finally:
        conexao.close()


def validar_otp(id_usuario, otp_digitado):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT otp_ativo, otp_expiracao
                FROM usuario
                WHERE id_usuario = %s
            """, (id_usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                print("Nenhum usuário encontrado.")
                return False

            otp_valido = resultado["otp_ativo"]
            expiracao = resultado["otp_expiracao"]
            agora = datetime.now()

            return (str(otp_digitado) == str(otp_valido)) and (expiracao > agora)

    finally:
        conexao.close()
