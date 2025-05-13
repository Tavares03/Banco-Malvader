from flask import Blueprint, render_template, request

login_route = Blueprint('login', __name__)

@login_route.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')