from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
migrate = Migrate(app,db)
login_manager = LoginManager()



login_manager.init_app(app)
db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)


import routes