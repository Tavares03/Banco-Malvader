from flask import Flask
from routes.login_route import login_route
from routes.cliente_route import cliente_route
from routes.funcionario_route import funcionario_route
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(login_route)
app.register_blueprint(cliente_route, url_prefix='/cliente')
app.register_blueprint(funcionario_route, url_prefix='/funcionario')

if __name__ == '__main__':
    app.run(debug=True)
