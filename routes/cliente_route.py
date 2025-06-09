from flask import Blueprint, render_template, request, redirect, session
from dao.cliente_dao import obter_saldo_por_usuario, listar_contas_do_usuario

cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
def cliente():
    if "usuario_id" not in session:
        return redirect('/')

    id_usuario = session["usuario_id"]
    saldo_total = obter_saldo_por_usuario(id_usuario)
    contas = listar_contas_do_usuario(id_usuario)

    return render_template("menu_cliente.html", saldo=saldo_total, contas=contas)

@cliente_route.route('/extrato/<int:id_conta>')
def ver_extrato(id_conta):
    return f"Página de extrato para conta {id_conta}"