from flask import Blueprint, render_template, request, redirect, session

cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
def cliente():
    return render_template('menu_cliente.html')