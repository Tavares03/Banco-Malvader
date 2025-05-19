from flask import Blueprint, render_template, request, redirect, session
from dao.usuario_dao import cadastrar_usuario, autenticar_usuario
from dao.cliente_dao import cadastrar_cliente
import re

login_route = Blueprint('login', __name__)

@login_route.route('/')
def login():
    return render_template('login.html')

@login_route.route('/autenticar', methods=['POST'])
def autenticar():
    cpf = re.sub(r"\D", "", request.form.get("cpf", "").strip())
    senha = request.form.get("senha", "").strip()

    usuario = autenticar_usuario(cpf, senha)

    if usuario:
        session["usuario_id"] = usuario["id_usuario"]
        session["tipo_usuario"] = usuario["tipo_usuario"]
        session["nome"] = usuario["nome"]

        if usuario["tipo_usuario"] == "CLIENTE":
            return redirect("/cliente")
        else:
            return redirect("/funcionario")
    else:
        return "CPF ou senha inválidos"

@login_route.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@login_route.route('/salvar_cadastro', methods=['POST'])
def salvar_cadastro():
    nome = request.form.get("nome", "").strip()
    cpf = re.sub(r"\D", "", request.form.get("cpf", "").strip())
    nascimento = request.form.get("nascimento", "").strip()
    telefone = request.form.get("telefone", "").strip()
    senha = request.form.get("senha", "").strip()
    confirmar_senha = request.form.get("confirmar_senha", "").strip()
    tipo_usuario = request.form.get("tipo_usuario", "").strip().upper()

    if not senha:
        return "Senha não pode ser vazia"

    if senha != confirmar_senha:
        return "Erro: As senhas não coincidem!"

    id_usuario = cadastrar_usuario(nome, cpf, nascimento, telefone, senha, tipo_usuario)

    if tipo_usuario == "CLIENTE":
        cadastrar_cliente(id_usuario)
    elif tipo_usuario == "FUNCIONARIO":
        pass

    return redirect("/")