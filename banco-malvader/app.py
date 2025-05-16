from flask import Flask
from routes.login_route import login_route
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(login_route)

if __name__ == '__main__':
    app.run(debug=True)