from flask import Blueprint, render_template, request

login_route = Blueprint('login', __name__)

@login_route.route('/login')
def login():
    return render_template('login.html')

@login_route.route('/autenticar', methods=['POST'])
def autenticar():
    nome = request.form['nome']
    cpf = request.form['cpf']
    senha = request.form['senha']

@login_route.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@login_route.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    cpf = request.form['cpf']
    senha = request.form['senha']
    return render_template('login.html')