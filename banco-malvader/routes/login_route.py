from flask import Blueprint, render_template, request

login_route = Blueprint('login', __name__)

@login_route.route('/login')
def login():
    return render_template('login.html')

@login_route.route('/autenticar', methods=['POST'])
def autenticar():
    nome = request.form.get("nome", "").strip()
    cpf = request.form.get("cpf", "").strip()
    senha = request.form.get("senha", "").strip()

@login_route.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@login_route.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    cpf = request.form.get("cpf", "").strip()
    senha = request.form.get("senha", "").strip()
    return render_template('login.html')