from flask import Flask
from routes.login_route import login_route

app = Flask(__name__)
app.register_blueprint(login_route)

if __name__ == '__main__':
    app.run(debug=True)